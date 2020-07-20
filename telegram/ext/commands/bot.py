from telegram.ext import Updater, CommandHandler

from .core import Command
from .errors import CommandNotFound, CommandAlreadyExists

class Bot:
    """Represent a telegram bot"""

    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.commands_dict = {}
        self._handlers = {}

    def command(self, *args, **kwargs):
        """Turns a function into a command"""

        def deco(func):
            name = kwargs.get("name") or func.__name__
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
        if name in self.commands_dict:
            raise CommandAlreadyExists("A command with that name already exists")

        command = Command(func, **kwargs)

        handler = CommandHandler(name, command.invoke)
        self.dispatcher.add_handler(handler)

        self._handlers[name] = handler
        self.commands_dict[name] = command

        return command
    def remove_command(self, name):
        """Removes a command"""

        if name not in self.commands:
            raise CommandNotFound("No command by that name")
            return

        self.dispatcher.remove_handler(self._handlers[name])
        self._handlers.pop(name)
        self.commands_dict.pop(name)

    @property
    def commands(self):
        """A list of commands in the bot"""

        return list(self.commands_dict.keys())

    def run(self, idle=True):
        """Runs the bot"""

        self.updater.start_polling()

        if idle:
            self.updater.idle()