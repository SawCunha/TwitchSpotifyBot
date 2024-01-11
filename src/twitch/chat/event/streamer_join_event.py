from twitchAPI.chat import Chat, JoinEvent, LeftEvent
from twitchAPI.type import ChatEvent


class StreamerJoinEvent:

    def __init__(self, chat: Chat, channel: str, locate):
        self.chat: Chat = chat
        self.channel: str = channel
        self.locate = locate
        self.chat.register_event(ChatEvent.JOIN, self.on_join)
        self.chat.register_event(ChatEvent.USER_LEFT, self.on_left)

    async def on_join(self, join: JoinEvent):
        resp = self.locate.translate('JOIN_USER', user=join.user_name)
        await self.chat.send_message(self.channel, resp)

    async def on_left(self, left: LeftEvent):
        resp = self.locate.translate('LEFT_JOIN', user=left.user_name)
        await self.chat.send_message(self.channel, resp)
