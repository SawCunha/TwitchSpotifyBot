from twitchAPI.chat.middleware import BaseCommandMiddleware
from twitchAPI.chat import ChatCommand, ChatUser
from utils.enum.permission import Permission


class PermissionMiddleware(BaseCommandMiddleware):

    def __init__(self, permission: Permission = Permission.ALL, locate=None):
        self.execute_blocked_handler = self.handle_command_blocked
        self.locate = locate
        self.permission: Permission = permission

    async def can_execute(self, cmd: ChatCommand) -> bool:
        return self.check_permission(cmd.user)

    async def was_executed(self, cmd: ChatCommand):
        pass

    async def handle_command_blocked(self, cmd: ChatCommand):
        message = f'Você não tem permissão para usar esse comando: "{cmd.name}"!'
        if self.locate is not None:
            message = self.locate.translate('NOT_PERMISSION', command=cmd.name)
        await cmd.reply(message)

    def check_permission(self, user: ChatUser):
        if user.badges is not None and 'broadcaster' in user.badges.keys() and user.badges['broadcaster'] == '1':
            return True
        if self.permission is Permission.ALL.name:
            return True
        if self.permission is Permission.SUBSCRIBER.name:
            if not user.subscriber:
                return False
        if self.permission is Permission.MOD.name:
            if not user.mod:
                return False
        if self.permission is Permission.TURBO.name:
            if not user.turbo:
                return False
        if self.permission is Permission.VIP.name:
            if not user.vip:
                return False

        return True
