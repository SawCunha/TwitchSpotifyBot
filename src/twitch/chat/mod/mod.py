from twitchio.ext import commands
from utils.errors import *
from utils import Log
from twitch.chat.user_ban import UserBan


class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.configuration = bot.configuration
        self.log: Log = bot.log

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not ctx.author.is_mod and not ctx.author.is_broadcaster:
            raise NotAuthorized('NOT_PERMISSION')
        return True

    @commands.command(name='music-ban')
    async def ban_command(self, ctx: commands.Context):
        request = ctx.message.content.split(' ')[1].lower()

        if request not in UserBan.users:
            UserBan.users.append(request)

        resp = self.configuration.locate.translate('USER_BAN')
        await ctx.reply(resp)
        self.log.resp(resp)

    @commands.command(name='music-unban')
    async def unban_command(self, ctx: commands.Context):
        request = ctx.message.content.split(' ')[1].lower()

        if request in UserBan.users:
            UserBan.users.remove(request)

        resp = self.configuration.locate.translate('USER_UNBAN')
        await ctx.reply(resp)
        self.log.resp(resp)
