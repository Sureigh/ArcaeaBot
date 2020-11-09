# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import aiohttp
from bs4 import BeautifulSoup

class Wiki(commands.Cog):
    """The cog responsible for organizing all data from the Arcaea wiki."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def grab_wiki(self, ctx):
        # First, create a client to connect and request data asynchronously
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://arcaea.fandom.com/wiki/Songs_by_Date') as r:
                soup = BeautifulSoup(await r.content.read(), "html.parser")

        # This should return two tables - the main table with every chart,
        # and small sub table with April Fools' charts
        # TODO: Finish this lmao; We may have to do manual coding
        for result in soup.find_all("table"):
            title = [str(title.text.strip()) for title in result.tr.find_all("th")]
            for chart in [str(chart.find_all("td")) for chart in result.tbody.find_all("tr")]:
                [column.text for column in chart]

        await ctx.send("Webpage results scraped and saved.")

def setup(bot):
    bot.add_cog(Wiki(bot))
