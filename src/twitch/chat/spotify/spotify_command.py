from twitchAPI.chat import Chat, ChatCommand
from twitch.chat.middleware.permission_middleware import PermissionMiddleware
from twitch.chat.middleware.command_cooldown import CommandCooldown
from twitch.chat.middleware.user_banned import UserBanned
from utils.enum.permission import Permission


class SpotifyCommand:

    def __init__(self, chat, music_controller, locate):
        self.chat: Chat = chat
        self.music_controller = music_controller
        self.locate = locate
        self._create_commands()

    def _create_commands(self):
        command_middleware_music = [CommandCooldown(cooldown_seconds=10, locate=self.locate), PermissionMiddleware(locate=self.locate), UserBanned(locate=self.locate)]
        self.chat.register_command('music', self.music, command_middleware=command_middleware_music)

        command_middleware_command_info = [CommandCooldown(cooldown_seconds=60, locate=self.locate), PermissionMiddleware(locate=self.locate), UserBanned(locate=self.locate)]
        self.chat.register_command('music-info', self.music_info, command_middleware=command_middleware_command_info)
        self.chat.register_command('music-help', self.music_help, command_middleware=command_middleware_command_info)

        command_middleware_mod = [CommandCooldown(cooldown_seconds=30, locate=self.locate), PermissionMiddleware(locate=self.locate, permission=Permission.MOD), UserBanned(locate=self.locate)]
        self.chat.register_command('music-skip', self.skip_music, command_middleware=command_middleware_mod)
        self.chat.register_command('music-play', self.play_music, command_middleware=command_middleware_mod)
        self.chat.register_command('music-pause', self.pause_music, command_middleware=command_middleware_mod)

    async def music(self, cmd: ChatCommand):
        if len(cmd.parameter) == 0:
            await cmd.reply('Voce deve fornecer o nome ou link da musica')
            return

        track, artist = self.music_controller.add_to_queue(cmd.parameter)

        if track is None:
            resp = self.locate.translate('NOT_FOUND_MUSIC_SPOTIFY')
            await cmd.reply(resp)
            return False
        else:
            resp = self.locate.translate('MUSIC_ADD_SPOTIFY', music=track, artist=artist)
            await cmd.reply(resp)
            await cmd.send(f'!addpoints {cmd.user.name} 25')
            return True

    async def music_info(self, cmd: ChatCommand):
        track, artist = self.music_controller.current_music()

        resp = self.locate.translate('MUSIC_INFO_SPOTIFY', music=track, artist=artist)

        await cmd.reply(resp)
        return True

    async def music_help(self, cmd: ChatCommand):
        resp = self.locate.translate('LINK_COMMAND')
        await cmd.reply(resp)
        return True

    async def skip_music(self, cmd: ChatCommand):
        track, artist = self.music_controller.current_music()
        self.music_controller.skip_music()

        resp = self.locate.translate('SKIP_MUSIC_SPOTIFY', music=track, artist=artist)
        await cmd.reply(resp)

    async def play_music(self, cmd: ChatCommand):
        track, artist = self.music_controller.current_music()
        self.music_controller.play_music()

        resp = self.locate.translate('PLAY_MUSIC_SPOTIFY', music=track, artist=artist)
        await cmd.reply(resp)

    async def pause_music(self, cmd: ChatCommand):
        track, artist = self.music_controller.current_music()
        self.music_controller.pause_music()

        resp = self.locate.translate('PAUSE_MUSIC_SPOTIFY', music=track, artist=artist)
        await cmd.reply(resp)

    def unregister_commands(self):
        self.chat.unregister_command('music')
        self.chat.unregister_command('music-info')
        self.chat.unregister_command('music-help')
        self.chat.unregister_command('music-skip')
        self.chat.unregister_command('music-play')
        self.chat.unregister_command('music-pause')