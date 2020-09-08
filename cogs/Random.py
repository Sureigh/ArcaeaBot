# -*- coding: utf-8 -*-

from pathlib import Path

import gspread_asyncio
from discord.ext import commands
from google.oauth2.service_account import Credentials


class Random(commands.Cog):
    """The main command segment, responsible for randomly choosing a song from a chart."""

    def __init__(self, bot):
        self.bot = bot
        self.pool = bot.pool

    # Creates table if none exists
    async def create_song_table(self):
        async with self.pool.acquire() as con:
            # TODO: Make sure this table creation works, I suppose
            await con.execute("""
                        CREATE TABLE IF NOT EXISTS songs(
                            id SMALLSERIAL PRIMARY KEY,
                            song_name TEXT,
                            pst SMALLINT, prs SMALLINT, ftr SMALLINT, byd SMALLINT, 
                            length VARCHAR(5),
                            bpm NUMERIC, 
                            jacket TEXT
                        )
                    """)

    # Updates table with chart data
    async def update_song_table(self):
        def get_creds():
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            credentials = Credentials.from_service_account_file(
                Path(__file__).parent.joinpath("arcaeabot-99f7b035456b.json"),
                scopes=scopes
            )

            return credentials

        agc = await gspread_asyncio.AsyncioGspreadClientManager(get_creds).authorize()

        sheet = await agc.open("Arcaea Songs")
        worksheet = await sheet.worksheet("Song List ArcBot 2")
        songs = await worksheet.get_all_values()

        # TODO: Make sure all the songs are updated into the database
        async with self.pool.acquire() as con:
            await con.execute()


def setup(bot):
    bot.add_cog(Random(bot))
