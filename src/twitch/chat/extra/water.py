from utils import Log
from twitchio.ext import commands, routines
from configuration.configuration import Configuration
import random


class Water(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.log: Log = bot.log
        self.configuration: Configuration = bot.configuration

        try:
            self.water_send_message.start()
        except RuntimeError:
            self.water_send_message.restart()

    @routines.routine(minutes=30, wait_first=True)
    async def water_send_message(self):
        message_id = random.randint(1, 100)
        resp = self.configuration.locate.translate(f'WATER_{message_id}')

        channel = self.configuration.twitch.channel
        await self.bot.get_channel(channel).send(resp)
        self.log.resp(resp)

        return True

