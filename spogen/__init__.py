import os
import sys
import spotipy
import spotipy.util as util
import lyricsgenius
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True) if test_config is None else app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # ensure tokens.json exists
    # doesn't actually halt execution, just catches ugly error and packages it nicely
    if not os.path.isfile('./tokens.json'): sys.exit('ERROR: tokens.json not found!')

    from . import db
    db.init_app(app)

    from . import lyrics
    objects = lyrics.init(spotipy, util, lyricsgenius)

    @app.route('/_get_music_data')
    def get_music_data():
        nonlocal objects # use objects from the parent function

        try:
            song_details = lyrics.get_song_data(objects["spotipy"], objects["genius"])
        except spotipy.client.SpotifyException:
            print("Token expired. Refreshing...")
            objects = lyrics.init(spotipy, util, lyricsgenius)
            print("Token refreshed.")
            song_details = lyrics.get_song_data(objects["spotipy"], objects["genius"])

        if song_details != None and song_details != "nothing playing":
            return jsonify(song_details)
        elif song_details == "nothing playing":
            return jsonify(songname = '', lyrics = '')
        else:
            return jsonify(songname = '', lyrics = 'Adding song to database...')

    @app.route('/')
    def root():
        if lyrics.get_playing_status(objects['spotipy']):
            print("something playing")
            return render_template('base.html')
        else:
            print("nothing playing")
            return render_template('noneplaying.html')

    @app.route('/_get_lyrics', methods=['POST'])
    def lyrics_post():
        nonlocal objects # use objects from the parent function
        newLyrics = request.form['lyrics'].replace('\n', '<br>')

        try:
            song_details = lyrics.get_song_data(objects["spotipy"], objects["genius"])
        except spotipy.client.SpotifyException:
            print("Token expired. Refreshing...")
            objects = lyrics.init(spotipy, util, lyricsgenius)
            print("Token refreshed.")
            song_details = lyrics.get_song_data(objects["spotipy"], objects["genius"])

        lyrics.set_lyrics(song_details['songid'], song_details['songname'], newLyrics)
        print("new lyrics:", newLyrics)
        return redirect(url_for('root'))

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    return app
