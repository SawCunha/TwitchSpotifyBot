import random
import string
import time
from twitchio.ext import commands
from utils.errors import *
from utils import DB, Log
from twitch.utils.twitch_utils import target_finder
from configuration.configuration import Configuration


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log: Log = bot.log
        self.db: DB = bot.db
        self.music_controller = bot.music_controller
        self.configuration: Configuration = bot.configuration
        self.channel_name = bot.channel_name
    
    async def cog_check(self, ctx: commands.Context) -> bool:
        if not self.db.is_user_admin(ctx.author.name.lower()):
            raise NotAuthorized('admin')
        return True
