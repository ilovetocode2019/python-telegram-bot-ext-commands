class NotFound(Exception):
    """Raised when something is not found"""

    pass

class CommandAlreadyExists(Exception):
    """Raised when trying to create a command that already exists"""

    pass

class LoadError(Exception):
    """Raised when the bot cannot load a cog"""

    pass