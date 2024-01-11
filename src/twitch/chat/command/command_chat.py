from twitchAPI.chat import Chat, ChatCommand
from twitch.chat.middleware.permission_middleware import PermissionMiddleware
from twitch.chat.middleware.command_cooldown import CommandCooldown
from twitch.chat.middleware.user_banned import UserBanned


class CommandChat:

    def __init__(self, chat, commands, locate):
        self.chat: Chat = chat
        self.commands: [] = commands
        self.locate = locate
        self._create_commands()

    def _create_commands(self):
        for command in self.commands:
            if command.active:
                command_middleware = [
                    CommandCooldown(cooldown_seconds=command.cooldown_seconds, locate=self.locate),
                    PermissionMiddleware(permission=command.permission, locate=self.locate),
                    UserBanned(locate=self.locate)
                ]
                self.chat.register_command(command.command, self.command, command_middleware=command_middleware)

    async def command(self, cmd: ChatCommand):
        message = self.get_message_by_command(cmd.name)
        await cmd.reply(message)

    def get_message_by_command(self, command_name: str):
        for command in self.commands:
            if command_name == command.command:
                return command.message

        return 'Trem, nu sei o que fala uai!'

    def unregister_commands(self):
        for command in self.commands:
            self.chat.unregister_command(command.command)

    def update_commands(self, commands: []):
        self.commands: [] = commands
        self._create_commands()
