from twitchio.ext import commands
from utils import DB, Log
from utils.errors import *
from twitch.utils.twitch_utils import check_permission
from configuration.configuration import Configuration


class SpotifyCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.log: Log = bot.log
        self.db: DB = bot.db
        self.music_controller = bot.music_controller
        self.configuration: Configuration = bot.configuration

    @commands.cooldown(1, 10, commands.Bucket.channel)
    @commands.command(name='music')
    async def music(self, ctx: commands.Context):
        user = ctx.author.name.lower()
        if self.db.is_user_banned(user):
            raise UserBanned

        request = ctx.message.content.strip(str(ctx.prefix + ctx.command.name))

        channel: str = self.configuration.twitch.channel
        is_user_privileged: bool = self.db.is_user_privileged(user)

        await check_permission(ctx.author, self.configuration.bot.permission.name, channel, is_user_privileged)

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
            self.db.add_requests(user)
            return True

    @commands.command(name='music-info')
    async def music_info(self, ctx: commands.Context):
        user = ctx.author.name.lower()
        if self.db.is_user_banned(user):
            raise UserBanned

        track, artist = self.music_controller.current_music()

        resp = self.configuration.locate.translate('MUSIC_INFO_SPOTIFY', music=track, artist=artist)

        await ctx.reply(resp)
        self.log.resp(resp)
        return None
