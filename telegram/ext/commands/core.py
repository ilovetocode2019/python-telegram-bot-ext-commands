import re
import inspect

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
        self.aliases = kwargs.get("aliases") or []
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

    def __call__(self, update, context):
        """Runs the command with checks"""

        ctx = self.bot.get_context(update.effective_message)

        for check in self.checks:
            if not check(ctx):
                return

        if self.cog:
            if not self.cog.cog_check(ctx):
                return

        other_args = []
        if self.cog:
            other_args.append(self.cog)
        other_args.append(ctx)

        return self.func(*other_args, *ctx.args, **ctx.kwargs)

    def invoke(self, ctx):
        """Invokes the command with given context"""

        for check in self.checks:
            if not check(ctx):
                return

        if self.cog:
            if not self.cog.cog_check(ctx):
                return

        other_args = []
        if self.cog:
            other_args.append(self.cog)
        other_args.append(ctx)

        return self.func(*other_args, *ctx.args, **ctx.kwargs)

class Cog:
    """The class to subclass a cog from"""

    pass

def command(*args, **kwargs):
    """Turns a function into a command"""

    def deco(func):
        kwargs["name"] = kwargs.get("name") or func.__name__
        command = Command(func, **kwargs)
        return command
    
    return deco