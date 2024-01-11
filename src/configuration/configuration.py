import configparser

from configuration.configuration_twitch import ConfigurationTwitch
from configuration.command.command_process import process_commands
from configuration.routines.routine_process import process_routines
from configuration.configuration_spotify import ConfigurationSpotify
from configuration.configuration_openai import ConfigurationOpenAi
from utils import LocateUtils


class Configuration:
    def __init__(self) -> None:
        self.twitch: ConfigurationTwitch = None
        self.spotify: ConfigurationSpotify = None
        self._Process_configuration()
        self.locate = LocateUtils()

    def _Process_configuration(self):
        config = configparser.ConfigParser()
        with open('./data/configuration.ini') as file:
            config.read_file(file)
            self._Process_configuration_twitch(config)
            self._Process_configuration_spotify(config)
            self._Process_configuration_openai(config)

    def _Process_configuration_twitch(self, config_app):
        my_app_id: str = config_app.get('TWITCH', 'my_app_id', fallback=None)
        my_app_secret: str = config_app.get('TWITCH', 'my_app_secret', fallback=None)
        channel: str = config_app.get('TWITCH', 'channel', fallback=None)
        commands = process_commands()
        routines = process_routines()
        self.twitch = ConfigurationTwitch(my_app_id, my_app_secret, channel, commands, routines)

    def _Process_configuration_spotify(self, config_app):
        active: bool = config_app.getboolean('SPOTIFY', 'active', fallback=False)
        client_id: str = config_app.get('SPOTIFY', 'client_id', fallback=None)
        secret: str = config_app.get('SPOTIFY', 'secret', fallback=None)
        username: str = config_app.get('SPOTIFY', 'username', fallback=None)
        self.spotify = ConfigurationSpotify(active, client_id, secret, username)

    def _Process_configuration_openai(self, config_app):
        active: bool = config_app.getboolean('OPENAI', 'active', fallback=False)
        api_key: str = config_app.get('OPENAI', 'api_key', fallback=None)
        gpt_model: str = config_app.get('OPENAI', 'gpt_model', fallback=None)
        self.openai = ConfigurationOpenAi(active, api_key, gpt_model)
