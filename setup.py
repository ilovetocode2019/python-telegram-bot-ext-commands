import setuptools
import re

version = ""
with open("telegram/ext/commands/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setuptools.setup(
    name="telegram-ext-commands",
    description="A commands extension for python-telegram-bot, intended to be similar to discord.py commands extension",
    author="Ilovetocode",
    url="https://github.com/ilovetocode2019/telegram-ext-commands",
    version=version,
    packages=["telegram.ext.commands"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)