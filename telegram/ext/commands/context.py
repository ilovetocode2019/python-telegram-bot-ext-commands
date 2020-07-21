class Context:
    """Context in a command"""

    def __init__(self, command, **kwargs):
        self.command = command
        self.bot = command.bot

        self.message = kwargs.get("message")
        self.chat = kwargs.get("chat")
        self.author = kwargs.get("author")
        self.args = kwargs.get("args")

    def send(self, content):
        """Shortcut for bot.send_message"""

        self.bot.updater.bot.send_message(chat_id=self.chat.id, text=content)