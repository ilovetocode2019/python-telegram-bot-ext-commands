import telegram
from telegram.ext import Updater, CommandHandler
import importlib
import inspect
import traceback
import sys
import types

from .core import Command, Cog
from .errors import NotFound, CommandAlreadyExists, LoadError, AlreadyExists
from .context import Context
from .help import help_command
from .utils import parse_args

class Bot:
    """Represent a telegram bot"""

    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.commands_dict = {}
        self._handlers = {}
        self.cogs_dict = {}
        self._listeners = {}

        self.extensions = {}

        self.help_command = help_command
        self.add_command(help_command, name="help", description="Help for the bot", usage="[command|category]", aliases=["start"])

    def get_context(self, message):
        command, given_args = parse_args(message.text)
        command = self.get_command(command)

        kwargs = {"command": command}
        kwargs["args"] = []
        kwargs["kwargs"] = {}
        kwargs["message"] = message
        kwargs["chat"] = message.chat
        kwargs["author"] = message.from_user

        return Context(**kwargs)

    def command(self, *args, **kwargs):
        """Turns a function into a command"""

        def deco(func):
            name = kwargs.get("name") or func.__name__
            kwargs["bot"] = self

            if name in self.commands_dict:
                raise CommandAlreadyExists("A command with that name already exists")

            command = Command(func, **kwargs)
            command.checks = getattr(func, "_command_checks", [])
            
            handler = CommandHandler(name, command.__call__)
            self.dispatcher.add_handler(handler)

            self._handlers[name] = handler
            self.commands_dict[name] = command


            for alias in command.aliases:
                handler = CommandHandler(alias, command.__call__)
                self.dispatcher.add_handler(handler)
                self.commands_dict[alias] = command

            return command
        
        return deco

    def add_command(self, func, **kwargs):
        """Adds a function as a command"""

        name = kwargs.get("name") or func.__name__
        kwargs["bot"] = self

        if name in self.commands_dict:
            raise CommandAlreadyExists("A command with that name already exists")

        command = Command(func, **kwargs)
        command.checks = getattr(func, "_command_checks", [])

        handler = CommandHandler(name, command.__call__)
        self.dispatcher.add_handler(handler)
        self._handlers[name] = handler


        for alias in command.aliases:
            handler = CommandHandler(alias, command.__call__)
            self.dispatcher.add_handler(handler)
            self._handlers[alias] = handler

        self.commands_dict[name] = command
        return command

    def remove_command(self, name):
        """Removes a command"""

        if not self.get_command(name):
            raise NotFound("No command by that name")

        command = self.get_command(name)

        if command.cog:
            command.cog.commands.remove(command)

        for alias in command.aliases:
            self.dispatcher.remove_handler(self._handlers[alias])
            self._handlers.pop(alias)

        self.dispatcher.remove_handler(self._handlers[command.name])
        self._handlers.pop(command.name)
        self.commands_dict.pop(command.name)

    def get_command(self, name):
        if name in self.commands_dict:
            return self.commands_dict[name]
        
        for command in self.commands:
            if name in command.aliases:
                return command

    @property
    def commands(self):
        """A list of commands in the bot"""

        return list(self.commands_dict.values())

    def event(self, func):
        """Turns a function into the listener for a event"""

        setattr(self, func.__name__, func)
        return func

    def add_listener(self, func, name=None):
        """Adds a function as a listener"""

        name = name or func.__name__

        if name in self._listeners:
            self._listeners[name].append(func)
        else:
            self._listeners[name] = [func]

    def _dispatch(self, event, *args):
        """Dispatches an event"""

        event = f"on_{event}"
        if event in self._listeners:
            listeners = self._listeners[event]
        else:
            listeners = []

        try:
            listeners.append(getattr(self, event))
        except AttributeError:
            pass

        for listener in listeners:
            listener(*args)

    def on_command_error(self, ctx, error):
        """Default command error handler"""

        if "on_command_error" in self._listeners:
            return

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def load_extension(self, location):
        """Loads an extension into the bot"""

        cog = importlib.import_module(location)

        if not hasattr(cog, "setup"):
            raise LoadError("No setup function")

        cog.setup(self)
        
    def unload_extension(self, location):
        """Unloads an extension from the bot"""

        cog_name = self.extensions.get(location)
        if not cog_name:
            raise NotFound("Extension is not loaded")

        self.remove_cog(cog_name)

        self.extensions.pop(location)

    def reload_extension(self, location):
        """Reloads an extension in the bot"""

        if location not in self.extensions:
            raise NotFound("Extension not loaded")

        lib = sys.modules[location]
        importlib.reload(lib)
        self.remove_cog(self.extensions[location])
        
        sys.modules[location].setup(self)

    def add_cog(self, cog):
        """Adds a cog to the bot"""
        
        if not issubclass(cog.__class__, Cog):
            raise LoadError("Cogs must be a subclass of Cog")

        cog_commands = []
        for command in dir(cog):
            command = getattr(cog, command)
            if isinstance(command, Command):
                cog_commands.append(command)
                command.bot = self
                command.cog = cog

                if command.name in self.commands_dict:
                    raise CommandAlreadyExists("A command with that name already exists")

                handler = CommandHandler(command.name, command.__call__)
                self.dispatcher.add_handler(handler)
                self._handlers[command.name] = handler

                for alias in command.aliases:
                    handler = CommandHandler(alias, command.__call__)
                    self.dispatcher.add_handler(handler)
                    self._handlers[alias] = handler

                self.commands_dict[command.name] = command

            elif isinstance(command, types.MethodType):
                try:
                    listener_name = command._cog_listener
                    self.add_listener(command, listener_name)
                except AttributeError:
                    pass
                
        if hasattr(cog, "cog_check"):
            if not inspect.ismethod(cog.cog_check):
                raise LoadError("Cog check is not a function")

            cog_check = cog.cog_check
        else:
            def cog_check(context):
                return True
            cog.cog_check = cog_check

        cog.name = cog.__class__.__name__
        cog.commands = cog_commands
        self.cogs_dict[cog.name] = cog

        if str(cog.__module__) != "__main__":
            self.extensions[cog.__module__] = cog.name

    def remove_cog(self, cog):
        """Removes and cog from the bot"""

        if cog not in self.cogs_dict:
            raise NotFound("Cog is not loaded")

        for command in self.cogs_dict[cog].commands:
            try:
                self.remove_command(command.name)
            except NotFound:
                pass

        self.cogs_dict.pop(cog)

    @property
    def cogs(self):
        return list(self.cogs_dict.values())

    def run(self, idle=True):
        """Runs the bot"""

        self.updater.start_polling()

        if idle:
            self.updater.idle()