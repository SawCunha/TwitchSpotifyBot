from twitchAPI.chat.middleware import BaseCommandMiddleware
from twitchAPI.chat import ChatCommand
from twitch.chat.user_ban import UserBan


class UserBanned(BaseCommandMiddleware):

    def __init__(self, locate=None):
        self.execute_blocked_handler = self.handle_command_blocked
        self.locate = locate

    async def can_execute(self, cmd: ChatCommand) -> bool:
        user = cmd.user.name.lower()
        return user not in UserBan.users

    async def was_executed(self, cmd: ChatCommand):
        pass

    async def handle_command_blocked(self, cmd: ChatCommand):
        message = 'Você foi banido, não pode executar mais nenhum comando nessa Live.'
        if self.locate is not None:
            message = self.locate.translate('USER_BANNED')
        await cmd.reply(message)



