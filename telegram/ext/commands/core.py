import re

from .context import Context
from .errors import NotFound

class Command:
    """Represents a command"""
    
    def __init__(self, func, **kwargs):
        self.func = func

        self._data = kwargs
        self.name = kwargs.get("name") or func.__name__
        self.description = kwargs.get("description")
        self.usage = kwargs.get("usage")
        self.hidden = kwargs.get("hidden") or False
        self.parent = kwargs.get("parent")
        self.cog = kwargs.get("cog")
        self.bot = kwargs.get("bot")
        self.checks = []
    
    def add_check(self, func):
        self.checks.append(func)
    
    def remove_check(self, func):
        if func not in self.checks:
            raise NotFound("That function is not yet a check")
        self.checks.remove(func)

    def invoke(self, update, context):
        """Runs a command with checks"""

        ctx = self.bot.get_context(update.effective_message)

        for check in self.checks:
            if not check(ctx):
                return

        if self.cog:
            if not self.cog.cog_check(ctx):
                return

        return self.func(ctx)

class Group:
    """Basicly the same as as the Command class except you can create subcommands"""

    def __init__(self, func, **kwargs):
        self.func = func

        self._data = kwargs
        self.name = kwargs.get("name") or func.__name__
        self.description = kwargs.get("description")
        self.usage = kwargs.get("usage")
        self.hidden = kwargs.get("hidden") or False
        self.cog = kwargs.get("cog")
        self.bot = kwargs.get("bot")
        self.checks = []
        self.subcommands = []
    
    def add_check(self, func):
        self.checks.append(func)
    
    def remove_check(self, func):
        if func not in self.checks:
            raise NotFound("That function is not yet a check")
        self.checks.remove(func)

    def command(self, *args, **kwargs):
        """Creates a subcommand from the main command"""

        def deco(func):
            kwargs["bot"] = self.bot
            kwargs["parent"] = self
            command = Command(func, **kwargs)
            self.subcommands.append(command)
            return command

        return deco

    def invoke(self, update, context):
        """Runs a command with checks"""

        ctx = self.bot.get_context(update.effective_message)

        for check in self.checks:
            if not check(ctx):
                return

        if self.cog:
            if not self.cog.cog_check(ctx):
                return
        
        if len(context.args) != 0:
            for subcommand in self.subcommands:
                if subcommand.name == context.args[0]:
                    old = update.effective_message.text
                    span = re.search(self.name, old).span()
                    update.effective_message.content = old[:span[0]] + old[span[1]:]
                    subcommand.invoke(update, context)
                    return

        return self.func(ctx)
    
class Cog:
    """Represents an cog loaded into the bot"""

    def __init__(self, name, commands, check):
        self.name = name
        self.commands = commands
        
def command(*args, **kwargs):
    """Turns a function into a command"""

    def deco(func):
        command = Command(func, **kwargs)
        return command
    
    return deco

def group(*args, **kwargs):
    """Turns a function into a command group"""

    def deco(func):
        group = Group(func, **kwargs)
        return group
    
    return deco