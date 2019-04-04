import sys
import simplejson
from multiprocessing import Process, Value
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

# spotify data
def init(spotipy, util, lyricsgenius):
    scope = 'user-read-playback-state'
    username = "dandalf21"

    # Load tokens
    with open('./tokens.json', 'r') as json_file:
        tokens = simplejson.load(json_file)

    # Authenticate Spotify and Genius
    token = util.prompt_for_user_token(username, scope, tokens["spotify"]['client_id'], tokens["spotify"]['client_secret'], tokens["spotify"]['redirect_uri'])
    genius = lyricsgenius.Genius(tokens["genius"]["token"])

    sp = spotipy.Spotify(auth=token)

    return {"spotipy": sp,
            "genius":   genius}

# if len(sys.argv) > 1:
#     username = sys.argv[1]
# else:
#     print("Usage: %s username" % (sys.argv[0],))
#     sys.exit()

# Global data
class Data():
    def __init__(self):
        self.currently_playing_song = {'name':  None, 'artist': None, 'lyrics': None}

    def set_currently_playing_song(self, name, artist, lyrics):
        self.currently_playing_song['name'] = name
        self.currently_playing_song['artist'] = artist
        self.currently_playing_song['lyrics'] = lyrics

global_data = Data()

# Define functions
def get_artist(song):
    artists = []
    for artist in song['artists']:
        artists.append(artist['name'])
    return artists

def get_track(sp):
    current_playback = sp.current_playback()

    if current_playback is not None:
        current_playback = current_playback['item']
        return {'name':  current_playback['name'],
                'artist': get_artist(current_playback)}
    else:
        return {'name':  None,
                'artist': None}

def get_lyrics(genius, song):
    return genius.search_song(song["name"], song["artist"][0]).lyrics


def output_lyrics_loop(sp, genius):
    global global_data

    current_song = {'name':  None,
                    'artist': None}
    running = True

    while running:
        last_song = current_song
        current_song = get_track(sp)

        if last_song['name'] != current_song['name']:
            print_track(current_song)
            lyrics = get_lyrics(genius, current_song)

            global_data.set_currently_playing_song(current_song['name'], current_song['artist'], lyrics)
            print(global_data.currently_playing_song)

def print_track(current_song): # Change later, maybe to output a string or list of formatted strings (eg. [title, [artist1, artist2]])
    if len(current_song['artist']) == 1:
        print(current_song['name'], 'by', str(current_song['artist'][0]), 'is now playing.')
    else:
        artist_string = [current_song['artist'][0]]
        for index in range(1, len(current_song['artist'])):
            artist = current_song['artist'][index]
            if artist == current_song['artist'][-1]:
                artist_string.append(' and ' + str(artist))
            else:
                artist_string.append(', ' + str(artist))
        artist_string = ''.join(artist_string)
        print(current_song['name'], 'by', str(artist_string), 'is now playing.')

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
