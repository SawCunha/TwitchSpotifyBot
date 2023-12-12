from twitchio.ext import commands
from utils import Log
from utils.errors import *
from twitch.chat.user_ban import UserBan


class SpotifyCommandMod(commands.Cog):

    def __init__(self, bot):
        super()._load_methods(bot)
        self.bot = bot
        self.configuration = bot.configuration
        self.log: Log = bot.log
        self.music_controller = bot.music_controller

    async def cog_check(self, ctx: commands.Context) -> bool:
        user = ctx.author.name.lower()

        if not ctx.author.is_mod and not ctx.author.is_broadcaster:
            raise NotAuthorized('NOT_PERMISSION')

        if user in UserBan.users:
            raise UserBanned

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
