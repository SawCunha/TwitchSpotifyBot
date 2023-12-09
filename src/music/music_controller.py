from utils.db_handler import DB
from utils.errors import TrackNotFound
from integration.spotify.spotify_api import Spotify
from utils import Log
from music.music_utils import is_spotify_link, process_spotify_link


class MusicController:
    def __init__(self, db: DB, spotify: Spotify, log: Log):
        self.db = db
        self.spotify = spotify
        self.log = log

    def add_to_queue(self, request: str):
        if is_spotify_link(request.strip()):
            link = process_spotify_link(request.strip())
        else:
            link = self.spotify.search_song(request)

        if link is not None:
            track, artist, link = self.spotify.get_track_info(url=link)
            self.spotify.add_to_queue(link)
        else:
            raise TrackNotFound

        return track, artist

    def current_music(self):
        return self.spotify.get_current_track()

    def skip_music(self):
        self.spotify.next()

    def pause_music(self):
        self.spotify.pause()

    def play_music(self):
        self.spotify.play()
