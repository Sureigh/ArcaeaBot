# -*- coding: utf-8 -*-

from pymongo.errors import InvalidOperation

from discord.ext import commands


class Random(commands.Cog):
    """The main command segment, responsible for randomly choosing a song from a chart."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.gc_client = bot.gc_client

    # Manages the updating (and creation) of the song table whenever needed
    async def manage_song_table(self):
        songs = self.bot.songs

        # Create dictionary of songs
        title = songs.pop(0)
        title[0] = "_id"
        songs = [{k: v for k, v in zip(title, song)} for song in songs]  # Bless dict comprehension tbh

        # Push songs to song collection
        result = await self.db["Songs"].insert_many(songs)
        return songs, result
        # TODO: Push this list of dicts to a new MongoDB collection - look into Motor async

    # TODO: This is obviously only here for debug purposes. Remove when finished with bot.
    @commands.command()
    async def insert_songs(self, ctx):
        songs, songs_inserted = await self.manage_song_table()
        try:
            await ctx.send(len(songs_inserted.inserted_ids))
        except InvalidOperation:
            await ctx.send("Songs failed to insert. Fuck you.")
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
    bot.add_cog(Random(bot))
