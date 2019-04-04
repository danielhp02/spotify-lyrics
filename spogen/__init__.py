import os
import sys
import simplejson
import spotipy
import spotipy.util as util
import lyricsgenius
from multiprocessing import Process, Value
from flask import Flask


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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import lyrics
    objects = lyrics.init(spotipy, util, lyricsgenius)
    p = Process(target=lyrics.output_lyrics_loop, args=(objects["spotipy"], objects["genius"],))
    p.start()
    # app.run(debug=True, use_reloader=False)
    # p.join()
    # lyrics.output_lyrics_loop(objects["spotipy"], objects["genius"])

    return app
