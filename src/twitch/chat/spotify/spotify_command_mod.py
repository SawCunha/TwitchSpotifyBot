from twitchio.ext import commands
from utils import DB, Log
from utils.errors import *
from twitch.utils.twitch_utils import check_permission
from configuration.configuration import Configuration


class SpotifyCommandMod(commands.Cog):

    def __init__(self, bot):
        super()._load_methods(bot)
        self.bot = bot
        self.configuration = bot.configuration
        self.log: Log = bot.log
        self.db: DB = bot.db
        self.music_controller = bot.music_controller

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not self.db.is_user_privileged(ctx.author.name.lower()) or not self.db.is_user_admin(ctx.author.name.lower()):
            raise NotAuthorized('mod or admin')
        return True

    @commands.command(name='music-skip')
    async def skip_music(self, ctx: commands.Context):
        track, artist = self.music_controller.current_music()
        self.music_controller.skip_music()

        resp = self.configuration.locate.translate('SKIP_MUSIC_SPOTIFY', music=track, artist=artist)
        await ctx.reply(resp)
        self.log.resp(resp)

    @commands.command(name='music-play')
    async def play_music(self, ctx: commands.Context):
        track, artist = self.music_controller.current_music()
        self.music_controller.play_music()

        resp = self.configuration.locate.translate('PLAY_MUSIC_SPOTIFY', music=track, artist=artist)
        await ctx.reply(resp)
        self.log.resp(resp)

    @commands.command(name='music-pause')
    async def pause_music(self, ctx: commands.Context):
        track, artist = self.music_controller.current_music()
        self.music_controller.pause_music()

        resp = self.configuration.locate.translate('PAUSE_MUSIC_SPOTIFY', music=track, artist=artist)
        await ctx.reply(resp)
        self.log.resp(resp)
