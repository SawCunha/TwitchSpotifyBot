from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub
from configuration.configuration import Configuration
from twitch.chat import SpotifyCommand, SpotifyRoutines, Mod, CommandChat, StreamerCommand, RoutinesChat, \
    StreamerJoinEvent
from pathlib import PurePath


class TwitchBot:
    def __init__(self, configuration: Configuration, music_controller, loop):
        self.configuration_twitch = configuration.twitch
        self.is_spotify = configuration.spotify.active
        self.music_controller = music_controller
        self.locate = configuration.locate
        self.loop = loop

    async def run(self):
        await self._connect_twitch()
        await self._create_chat()

    async def _connect_twitch(self):
        self.target_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
        self.twitch = await Twitch(self.configuration_twitch.my_app_id, self.configuration_twitch.my_app_secret)
        helper = UserAuthenticationStorageHelper(self.twitch, self.target_scope,
                                                 storage_path=PurePath('data/twitch_cache.json'))
        await helper.bind()

    async def _create_chat(self):
        self.chat = await Chat(self.twitch)
        self.chat.register_event(ChatEvent.READY, self.on_ready)

        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)
        self.chat.register_event(ChatEvent.SUB, self.on_sub)
        self.streamer_join_event = StreamerJoinEvent(self.chat, self.configuration_twitch.channel, self.locate)

        if self.is_spotify:
            self.spotify_command = SpotifyCommand(self.chat, self.music_controller, self.locate)
            self.spotify_routines = SpotifyRoutines(self.chat, self.configuration_twitch.channel, self.music_controller,
                                                    self.locate, self.loop)

        self.mod_command = Mod(self.chat, self.locate)
        self.command_chat = CommandChat(self.chat, self.configuration_twitch.commands, self.locate)
        self.routines_chat = RoutinesChat(self.chat, self.configuration_twitch.channel,
                                          self.configuration_twitch.routines, self.locate, self.loop)
        self.streamer_command = StreamerCommand(self.chat, locate=self.locate, command_chat=self.command_chat,
                                                routines_chat=self.routines_chat)

        self.chat.start()

    async def on_ready(self, ready_event: EventData):
        resp = self.locate.translate('BOT_UP')
        print(resp)
        await ready_event.chat.join_room(self.configuration_twitch.channel)
        await ready_event.chat.send_message(self.configuration_twitch.channel, resp)

    async def on_message(self, msg: ChatMessage):
        print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')

    async def on_sub(self, sub: ChatSub):
        print(f'New subscription in {sub.room.name}:\n'
              f'  Type: {sub.sub_plan}\n'
              f'  Message: {sub.sub_message}')

    async def stop_twitch(self):
        if self.is_spotify:
            self.spotify_command.unregister_commands()
            self.spotify_routines.unregister_routines()

        self.mod_command.unregister_commands()
        self.command_chat.unregister_commands()
        self.streamer_command.unregister_commands()
        self.routines_chat.unregister_routines()

        self.chat.stop()
        await self.twitch.close()
