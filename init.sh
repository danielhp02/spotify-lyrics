#!/bin/sh
pip install spotipy
pip install simplejson
pip install lyricsgenius
export FLASK_APP=spogen
export FLASK_ENV=development
echo 'All done. Now what you need to do is execute flask init-db and then flask run.'