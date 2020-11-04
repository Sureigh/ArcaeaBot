#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
import motor.motor_asyncio
import gspread_asyncio
from discord.ext import commands
from google.oauth2 import service_account


import config

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('%'), **kwargs)
        self.loop.create_task(self.async_init())


        # MongoDB
        self.db_client = motor.motor_asyncio.AsyncIOMotorClient(config.mongodb)

        # Google Cloud (and related products)
        credentials = service_account.Credentials.from_service_account_file(config.gc_json)
        scoped_credentials = credentials.with_scopes(config.gc_scopes)
        self.gc_client = gspread_asyncio.AsyncioGspreadClientManager(lambda: scoped_credentials)

    async def async_init(self):
        self.gc_client = await self.gc_client.authorize()

    async def on_ready(self):
        # Load cogs
        for cog in config.cogs:
            try:
                self.load_extension(f"cogs.{cog}")
            except Exception as exc:
                print(f'Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')

        await self.change_presence(activity=discord.Game(f"%help | Online on {len(self.guilds)} servers"))
        print(f'Logged on as {self.user} (ID: {self.user.id})')


bot = Bot()

bot.run(config.TOKEN)
