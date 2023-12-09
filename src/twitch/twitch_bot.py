import traceback
import sys
import asyncio
import twitchio
from twitchio.ext import commands, routines
from utils import Log, DB
from utils.errors import *
from music.music_controller import MusicController
from twitch.chat import *
from configuration.configuration import Configuration


class TwitchBot(commands.Bot):
    def __init__(self, configuration: Configuration, log: Log, db: DB, music_controller: MusicController):
        token = configuration.twitch.token
        twitch_channel = configuration.twitch.channel
        super().__init__(token, prefix='!', initial_channels=[twitch_channel])
        self.music_controller = music_controller
        self.db = db
        self.units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        self.is_live = False
        self.configuration = configuration
        self.log = log
        self.channel_name = twitch_channel
        self.channel_obj = None
        self.user_cache = self.db.get_all_users()
        self.offline_cogs = [ModCog, AdminCog]
        self.online_cogs = [SpotifyCommand, SpotifyCommandMod]

    async def global_before_invoke(self, ctx):
        user = ctx.author.name.lower()
        self.check_user(user)
        request = ctx.message.content.strip(str(ctx.prefix + ctx.command.name))
        self.log.req(user, request, ctx.command.name)

    @routines.routine(seconds=15)
    async def check_live(self):
        if self.channel_obj is None:
            return

        if self.configuration.app.dev:
            self.set_live(True)
            return

        data = await self.fetch_streams([self.channel_obj.id])
        if len(data) == 0:
            self.set_live(False)
        else:
            self.set_live(True)

    async def event_command_error(self, context: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.errors.CommandOnCooldown):
            resp = str(error)
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, commands.errors.CommandNotFound):
            resp = self.configuration.locate.translate('COMMAND_NOT_FOUND', command=error.name)
            await context.reply(resp)
            self.log.resp(str(error))
            self.log.resp(resp)

        elif isinstance(error, NotAuthorized):
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)
            self.log.error(str(error.__traceback__))
            resp = f'Sorry, you must be a {error.clearance} to use the {context.command.name} command!'
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, TargetNotFound):
            resp = f'Could not find target.'
            await context.reply(resp)
            self.log.error(resp)

        elif isinstance(error, UserAlreadyRole):
            if error.has_role:
                resp = f'User is already {error.role}'
            else:
                resp = f'User is not {error.role}'
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, NotActive):
            resp = f'Song request are currently turned off.'
            if not self.is_live:
                resp = resp + f'({self.channel_name} not live)'
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, TrackRecentlyPlayed):
            resp = f'{error.track} by {error.artist} has been recently played.'
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, TimeNotFound):
            resp = f'Could not find time period.'
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, UserBanned):
            self.log.resp(
                f'User: {context.author.name} is banned, not responding.')

        elif isinstance(error, YoutubeLink):
            resp = "Youtube support is coming soon!"
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, UnsupportedLink):
            resp = "Please only use spotify links!"
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, DBError):
            resp = "A db error occurred during handling of request"
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, BadPerms):
            resp = f'Sorry, you must be a {error.perm} to use this command!'
            await context.reply(resp)
            self.log.resp(resp)

        elif isinstance(error, asyncio.exceptions.TimeoutError):
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)
            self.log.error(error)
            if len(self.connected_channels) < 1:
                await asyncio.sleep(20)
                await self.join_channels(self.channel_name)

        elif isinstance(error, SettingsError):
            await context.reply(error.message)
            self.log.resp(error.message)

        else:
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)
            self.log.error(error)

    def check_user(self, user):
        if user in self.user_cache:
            return None
        else:
            self.db.check_user_exists(user)
            self.user_cache.append(user)
            return None

    @check_live.error
    async def live_error(self, error):
        self.log.error(str(error))
        await self.init_routines()

    async def routine_init(self):
        self.log.info('Starting routines')
        try:
            self.check_live.start()
        except RuntimeError:
            self.check_live.restart()

    async def event_ready(self):
        self.log.info('Bot is ready')

    async def event_reconnect(self):
        self.log.info('Bot is reconnecting')
        self.reload_cogs()

    async def event_channel_joined(self, channel: twitchio.Channel):
        await channel.send(self.configuration.locate.translate('BOT_UP'))
        self.load_cogs()
        self.log.info(f'Bot joined {channel.name}')
        self.channel_obj = await channel.user()
        await self.routine_init()

    def set_live(self, live: bool) -> None:
        if live == self.is_live:
            return

        self.is_live = live
        if live:
            self.log.info(f'{self.channel_name} now live! Starting online cog')
            self.load_online_cogs()

        else:
            self.log.info(f'{self.channel_name} no longer live! Stopping online cog')
            self.unload_online_cogs()

    @commands.command(name='sp-reload')
    async def reload_cogs_command(self, ctx):
        user = ctx.author.name.lower()
        request = ctx.message.content.strip(str(ctx.prefix + ctx.command.name))
        self.log.req(user, request, ctx.command.name)

        if not self.db.is_user_admin(user):
            return

        self.log.info('Reloading cogs')

        self.reload_cogs()

        await ctx.send('All cogs reloaded')

    def reload_cogs(self):
        self.unload_all_cogs()
        self.load_cogs()

    def load_online_cogs(self):
        if self.configuration.botSpotify.active:
            self.add_cog(SpotifyCommand(self))
            self.add_cog(SpotifyCommandMod(self))

    def unload_online_cogs(self):
        cog_names = [cog.__cogname__ for cog in self.online_cogs]
        loaded_cogs = [cog for cog in self.cogs.keys()]
        for cog in cog_names:
            if cog in loaded_cogs:
                self.remove_cog(cog)

    def unload_all_cogs(self):
        loaded_cogs = [cog for cog in self.cogs.keys()]
        for cog in loaded_cogs:
            self.remove_cog(cog)

    def load_offline_cogs(self):
        for cog in self.offline_cogs:
            self.add_cog(cog(self))

    def load_cogs(self):
        self.load_offline_cogs()
        if self.is_live:
            self.load_online_cogs()
