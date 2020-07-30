def help_command(ctx, command_name=None):
    if not command_name:
        msg = ""
        for cog in ctx.bot.cogs:
            msg += "\n\n"
            msg += cog.name + "\n"
            msg += "\n".join([f"/{command.name} - {command.description or 'No description'}" for command in cog.commands if not command.hidden])
        
        msg += "\n\nNo category\n"
        msg += "\n".join([f"/{command.name}" for command in ctx.bot.commands if not command.cog])

        ctx.send(msg)

    else:
        command = ctx.bot.commands_dict.get(command_name)
        if command and not command.hidden:
            msg = f"/{command.name} {command.usage or ''} - {command.description or 'No description'}\n"
            if len(command.aliases) != 0:
                msg += f"\nAliases: {', '.join(command.aliases)}"
            ctx.send(msg)

            return

        cog = ctx.bot.cogs_dict.get(command_name)
        if cog:
            msg = cog.name + "\n"
            msg += "\n" + "\n".join([f"/{command.name} - {command.description or 'No description'}" for command in cog.commands])
            ctx.send(msg)
            return
        
        ctx.send("❌ No cog or command by that name")
        