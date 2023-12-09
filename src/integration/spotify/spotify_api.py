import spotipy
from configuration.configuration import ConfigurationSpotify
from utils.errors import BadLink, NoCurrentTrack


class Spotify:
    def __init__(self, creds: ConfigurationSpotify):
        self.user = creds.username
        self.client_id = creds.client_id
        self.secret = creds.secret
        self.token = self.get_token()
        self.sp = self.auth()
        self.sp.search(q='test')

    def get_token(self):
        cache_path = f'./secret/.cache-{self.user}'
        handler = spotipy.oauth2.CacheFileHandler(cache_path=cache_path,
                                                  username=self.user)

        scopes = 'user-modify-playback-state user-read-playback-state ' \
                 'user-read-currently-playing user-read-playback-position' \
                 ' user-read-recently-played streaming'

        return spotipy.SpotifyOAuth(client_id=self.client_id,
                                    client_secret=self.secret,
                                    redirect_uri='https://open.spotify.com/',
                                    cache_handler=handler,
                                    open_browser=False, scope=scopes)

    def auth(self):
        return spotipy.Spotify(auth_manager=self.token)

    def search_song(self, query):
        try:
            results = self.sp.search(query, limit=1, type='track')
            if results is None:
                return None
            else:
                return results['tracks']['items'][0]['external_urls']['spotify']
        except IndexError:
            return None

    def add_to_queue(self, uri):
        try:
            self.sp.add_to_queue(uri)
        except IndexError:
            return None

    def get_current_playlist(self):
        info = self.sp.current_playback()
        if info is None:
            return None
        try:
            return info['context']['external_urls']['spotify']
        except (KeyError, TypeError):
            return None

    def get_track_info(self, url=None, info=None):

        if url is None and info is None:
            raise BadLink

        if info is None:
            info = self.sp.track(url)
            if info is None:
                raise BadLink

        link = info['external_urls']['spotify']
        track = info['name']
        artists_info_all = info['artists']
        artists = []
        for artist_info in artists_info_all:
            artist = artist_info['name']
            artists.append(artist)
        artists = str(artists)
        artists = artists.strip('[')
        artists = artists.strip(']')
        artists = artists.strip("'")
        artists = artists.replace("'", '')
        return track, artists, link

    def get_current_track(self):
        try:
            info = self.sp.current_user_playing_track()['item']
            if info is None:
                raise NoCurrentTrack
            track, artist, _ = self.get_track_info(info=info)
            return track, artist
        except TypeError:
            raise NoCurrentTrack

    def get_track_link(self, request):
        if 'open.spotify' in request:
            words = request.split(' ')
            link = None
            for word in words:
                if 'open.spotify' in word:
                    link = word
                    link = link.strip('\r')
                    link = link.strip('\n')
            try:
                track, artist, link = self.get_track_info(url=link)
                return track, artist, link

            except spotipy.SpotifyException:
                return None, None, None

        elif 'http' in request:
            return None, None, None

        else:
            request = request.replace('!sr ', '')
            request = request.replace(' by ', ' ')
            request = request.strip('-')
            song_link = self.search_song(request)
            if song_link:
                track, artist, link = self.get_track_info(url=song_link)
                return track, artist, song_link
            else:
                return None, None, None

    def skip(self):
        track, artist = self.get_current_track()
        self.sp.next_track()
        return track, artist

    def get_context(self) -> dict:
        try:
            info = self.sp.current_user_playing_track()
            if info is None:
                raise NoCurrentTrack
            track = info['item']['name']
            artists_info_all = info['item']['artists']
            artists = []
            for artist_info in artists_info_all:
                artist = artist_info['name']
                artists.append(artist)
            artists = str(artists)
            artists = artists.strip('[')
            artists = artists.strip(']')
            artists = artists.strip("'")
            artists = artists.replace("'", '')
            image = info['item']['album']['images'][1]['url']
            prog = info['progress_ms']
            length = info['item']['duration_ms']
            track_id = info['item']['id']
            if info['is_playing']:
                paused = False
            else:
                paused = True
            try:
                playlist = info['context']['external_urls']['spotify']
            except TypeError:
                playlist = None
            return {'track': track,
                    'artist': artists,
                    'progress': prog,
                    'duration': length,
                    'album_art': image,
                    'playlist': playlist,
                    'playback_id': track_id,
                    'paused': paused}
        except TypeError as er:
            print(er)
            raise NoCurrentTrack

    def next(self):
        self.sp.next_track()

    def pause(self):
        playback = self.sp.current_playback()
        if playback['is_playing']:
            self.sp.pause_playback()

    def play(self):
        playback = self.sp.current_playback()
        if not playback['is_playing']:
            self.sp.start_playback()
