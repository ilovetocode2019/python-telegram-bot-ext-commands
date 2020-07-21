from .context import Context

class Command:
    """Represents a command"""
    
    def __init__(self, func, **kwargs):
        self.func = func

        self._data = kwargs
        self.name = kwargs.get("name") or func.__name__
        self.description = kwargs.get("description")
        self.usgae = kwargs.get("usage")
        self.hidden = kwargs.get("hidden") or False
        self.cog = kwargs.get("cog")
        self.bot = kwargs.get("bot")

    def invoke(self, update, context):
        """Runs a comand"""

        ctx = Context(self, update, context)
        return self.func(ctx)

class Cog:
    """Represents an cog loaded into the bot"""

    def __init__(self, name, commands):
        self.name = name
        self.commands = commands

def command(*args, **kwargs):
    """Turns a function into a command"""

    def deco(func):
        name = kwargs.get("name") or func.__name__
        command = Command(func, **kwargs)
        return command
    
    return deco