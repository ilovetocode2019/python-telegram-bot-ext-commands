# Telegram-ext-commands

A commands extension for python-telegram-bot, intended to be similar to discordpy commands extension

## Install

`pip install git+https://github.com/ilovetocode2019/telegram-ext-commands`

## Usage

```python
from telegram.ext import commands

bot = commands.Bot(TOKEN)

@bot.command(name="hi")
def test(context):
    context.send("Hello!")

bot.run()
```

