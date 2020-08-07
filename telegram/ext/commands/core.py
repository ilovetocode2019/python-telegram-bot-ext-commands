import re
import inspect
import telegram

from .context import Context
from .errors import NotFound, ArgumentError, CheckFailure
from .utils import parse_args

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

    def _parse_args(self, ctx):
        command, given_args = parse_args(ctx.message.text)

        if ctx.command:
            takes_args = [x[1] for x in list(inspect.signature(ctx.command.func).parameters.items())]
            if ctx.command.cog:
                takes_args.pop(0)
            takes_args.pop(0)

            for counter, argument in enumerate(takes_args):
                try:
                    if argument.kind != inspect._ParameterKind.KEYWORD_ONLY:
                        give = given_args[0]

                        converter = argument.annotation
                        if converter != inspect._empty:
                            try:
                                if converter == telegram.ChatMember:
                                    give = ctx.bot.updater.bot.get_chat_member(chat_id=message.chat.id, user_id=give)
                                elif converter == telegram.Chat:
                                    give = ctx.bot.updater.bot.get_chat(chat_id=give)
                                else:
                                    give = argument.annotation(give)
                            except:
                                raise ArgumentError(f"Failed to convert '{give}' to '{converter.__name__}'")
    
                        ctx.args.append(give)

                        given_args.pop(0)
                    else:
                        give = " ".join(given_args)
                        if give == "":
                            raise IndexError()

                        converter = argument.annotation
                        if converter != inspect._empty:
                            try:
                                if converter == telegram.ChatMember:
                                    give = ctx.bot.updater.bot.get_chat_member(chat_id=message.chat.id, user_id=give)
                                elif converter == telegram.Chat:
                                    give = ctx.bot.updater.bot.get_chat(chat_id=give)
                                else:
                                    give = argument.annotation(give)
                            except:
                                raise ArgumentError(f"Failed to convert '{give}' to '{converter.__name__}'")
                        

                        ctx.kwargs[argument.name] = give
                        
                except IndexError:
                    if argument.default == inspect._empty:
                        raise ArgumentError(f"'{argument.name}' is a required argument that is missing")
                    if argument.kind != inspect._ParameterKind.KEYWORD_ONLY:
                        ctx.args.append(argument.default)

    def _dispatch_error(self, ctx, error):
        """Dispatch an error"""

        ctx.bot._dispatch("command_error", ctx, error)

    def __call__(self, update, context):
        """Runs the command with checks"""

        ctx = self.bot.get_context(update.effective_message)

        try:
            self.invoke(ctx)
        except Exception as e:
            self._dispatch_error(ctx, e)

    def invoke(self, ctx):
        """Invokes the command with given context"""

        for check in self.checks:
            if not check(ctx):
                raise CheckFailure("A check for this command has failed")

        if self.cog:
            if not self.cog.cog_check(ctx):
                raise CheckFailure("A check for this command has failed")

        other_args = []
        if self.cog:
            other_args.append(self.cog)
        other_args.append(ctx)

        self._parse_args(ctx)
        return self.func(*other_args, *ctx.args, **ctx.kwargs)


class Cog:
    """The class to subclass a cog from"""

    @classmethod
    def listener(cls, name=None):

        def deco(func):
            func._cog_listener = name or func.__name__
            return func

        return deco

def command(*args, **kwargs):
    """Turns a function into a command"""

    def deco(func):
        kwargs["name"] = kwargs.get("name") or func.__name__
        command = Command(func, **kwargs)
        command.checks = getattr(func, "_command_checks", [])
        return command
    
    return deco

def error_handler(func):
    """Makes a function in a cog an error handler"""

    func._is_error_handler = True
    return func

def check(check_function):

    def deco(func):
        if isinstance(func, Command):
            func.add_check(check_function)
        else:
            if not getattr(func, "_command_checks", None):
                func._command_checks = [check_function]
            else:
                func._command_checks.append(check_function)
        return func

        return

    return deco