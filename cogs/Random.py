# -*- coding: utf-8 -*-

from discord.ext import commands


class Random(commands.Cog):
    """The main command segment, responsible for randomly choosing a song from a chart."""

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Random(bot))
