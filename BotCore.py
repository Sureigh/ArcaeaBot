#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import discord
from discord.ext import commands

import config

from pathlib import Path
import datetime

def main():
    """This is the main file of ArcaeaBot. Please run the bot by running this file."""

    class Bot(commands.Bot):
        def __init__(self, **kwargs):
            super().__init__(command_prefix=commands.when_mentioned_or('%'), **kwargs)
            # Logging
            logger = logging.getLogger('discord')
            logger.setLevel(logging.INFO)

            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            handler = logging.FileHandler(filename=Path("logs", f"{time}.log"),
                                          encoding='utf-8', mode='w')
            handler.setFormatter(logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: %(message)s'))
            logger.addHandler(handler)

        async def on_ready(self):
            for cog in config.cogs:
                try:
                    self.load_extension(f"cogs.{cog}")
                    print(f"Loaded cog {cog} successfully")
                except Exception as exc:
                    print(f'Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')

            await self.change_presence(activity=discord.Game(f"%help | Online on {len(self.guilds)} servers"))
            print(f'Logged on as {self.user} (ID: {self.user.id})')

    bot = Bot()

    bot.run(config.TOKEN)


if __name__ == "__main__":
    main()
