from datetime import datetime, timezone
import humanize
from dotenv import load_dotenv
import requests
import requests_cache
import json
import os
import discord

requests_cache.install_cache('advent_cache', backend='sqlite', expire_after=900)
load_dotenv()

TOKEN = os.getenv('TOKEN')
COOKIES = {'session': os.getenv('COOKIE')}
VIEW_URL = 'https://adventofcode.com/2022/leaderboard/private/view/2442051'
BASE_URL = 'https://adventofcode.com/2022/leaderboard/private/view/'
URL = BASE_URL + '2442051.json'


def generate_leaderboard(url):
    leaderboard, created_at = request_leaderboard(url)
    embed = create_embed_from_leaderboard(leaderboard, created_at)
    return embed


def request_leaderboard(url):
    response = requests.get(url, cookies=COOKIES)
    leaderboard_json = json.loads(response.text)
    created_at = response.created_at if response.created_at is not None else datetime.utcnow()
    return leaderboard_json, created_at


def create_embed_from_leaderboard(leaderboard, created_at):
    members = leaderboard['members']
    owner_id = leaderboard['owner_id']
    owner_name = members[str(owner_id)]['name']
    last_updated = humanize.precisedelta(datetime.utcnow() - created_at, format="%0.0f")
    embed = discord.Embed(
        title=f"2022 Advent of Code Leaderboard for {owner_name}",
        url=VIEW_URL,
        description=f"Last updated {last_updated} ago",
        color=discord.Color.green()
    )
    return embed


class AdventofCodeClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$advent'):
            await message.channel.send(embed=generate_leaderboard(URL))


intents = discord.Intents.default()
intents.message_content = True

client = AdventofCodeClient(intents=intents)
client.run(TOKEN)
