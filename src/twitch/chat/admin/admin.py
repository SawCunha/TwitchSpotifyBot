import random
import string
import time
from twitchio.ext import commands
from utils.errors import *
from utils import Log
from configuration.configuration import Configuration


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log: Log = bot.log
        self.music_controller = bot.music_controller
        self.configuration: Configuration = bot.configuration
        self.channel_name = bot.channel_name

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not ctx.author.is_broadcaster:
            raise NotAuthorized('NOT_PERMISSION')
        return True

    @commands.command(name='sp-reload')
    async def reload_cogs_command(self, ctx):
        user = ctx.author.name.lower()
        request = ctx.message.content.strip(str(ctx.prefix + ctx.command.name))
        self.log.req(user, request, ctx.command.name)

        self.log.info('Reloading cogs')

        self.reload_cogs()

        await ctx.send('All cogs reloaded')