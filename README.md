# telegram-ext-commands

I am no longer maintaining this. I just wanted a commands framework like discord-ext-commands for writing my bots. See [telegram.py](https://github.com/ilovetocode2019/telegram-ext-commands) instead.

<hr>

A commands extension for python-telegram-bot, intended to be similar to the discord.py commands extension.

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

