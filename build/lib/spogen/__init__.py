import os
import spotipy
import spotipy.util as util
import lyricsgenius
from multiprocessing import Process, Value
from flask import Flask, render_template
import time
import schedule





def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import lyrics
    objects = lyrics.init(spotipy, util, lyricsgenius)

    
    @app.route('/')
    def root():
        if lyrics.get_playing_status(objects['spotipy']):
            song_metadata = lyrics.get_song_data(objects["spotipy"], objects["genius"])
            return render_template('base.html', song_album=song_metadata['album'], song_name=song_metadata['songname'], song_artist=song_metadata['artistlinks'], lyrics=song_metadata['lyrics'], album_art=song_metadata['albumart'][1],album_art_thumbnail=song_metadata['albumart'][2], songid=song_metadata['songid'], albumid=song_metadata['albumid'], videolink=song_metadata['videolink'])
        else:
            return render_template('noneplaying.html')

    return app
