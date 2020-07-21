class Context:
    """Context in a command"""

    def __init__(self, command, update, context):
        self.command = command

        self.update = update
        self.context = context

        self.message = update.effective_message
        self.chat = update.effective_chat
        self.author = update.effective_user
        self.args = context.args

        self.bot = command.bot

    def send(self, content):
        """Shortcut for bot.send_message"""

        self.bot.updater.bot.send_message(chat_id=self.chat.id, text=content)