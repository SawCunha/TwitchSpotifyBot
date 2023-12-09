from twitchio.ext import commands
from utils.errors import *
from utils import Timer, DB, Log
from twitch.utils.twitch_utils import time_finder, target_finder
from configuration.configuration import Configuration


class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log: Log = bot.log
        self.db: DB = bot.db
        self.music_controller = bot.music_controller
        self.configuration: Configuration = bot.configuration
        self.units = bot.units
        self.channel_name = bot.channel_name
        self.units_full = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not self.db.is_user_privileged(ctx.author.name.lower()) or not self.db.is_user_admin(
                ctx.author.name.lower()):
            raise NotAuthorized('mod or admin')
        return True

    @commands.command(name='music-ban')
    async def ban_command(self, ctx: commands.Context):
        user = ctx.author.name.lower()
        request = ctx.message.content.strip(str(ctx.prefix + ctx.command.name))

        target = target_finder(self.db, request)

        if self.ban(user, target):
            resp = f'@{target} has been banned!'
            await ctx.reply(resp)
            self.log.resp(resp)

    def ban(self, user, target):
        # if the user is an admin ban the target even if they're a mod
        if self.db.is_user_admin(user):
            self.db.ban_user(target)
            return True

        # if the user is a mod and the target isn't a mod or admin then ban the target
        elif self.db.is_user_mod(user) and not self.db.is_user_privileged(target):
            self.db.ban_user(target)
            return True

        else:
            raise NotAuthorized('mod/admin')

    @commands.command(name='music-unban')
    async def unban_command(self, ctx: commands.Context):
        user = ctx.author.name.lower()
        request = ctx.message.content.strip(str(ctx.prefix + ctx.command.name))

        target = target_finder(self.db, request)

        if self.unban(user, target):
            resp = f'@{target} has been unbanned!'
            await ctx.reply(resp)
            self.log.resp(resp)

    def unban(self, user, target):
        # if user is a mod or admin and target is banned then unban them
        if self.db.is_user_privileged(user):
            self.db.unban_user(target)
            return True
        else:
            raise NotAuthorized('mod/admin')