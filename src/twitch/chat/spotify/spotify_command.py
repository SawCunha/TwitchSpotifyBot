from twitchio.ext import commands
from utils import Log
from utils.errors import *
from twitch.utils.twitch_utils import check_permission
from configuration.configuration import Configuration
from twitch.chat.user_ban import UserBan


class SpotifyCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.log: Log = bot.log
        self.music_controller = bot.music_controller
        self.configuration: Configuration = bot.configuration

    async def cog_check(self, ctx: commands.Context) -> bool:
        user = ctx.author.name.lower()
        channel: str = self.configuration.twitch.channel

        if not await check_permission(ctx.author, self.configuration.bot.permission.name, channel):
            raise NotAuthorized('NOT_PERMISSION')

        if user in UserBan.users:
            raise UserBanned

        return True

    @commands.cooldown(3, 20, commands.Bucket.channel)
    @commands.command(name='music')
    async def music(self, ctx: commands.Context):
        request = ctx.message.content.strip(str(ctx.prefix + ctx.command.name))

        track, artist = self.music_controller.add_to_queue(request)

        if track is None:
            resp = self.configuration.locate.translate('NOT_FOUND_MUSIC_SPOTIFY')
            await ctx.reply(resp)
            self.log.resp(resp)
            return False
        else:
            resp = self.configuration.locate.translate('MUSIC_ADD_SPOTIFY', music=track, artist=artist)
            await ctx.reply(resp)
            self.log.resp(resp)
            return True

    @commands.command(name='music-info')
    async def music_info(self, ctx: commands.Context):
        track, artist = self.music_controller.current_music()

        resp = self.configuration.locate.translate('MUSIC_INFO_SPOTIFY', music=track, artist=artist)

        await ctx.reply(resp)
        self.log.resp(resp)
        return True

    @commands.command(name='music-help')
    async def music_help(self, ctx: commands.Context):
        resp = self.configuration.locate.translate('LINK_COMMAND')
        await ctx.reply(resp)
        self.log.resp(resp)
        return True