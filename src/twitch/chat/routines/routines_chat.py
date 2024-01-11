from twitchAPI.chat import Chat
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio


class RoutinesChat:

    def __init__(self, chat: Chat, channel: str, routines: [], locate, loop):
        self.chat: Chat = chat
        self.channel = channel
        self.routines: [] = routines
        self.locate = locate
        self.scheduler = BackgroundScheduler()
        self._create_routines()
        self.loop = loop

    def _create_routines(self):
        for routine in self.routines:
            if routine.active:
                self.scheduler.add_job(self.routine_executor, 'interval', minutes=routine.time_minutes,
                                       args=[routine.message], id=routine.routine)

        self.start()

    def routine_executor(self, message):
        asyncio.run_coroutine_threadsafe(self.chat.send_message(self.channel, message), self.loop)

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()

    def unregister_routines(self):
        self.stop()
        self.scheduler.remove_all_jobs()

    def update_routines(self, routines: []):
        self.routines: [] = routines
        self.scheduler = BackgroundScheduler()
        self._create_routines()
