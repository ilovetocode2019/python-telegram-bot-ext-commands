def parse_args(content):
    """Gets the command name and arguments from message content"""

    #Split the message
    splited = content.split()
    command_text = splited[0]

    args = splited[1:]

    command_text = command_text[1:]
    command = command_text

    #If the message is in a group, we need to remove the mention from command_text
    if "@" in command_text:
        finished_command_text = ""
        past_mention = False
        for x in command_text[::-1]:
            if past_mention:
                finished_command_text += x
            elif x == "@":
                past_mention = True
        
        command = finished_command_text[::-1]

    return command, args