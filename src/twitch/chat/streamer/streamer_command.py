from twitchAPI.chat import Chat, ChatCommand
from twitchAPI.chat.middleware import StreamerOnly
from twitch.chat import CommandChat, RoutinesChat
from configuration.command.command_process import process_commands
from configuration.routines.routine_process import process_routines


class StreamerCommand:
    def __init__(self, chat: Chat, locate, command_chat: CommandChat, routines_chat: RoutinesChat):
        self.chat: Chat = chat
        self.locate = locate
        self.command_chat: CommandChat = command_chat
        self.routines_chat: RoutinesChat = routines_chat
        self._create_commands()

    def _create_commands(self):
        command_middleware = [StreamerOnly()]

        self.chat.register_command('reload', self.reload, command_middleware=command_middleware)

    async def reload(self, cmd: ChatCommand):
        self.command_chat.unregister_commands()
        commands = process_commands()
        self.command_chat.update_commands(commands)

        self.routines_chat.unregister_routines()
        routines = process_routines()
        self.routines_chat.update_routines(routines)

        resp = self.locate.translate('COMMANDS_RELOAD')
        await cmd.reply(resp)

    def unregister_commands(self):
        self.chat.unregister_command('reload')
