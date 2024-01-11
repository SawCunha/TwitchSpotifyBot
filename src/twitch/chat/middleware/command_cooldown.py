from twitchAPI.chat.middleware import BaseCommandMiddleware, GlobalCommandCooldown
from twitchAPI.chat import ChatCommand


class CommandCooldown(BaseCommandMiddleware):

    def __init__(self, cooldown_seconds: int = 10, locate=None):
        self.cooldown_seconds = cooldown_seconds
        self.global_command_cooldown: GlobalCommandCooldown = GlobalCommandCooldown(cooldown_seconds=cooldown_seconds)
        self.execute_blocked_handler = self.handle_command_cooldown
        self.locate = locate

    async def can_execute(self, cmd: ChatCommand) -> bool:
        return await self.global_command_cooldown.can_execute(cmd)

    async def was_executed(self, cmd: ChatCommand):
        await self.global_command_cooldown.was_executed(cmd)

    async def handle_command_cooldown(self, cmd: ChatCommand):
        message = f'O comando \'{cmd.name}\' está em espera, aguarde: {self.cooldown_seconds} segundos!'
        if self.locate is not None:
            message = self.locate.translate('COMMAND_COOLDOWN', command=cmd.name, time=self.cooldown_seconds)
        await cmd.reply(message)

