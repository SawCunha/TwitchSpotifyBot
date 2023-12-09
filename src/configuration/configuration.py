import configparser

from configuration.configurationApp import ConfigurationApp
from configuration.configurationTwitch import ConfigurationTwitch
from configuration.configurationSpotify import ConfigurationSpotify
from configuration.configurationBot import ConfigurationBot
from configuration.configurationBotSpotify import ConfigurationBotSpotify
from utils.enum.permission import Permission
from utils import LocateUtils


class Configuration:
    def __init__(self) -> None:
        self.app: ConfigurationApp = None
        self.twitch: ConfigurationTwitch = None
        self.spotify: ConfigurationSpotify = None
        self.bot: ConfigurationBot = None
        self.botSpotify: ConfigurationBotSpotify = None
        self._Process_configuration()
        self.locate = LocateUtils(self.app.language)

    def _Process_configuration(self):
        config = configparser.ConfigParser()
        with open('./secret/configuration.ini') as file:
            config.read_file(file)
            self._Process_configuration_app(config)
            self._Process_configuration_twitch(config)
            self._Process_configuration_spotify(config)
            self._Process_configuration_bot(config)
            self._Process_configuration_bot_spotify(config)

    def _Process_configuration_app(self, config_app):
        log: bool = config_app.getboolean('APP', 'log')
        dev: bool = config_app.getboolean('APP', 'dev')
        language: str = config_app.get('APP', 'language')
        self.app = ConfigurationApp(log, dev, language)

    def _Process_configuration_twitch(self, config_app):
        active: bool = config_app.getboolean('TWITCH', 'active')
        token: str = config_app.get('TWITCH', 'token')
        channel: str = config_app.get('TWITCH', 'channel')
        self.twitch = ConfigurationTwitch(active, token, channel)

    def _Process_configuration_spotify(self, config_app):
        client_id: str = config_app.get('SPOTIFY', 'client_id')
        secret: str = config_app.get('SPOTIFY', 'secret')
        username: str = config_app.get('SPOTIFY', 'username')
        self.spotify = ConfigurationSpotify(client_id, secret, username)

    def _Process_configuration_bot(self, config_app):
        active: bool = config_app.getboolean('BOT', 'active')
        permission: Permission = Permission(config_app.get('BOT', 'permission').lower())
        self.bot = ConfigurationBot(active, permission)

    def _Process_configuration_bot_spotify(self, config_app):
        active: bool = config_app.getboolean('BOT_SPOTIFY', 'active')
        self.botSpotify = ConfigurationBotSpotify(active)


    # @property
    # def app(self):
    #     return self.app
    #
    #
    # @property
    # def spotify(self):
    #     return self.spotify
    #
    #
    # @property
    # def twitch(self):
    #     return self.twitch