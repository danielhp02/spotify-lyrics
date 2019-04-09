import sys
import simplejson
import spotipy
from multiprocessing import Process, Value
# import sqlite3
from . import db

import click
from flask import current_app, g, render_template
from flask.cli import with_appcontext

current_song_id = 0

# spotify data
def init(spotipy, util, lyricsgenius):
    scope = 'user-read-playback-state'
    username = "shawarmawolf" # <-- Change to your Spotify username

    # Load tokens
    with open('./tokens.json', 'r') as json_file:
        tokens = simplejson.load(json_file)

    # Authenticate Spotify and Genius
    token = util.prompt_for_user_token(username, scope, tokens["spotify"]['client_id'], tokens["spotify"]['client_secret'], tokens["spotify"]['redirect_uri'])
    genius = lyricsgenius.Genius(tokens["genius"]["token"])

    sp = spotipy.Spotify(auth=token)
    return {"spotipy":  sp,
            "genius":   genius}

# if len(sys.argv) > 1:
#     username = sys.argv[1]
# else:
#     print("Usage: %s username" % (sys.argv[0],))
#     sys.exit()

# Define functions
def get_artist(song):
    artists = []
    for artist in song['artists']:
        artists.append(artist['name'])
    return artists

# returns a list of all the links to all art sizes
def get_art(song):
    art = []
    for i in song['album']['images']:
        art.append(i['url'])
    return art

def concat_list(l):
    out = ''
    for s in l:
        if out == '':
            out = s
        else:
            out = out + ', ' + s
    return out


def get_track(sp):
    current_playback = sp.current_playback()
    current_playback = current_playback['item']
    art = get_art(current_playback)
    return {'name':  current_playback['name'],
            'artistid': current_playback['artists'][0]['id'],
            'albumid': current_playback['album']['id'],
            'songid': current_playback['id'],
            'artist': current_playback['artists'][0]['name'],
            'album': current_playback['album']['name'],
            'albumartbig': art[0],
            'albumartmed': art[1],
            'albumartsml': art[2],
            'tracknr': current_playback['track_number']}

def get_lyrics(genius, song):
    try:
        print(song["artist"])
        return genius.search_song(song["name"], song["artist"]).lyrics
    except AttributeError:
        return "Lyrics not found."

def get_playing_status(sp):
    # Check if user is currently playing a song
    if sp.current_playback() != None:
        return True
    else: 
        return False

def get_song_data(sp, genius):

    song_data = get_track(sp)
    print(song_data['artist'])
    if db.query_db("SELECT SONGID FROM SONG WHERE SONGID = ?", (song_data['songid'],)) == []:
        if db.query_db('SELECT * FROM ARTIST WHERE ARTISTID = ?', (song_data['artistid'],)) == []:
            print('Artist not found in database. Artist will be added.')
            db.query_db('INSERT INTO ARTIST (ARTISTID, ARTISTNAME) VALUES (?, ?)', (song_data['artistid'], song_data['artist']))

        if db.query_db('SELECT * FROM ALBUM WHERE ALBUMID = ?', (song_data['albumid'],)) == []:
            print('Album not found in database. Album will be added.')
            db.query_db('INSERT INTO ALBUM (ALBUMID, ARTISTID, ALBUMNAME, ALBUMARTBIG, ALBUMARTMED, ALBUMARTSML) VALUES (?, ?, ?, ?, ?, ?)', (song_data['albumid'], song_data['artistid'], song_data['album'], song_data['albumartbig'], song_data['albumartmed'], song_data['albumartsml'],))

        print("Song not found in database. Song will be added.")
        lyrics = get_lyrics(genius, song_data)
        db.query_db("INSERT INTO SONG (SONGID, ALBUMID, SONGNAME, LYRICS, TRACKNR) VALUES (?, ?, ?, ?, ?)", (song_data['songid'], song_data['albumid'], song_data['name'], lyrics, song_data['tracknr'],))

        current_song_id = song_data['songid']
        print("current_song_id:", current_song_id)

        db.get_db().commit() # Saves database
        print("Current song successfully entered into database.")
    else:
        print("Song is already in database.")
        current_song_id = song_data['songid']
        print("current_song_id:", current_song_id)
    return current_song_id

def print_track(songid):
    song = db.query_db("SELECT * FROM SONG WHERE SONGID = ?", (songid,))
    album = db.query_db("SELECT * FROM ALBUM WHERE ALBUMID == ?", (song[0]['ALBUMID'],))
    artist = db.query_db("SELECT * FROM ARTIST WHERE ARTISTID == ?", (album[0]['ARTISTID'],))

    lyrics = list(repr(song[0]["LYRICS"]).replace(r"\n", "<br>"))
    del lyrics[0]
    del lyrics[-1]
    lyrics = "".join(lyrics)

    output = {  'name': song[0]['SONGNAME'],
                'album': album[0]['ALBUMNAME'],
                'artist': artist[0]['ARTISTNAME'],
                'albumartbig': album[0]['ALBUMARTBIG'],
                'albumartmed': album[0]['ALBUMARTMED'],
                'albumartsml': album[0]['ALBUMARTSML'],
                'tracknr': song[0]['TRACKNR'],
                'lyrics': lyrics,
                'songid': song[0]['SONGID'],
                'albumid': album[0]['ALBUMID'],
                'artistid': artist[0]['ARTISTID']
    }
    return output

# def output_lyrics_loop(sp, genius):

    # running = True
    #
    # while running:
    #     last_song = current_song
    #     current_song = get_track(sp)

        # if last_song['name'] != current_song['name']:
            # print_track(current_song)
            # lyrics = get_lyrics(genius, current_song)

            # global_data.set_currently_playing_song(current_song['name'], current_song['artist'], lyrics)
            # print(global_data.currently_playing_song)

# @app.route('/')
# def index():
#     # print(currently_playing_song)
#     return str(global_data.currently_playing_song)
#
# if __name__ == "__main__":
#    # recording_on = Value('b', True)
#    p = Process(target=output_lyrics_loop, args=(sp,))
#    p.start()
#    app.run(debug=True, use_reloader=False)
#    p.join()

# if token:
#     sp = spotipy.Spotify(auth=token)
#
#     current_song = {'name':  None,
#                     'artist': None}
#     running = True
#     try:
#         while running:
#             last_song = current_song
#             current_song = get_track(sp)
#
#             if last_song['name'] != current_song['name']:
#                 print_track(current_song)
#                 print(get_lyrics(current_song))
#
#     except KeyboardInterrupt:
#         print("\nClosing...")
#         sys.exit()
# else:
#     print("Can't get token for", username)
