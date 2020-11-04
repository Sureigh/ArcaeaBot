# -*- coding: utf-8 -*-

import motor.motor_asyncio

from discord.ext import commands


class Random(commands.Cog):
    """The main command segment, responsible for randomly choosing a song from a chart."""

    def __init__(self, bot):
        self.bot = bot
        self.db_client = bot.db_client
        self.gc_client = bot.gc_client

    # Manages the updating (and creation) of the song table whenever needed
    async def manage_song_table(self):
        spreadsheet = await self.gc_client.open("Arcaea Songs")
        worksheet = await spreadsheet.worksheet("Song List ArcBot2")
        songs = await worksheet.get_all_values()

    """@commands.command()
    async def testing(self, ctx):
        await ctx.send(await self.manage_song_table())"""


def setup(bot):
    bot.add_cog(Random(bot))
