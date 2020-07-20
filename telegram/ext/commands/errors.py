class CommandNotFound(Exception):
    """Raised when a command is not found"""

    pass

class CommandAlreadyExists(Exception):
    """Raised when trying to create a command that already exists"""

    pass