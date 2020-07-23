from telegram.ext import Updater, CommandHandler
import importlib
import inspect

from .core import Command, Cog
from .errors import NotFound, CommandAlreadyExists, LoadError
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

        self.extensions = {}

        self.help_command = help_command
        self.add_command(help_command, name="help", description="Help for the bot", usage="<command|category>")

    def get_context(self, message):
        command, args = parse_args(message.text)

        command = self.commands_dict[str(command)]
        kwargs = {"command":command, "args":args}
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
            
            handler = CommandHandler(name, command.invoke)
            self.dispatcher.add_handler(handler)

            self._handlers[name] = handler
            self.commands_dict[name] = command

            return command
        
        return deco

    def add_command(self, func, **kwargs):
        """Adds a function as a command"""

        name = kwargs.get("name") or func.__name__
        kwargs["bot"] = self

        if name in self.commands_dict:
            raise CommandAlreadyExists("A command with that name already exists")

        command = Command(func, **kwargs)

        handler = CommandHandler(name, command.invoke)
        self.dispatcher.add_handler(handler)

        self._handlers[name] = handler
        self.commands_dict[name] = command

        return command

    def add_command(self, func, **kwargs):
        """Adds a function as a command"""

        name = kwargs.get("name") or func.__name__
        kwargs["bot"] = self

        if name in self.commands_dict:
            raise CommandAlreadyExists("A command with that name already exists")

        command = Command(func, **kwargs)

        handler = CommandHandler(name, command.invoke)
        self.dispatcher.add_handler(handler)

        self._handlers[name] = handler
        self.commands_dict[name] = command

    def remove_command(self, name):
        """Removes a command"""

        if name not in [x.name for x in self.commands]:
            raise NotFound("No command by that name")

        command = self.commands_dict[name]

        if command.cog:
            command.cog.commands.remove(command)

        self.dispatcher.remove_handler(self._handlers[name])
        self._handlers.pop(name)
        self.commands_dict.pop(name)

    @property
    def commands(self):
        """A list of commands in the bot"""

        return list(self.commands_dict.values())

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

        pass

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

                handler = CommandHandler(command.name, command.invoke)
                self.dispatcher.add_handler(handler)

                self._handlers[command.name] = handler
                self.commands_dict[command.name] = command
                
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