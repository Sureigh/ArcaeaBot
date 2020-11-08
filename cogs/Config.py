# -*- coding: utf-8 -*-

import gspread_asyncio
import motor.motor_asyncio
import discord
from discord.ext import commands
from google.oauth2 import service_account

import config


class Config(commands.Cog):
    """A debug cog used to configure, manage and setup parts of ArcaeaBot."""

    def __init__(self, bot):
        # MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(config.mongodb)
        bot.db = client["ArcaeaBot"]

        # Google Cloud (and related products)
        credentials = service_account.Credentials.from_service_account_file(config.gc_json)
        scoped_credentials = credentials.with_scopes(config.gc_scopes)
        bot.gc_client = gspread_asyncio.AsyncioGspreadClientManager(lambda: scoped_credentials)
        bot.songs = None

        bot.loop.create_task(self.async_init())

        self.bot = bot
        self.db = bot.db
        self.gc_client = bot.gc_client

    async def async_init(self):
        bot = self.bot
        bot.gc_client = await bot.gc_client.authorize()

        # GSheet data grabber - grabs data when requested, otherwise ignores and uses cached data
        async def grab_songs(client, gc_client):
            # TODO: Modify this condition in the future - if there are new song entries on the wiki, then proceed
            if client.songs is None:
                spreadsheet = await gc_client.open("Arcaea Songs")
                # TODO: When we eventually remove the first manually-made sheet, change reference to sheet below
                worksheet = await spreadsheet.worksheet("Song List ArcBot2")

                # Organize songs
                songs = await worksheet.get_all_values()
                title = songs.pop(0)
                title[0] = "_id"

                return [{k: v for k, v in zip(title, song)} for song in songs]  # Bless dict comprehension tbh

        bot.songs = await grab_songs(bot, bot.gc_client)

    @commands.command(aliases=["dropdb"])
    async def cleardb(self, ctx):
        await self.db.drop_collection("Songs")
        await ctx.send("<:TohruShrug:361977037306724366>")

    @commands.command(aliases=["check_db", "checkdb", "songlist", "song_list"])
    async def song_list_length(self, ctx):
        # TODO: Once we learn webscraping, compare it to the wiki song list instead.
        # TODO: Call a (sub)command that will update the wiki list to the cloud sheet.
        embed = discord.Embed(
            description=f"GSheets currently has {len(self.bot.songs)} songs."
        ).set_author(name="Checking bot songs sync...")

        msg = await ctx.send(embed=embed)

        embed.description = (f"{embed.description}\n"
                             f"[Placeholder] currently has [Placeholder] songs.")

        # TODO: Change this condition.
        if len(self.bot.songs) == len("[Placeholder]"):
            embed.set_author(name="Bot songs synced!")
            embed.color = discord.Color.green()
        else:
            embed.set_author(name="Bot songs not synced!")
            embed.color = discord.Color.red()

        await msg.edit(embed=embed)

    # TODO: Something like this as well. Perhaps send two, or three dicts per message, so as to not
    #  overload the 2000 char limit, in a nice spool, with the requested amount filling the length parameter.
    #  Maybe you'll be smart about writing functions to unroll it all, eh?
    @commands.command()
    async def lemme_see_db(self, ctx):
        cursor = self.db["Songs"].find()
        await ctx.send(str([doc for doc in await cursor.to_list(length=None)])[:2000])


def setup(bot):
    bot.add_cog(Config(bot))
