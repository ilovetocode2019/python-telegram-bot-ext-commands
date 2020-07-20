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

    def invoke(self, update, context):
        """Runs a a comand"""

        ctx = Context(self, update, context)
        return self.func(ctx)