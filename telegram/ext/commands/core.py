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

        if self.cog:
            return self.func(self.cog, ctx)
        else:
            return self.func(ctx)

class Cog:
    """The class to subclass a cog from"""

    pass

def command(*args, **kwargs):
    """Turns a function into a command"""

    def deco(func):
        command = Command(func, **kwargs)
        return command
    
    return deco