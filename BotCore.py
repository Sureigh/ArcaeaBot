#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

import config
import asyncpg

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('%'), **kwargs)
        self.loop.create_task(self.async_init())

    async def async_init(self):
        try:
            self.pool = await asyncpg.connect(config.pool)
        except:
            self.pool = "peepee poopoo"

    async def on_ready(self):
        # Load cogs
        for cog in config.cogs:
            try:
                self.load_extension(f"cogs.{cog}")
            except Exception as exc:
                print(f'Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')

        # Set bot status
        await self.change_presence(activity=discord.Game(f"%help | Online on {len(self.guilds)} servers"))
        print(f'Logged on as {self.user} (ID: {self.user.id})')


bot = Bot()

bot.run(config.TOKEN)
