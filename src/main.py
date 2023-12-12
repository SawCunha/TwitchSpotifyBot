import os
from integration.spotify.spotify_api import Spotify
from twitch.twitch_bot import TwitchBot
from os.path import exists
from music.music_controller import MusicController
from utils import Log
from configuration.configuration import Configuration


def init_data_dir():
    if not exists('./data'):
        os.mkdir('./data')


def start_twitch_bot(configuration: Configuration, ac_log: Log):
    twitch_log = Log('Twitch', configuration.app.log)

    s_bot = Spotify(configuration.spotify)
    ac = MusicController(s_bot, ac_log)

    t_bot = TwitchBot(configuration, twitch_log, ac)
    t_bot.run()


def main():
    init_data_dir()
    configuration = Configuration()

    # Database log is used for both twitch and discord bots DB instances
    # Database not initialized in main function as it cannot be shared between threads
    ac_log = Log('music', configuration.app.log)

    start_twitch_bot(configuration, ac_log)


if __name__ == "__main__":
    main()
