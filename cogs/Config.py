# -*- coding: utf-8 -*-

import itertools

import gspread_asyncio
import motor.motor_asyncio
from discord.ext import commands
from google.oauth2 import service_account

import config


class Config(commands.Cog):
    """The description for Config goes here."""

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
                return await worksheet.get_all_values()

        bot.songs = await grab_songs(bot, bot.gc_client)

    # Manages the updating (and creation) of the song table whenever needed
    async def manage_song_table(self):
        songs = self.bot.songs

        # Create dictionary of songs
        title = songs.pop(0)
        title[0] = "_id"
        songs = [{k: v for k, v in zip(title, song)} for song in songs]  # Bless dict comprehension tbh

        # Push songs to song collection
        """
        Workflow process:
        - Function will compare each song.
        - If there are differences, the one cached in GSheets will replace the one on DB.
        - If document does not exist, it will be pushed into DB.
        - Returns a list of all results inserted.
        """
        db_songs = await self.db["Songs"].find().to_list(length=None)
        result = []

        # If the db has not been constructed at all/corrupted
        if len(db_songs) == 0:
            result = len(await self.db["Songs"].insert_many(songs).inserted_ids)
        else:
            for document, song in itertools.zip_longest(db_songs, songs, fillvalue={}):
                if document != song:
                    i = song.pop("_id")
                    result.append(await self.db["Songs"].replace_one({"_id": i}, song))

            result = sum([song.modified_count for song in result])

        return result

    # TODO: This is obviously only here for debug purposes. Remove when finished with bot.
    @commands.command()
    async def insert_songs(self, ctx):
        await ctx.send("Please hold, this may take some time...")
        total = await self.manage_song_table()
        await ctx.send(f"Modified {total} songs.")
        await ctx.send("<a:default_dance:583909994504912901>")

    @commands.command()
    async def cleardb(self, ctx):
        await self.db.drop_collection("Songs")
        await ctx.send("<:TohruShrug:361977037306724366>")

    # TODO: Maybe I'll keep this around as a debug command. A debug cog, maybe?
    @commands.command()
    async def song_list_length(self, ctx):
        await ctx.send(f"GSheets currently has {len(self.bot.songs)} songs.")
        cursor = self.db["Songs"].find()
        songs = [doc for doc in await cursor.to_list(length=None)]
        await ctx.send(f"MongoDB currently has {len(songs)} songs.")

    # TODO: Something like this as well. Perhaps send two, or three dicts per message, so as to not
    #  overload the 2000 char limit, in a nice spool, with the requested amount filling the length parameter.
    #  Maybe you'll be smart about writing functions to unroll it all, eh?
    @commands.command()
    async def lemme_see_db(self, ctx):
        cursor = self.db["Songs"].find()
        await ctx.send(str([doc for doc in await cursor.to_list(length=None)])[:2000])


def setup(bot):
    bot.add_cog(Config(bot))
