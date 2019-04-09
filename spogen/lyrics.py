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

def get_track(sp):
    current_playback = sp.current_playback()
    print(current_playback)
    current_playback = current_playback['item']
    art = get_art(current_playback)
    return {'name':  current_playback['name'],
            'artist': get_artist(current_playback),
            'album': current_playback['album']['name'],
            'album_art_big': art[0],
            'album_art_med': art[1],
            'album_art_sml': art[2]}

def get_lyrics(genius, song):
    try:
        return genius.search_song(song["name"], song["artist"][0]).lyrics
    except AttributeError:
        return "Lyrics not found."
    except TypeError:
        return 'You are not currently playing a song.'

def get_playing_status(sp):
    # Check if user is currently playing a song
    if sp.current_playback() != None:
        return True
    else: 
        return False

# def get_song_metadata(sp):
#     track_data_unformatted = sp.current_user_playing_track()
#     track_data = get_track(sp)
#     track_data['album_art'] = track_data_unformatted['item']['album']['images'][1]['url']
#     track_data['album'] = track_data_unformatted['item']['album']['name']
#     track_data['album_art_thumbnail'] = track_data_unformatted['item']['album']['images'][2]['url']
#     return track_data

def get_song_data(sp, genius):
    song_data = get_track(sp)
    if db.query_db("SELECT * FROM song WHERE name = ?", (song_data['name'],)) == []:
        print("Song not found in database. Song will be added.")
        db.query_db("SELECT name FROM song WHERE name = ?", (song_data['name'],))
        lyrics = get_lyrics(genius, song_data)
        db.query_db("INSERT INTO song (name, lyrics) VALUES (?, ?)", (str(song_data['name']), lyrics,))

        for artist in song_data["artist"]:
            db.query_db("INSERT INTO artists (artist, songname) VALUES (?, ?)", (str(artist), str(song_data['name']),))

        current_song_id = db.query_db("SELECT id FROM song WHERE id = (SELECT MAX(id) FROM song)")[0]["id"]
        print("current_song_id:", current_song_id)

        db.get_db().commit() # Saves database
        print("Current song successfully entered into database.")
    else:
        print("Song is already in database.")
        current_song_id = db.query_db("SELECT * FROM song WHERE name = ?", (song_data['name'],))[0]["id"]
        print("current_song_id:", current_song_id)

def print_track():
    current_song = db.query_db("SELECT * FROM song WHERE id = (SELECT MAX(id) FROM song)")[0]
    artists = db.query_db("SELECT * FROM artists WHERE songname = ?", (current_song["name"],))

    # print("type(current_song):", type(current_song))
    # print("artists:", artists[0][0])

    output = []

    # Process song name and artists
    if len(artists) == 1: # number of artists
        print("This song has one artist.")
        current_song_string = " ".join([current_song['name'], 'by', str(artists[0][0]), 'is now playing.'])
        output.append(current_song_string)
    else:
        print("This song has multiple artists.")
        artist_string = [artists[0][0]]
        for index in range(1, len(artists)):
            artist = artists[index][0]
            if artist == artists[-1][0]:
                artist_string.append(' and ' + str(artist))
            else:
                artist_string.append(', ' + str(artist))
        artist_string = ''.join(artist_string)
        current_song_string = " ".join([current_song['name'], 'by', str(artist_string), 'is now playing.'])
        output.append(current_song_string)

    # Process lyrics
    # print("lyrics:", repr(current_song["lyrics"]))
    lyrics = list(repr(current_song["lyrics"]).replace(r"\n", "<br>"))
    del lyrics[0]
    del lyrics[-1]
    lyrics = "".join(lyrics)
    # print(lyrics)
    output.append(lyrics)

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
