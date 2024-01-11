import logging
from integration.spotify.spotify_api import Spotify
from twitch.twitch_bot import TwitchBot
from music.music_controller import MusicController
from configuration.configuration import Configuration
import asyncio


def start_twitch_bot(configuration: Configuration):
    music_controller: MusicController = None

    if configuration.spotify.active:
        spotify = Spotify(configuration.spotify)
        music_controller = MusicController(spotify)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot = TwitchBot(configuration, music_controller, loop)

    asyncio.run_coroutine_threadsafe(bot.run(), loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.error('Ocorreu erro ao tentar parar o loop')
    finally:
        asyncio.run(bot.stop_twitch())
        loop.stop()
        loop.close()


def main():
    configuration = Configuration()

    start_twitch_bot(configuration)


if __name__ == "__main__":
    main()
