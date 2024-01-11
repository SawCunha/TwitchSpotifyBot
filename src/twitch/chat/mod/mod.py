from twitch.chat.user_ban import UserBan
from twitchAPI.chat import Chat, ChatCommand
from twitch.chat.middleware.permission_middleware import PermissionMiddleware
from twitch.chat.middleware.user_banned import UserBanned


class Mod:
    def __init__(self, chat, locate):
        self.chat: Chat = chat
        self.locate = locate
        self._create_commands()

    def _create_commands(self):
        command_middleware = [PermissionMiddleware(locate=self.locate), UserBanned(locate=self.locate)]

        self.chat.register_command('music-ban', self.ban_command, command_middleware=command_middleware)
        self.chat.register_command('music-unban', self.unban_command, command_middleware=command_middleware)

    async def ban_command(self, cmd: ChatCommand):
        user = cmd.parameter.lower()

        if user not in UserBan.users:
            UserBan.users.append(user)

        resp = self.locate.translate('USER_BAN')
        await cmd.reply(resp)

    async def unban_command(self, cmd: ChatCommand):
        user = cmd.parameter.lower()

        if user in UserBan.users:
            UserBan.users.remove(user)

        resp = self.locate.translate('USER_UNBAN')
        await cmd.reply(resp)

    def unregister_commands(self):
        self.chat.unregister_command('music-ban')
        self.chat.unregister_command('music-unban')
