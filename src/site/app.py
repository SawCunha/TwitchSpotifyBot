from flask import Flask, request
import flask
import spotipy
import os
import threading as th
import sys
path_src = os.path.abspath('./src')
sys.path.insert(1, path_src)
import main as bot
from logger import Log
from subprocess import call
import json

static_folder = os.path.abspath('./src/site/static')
app = Flask(__name__)

class Server:
    def __init__(self):
        self.bot_running = False
        if not os.path.exists('./data'):
            os.mkdir('./data')
        if not os.path.exists('./data/sbotify.log'):
            with open('./data/sbotify.log', 'w') as f:
                f.close()
        self.log = Log('Server')
        self.creds = bot.get_creds(self.log)
        self.user = self.creds['spotify username']
        self.cache_path = os.path.abspath(f'./secret/.cache-{self.user}')
        if not os.path.exists(self.cache_path):
            with open(self.cache_path, 'w') as f:
                json.dump({}, f)
                f.close()
                
        self.cache = spotipy.oauth2.CacheFileHandler(cache_path=self.cache_path, username=self.user)
        self.scopes = 'user-modify-playback-state user-read-playback-state user-read-currently-playing ' \
                      'user-read-playback-position user-read-recently-played streaming'
        self.spot_oath = None
        self.process = None

    def redirect_to_spotify(self):
        if self.bot_running:
            return flask.render_template("bot_running.html")
        else:
            redirect = request.base_url + "spotify-redirect"
            self.spot_oath = spotipy.SpotifyOAuth(client_id=self.creds["spotify client id"], client_secret=self.creds["spotify secret"], 
                                                  redirect_uri=redirect, open_browser=False, scope=self.scopes, cache_handler=self.cache)
            return flask.redirect(self.spot_oath.get_authorize_url())
    
    
    def spotify_callback(self):
        print(request.url)
        code = self.spot_oath.parse_response_code(request.url)
        print(code)
        self.spot_oath.get_access_token(code)
        print(self.bot_running)
        if not self.bot_running:
            th.Timer(1, self.start_bots).start()
            self.bot_running = True
        return flask.render_template("bot_running.html")
    
    def start_bots(self):
        try:
            call(["python3", "src/main.py"])
        except FileNotFoundError:
            call(["python", "src/main.py"])
    
    def run(self):
        app.run(host='0.0.0.0', port=5000)


if __name__ == "__main__":
    server = Server()
    @app.route("/", methods=["GET"])
    def route_index():
        return server.redirect_to_spotify()
    @app.route("/spotify-redirect", methods=["GET"])
    def route_spotify_redirect():
        return server.spotify_callback()
    @app.route("/static/style.css", methods=["GET"])
    def route_style():
        return flask.send_from_directory(static_folder, "style.css")
    server.run()

    

