from utils import Log
from twitchio.ext import commands, routines
from configuration.configuration import Configuration


class SpotifyRoutine(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.log: Log = bot.log
        self.configuration: Configuration = bot.configuration
        self.routine_init()

    @routines.routine(minutes=60, wait_first=True)
    async def send_link_commands(self):
        resp = self.configuration.locate.translate('LINK_COMMAND')

        channel = self.configuration.twitch.channel
        await self.bot.get_channel(channel).send(resp)
        self.log.resp(resp)

        return True

    def routine_init(self):
        self.log.info('Starting routines')
        try:
            self.send_link_commands.start()
        except RuntimeError:
            self.send_link_commands.restart()

