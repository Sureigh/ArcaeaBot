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
        # Acquire worksheet instance from cloud
        spreadsheet = await self.gc_client.open("Arcaea Songs")
        # TODO: When we eventually remove the first manually-made sheet, change the reference to said sheet below
        worksheet = await spreadsheet.worksheet("Song List ArcBot2")
        songs = await worksheet.get_all_values()

        # Create dictionary of songs
        title = songs.pop(0)
        songs = [{k: v for k, v in zip(title, song)} for song in songs]  # Bless dict comprehension tbh
        # TODO: Push this list of dicts to a new MongoDB collection - look into Motor async

    # TODO: This is obviously only here for debug purposes. Remove when finished with bot.
    @commands.command()
    async def testing(self, ctx):
        await ctx.send(await self.manage_song_table())


def setup(bot):
    bot.add_cog(Random(bot))
