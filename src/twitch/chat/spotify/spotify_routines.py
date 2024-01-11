from twitchAPI.chat import Chat
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio


class SpotifyRoutines:

    def __init__(self, chat, channel, music_controller, locate, loop):
        self.chat: Chat = chat
        self.channel: str = channel
        self.music_controller = music_controller
        self.locate = locate
        self.scheduler = BackgroundScheduler()
        self._create_routines()
        self.loop = loop

    def _create_routines(self):
        self.scheduler.add_job(self.send_link_commands, 'interval', minutes=40)

        self.start()

    def send_link_commands(self):
        resp = self.locate.translate('LINK_COMMAND')
        asyncio.run_coroutine_threadsafe(self.chat.send_message(self.channel, resp), self.loop)

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()

    def unregister_routines(self):
        self.stop()
        self.scheduler.remove_all_jobs()
