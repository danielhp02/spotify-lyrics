import sys
import urllib.request
import urllib.parse
import re
import simplejson
import spotipy
from . import db
import click
from flask import current_app, g, render_template
from flask.cli import with_appcontext
import requests
from requests.exceptions import HTTPError, Timeout

adding_to_db = False

# spotify data
def init(spotipy, util, lyricsgenius):
    scope = 'user-read-playback-state'
    username = "dandalf21" # <-- Change to your Spotify username

    # Load tokens
    with open('./tokens.json', 'r') as json_file:
        tokens = simplejson.load(json_file)
    
    # Authenticate Spotify and Genius
    token = util.prompt_for_user_token(username, scope, tokens["spotify"]['client_id'], tokens["spotify"]['client_secret'], tokens["spotify"]['redirect_uri'])
    genius = lyricsgenius.Genius(tokens["genius"]["token"])
    genius.skip_non_songs = True

    sp = spotipy.Spotify(auth=token)
    return {"spotipy":  sp,
            "genius":   genius}

# Define functions
def get_artists(song, s):
    # will always return a list
    artists = []
    for i in range(len(song)):
        artists.append(song[i][s])
    return artists

def get_art(song):
    art = []
    for i in song['album']['images']:
        art.append(i['url'])
    return art

def get_lyrics(genius, song_data):
    try:
        artist_name = ', '.join(song_data['artist'])
        genius_data = genius.search_song(song_data["songname"], artist_name)
        return [genius_data.lyrics, genius_data.url]
    except AttributeError:
        return "Lyrics not found."
    except HTTPError as e:
        print(e.errno)    # status code
        print(e.args[0])  # status code
        print(e.args[1])  # error message
    except Timeout:
        print("Request timed out.")
        return get_lyrics(genius, song_data)#"Request timed out."

def get_playing_status(sp):
    # Check if user is currently playing a song
    current_playback = sp.current_playback()
    if current_playback != None:
        return True if current_playback['currently_playing_type'] == 'track' else False
    else:
        return False

def format_song_name(song_name):
    # First try to format songnames ending in " - [year] Remaster" and similar variants
    matchObj = re.match(r'(.*) - \d\d\d\d remaster', song_name, re.I)
    if matchObj:
        print("Name formatted: songname ends in \" - [year] Remaster...\"")
        return matchObj.group(1)

    # Then try songnames without a year or the year at the end
    matchObj = re.match(r'(.*) - remaster', song_name, re.I)
    if matchObj:
        print("Name formatted: songname ends in \" - Remaster...\"")
        return matchObj.group(1)

    # Try songnames of singles
    matchObj = re.match(r'(.*) - single', song_name, re.I)
    if matchObj:
        print("Name formatted: songname ends in \" - ... Single\"")
        return matchObj.group(1)

    # Try songs with featured (ie, additional) artists. NOTE: not always beneficial, thus commented out
    # matchObj = re.match(r'(.*) \(feat.*\)', song_name, re.I)
    # if matchObj:
    #     print("Name formatted: songname ends in \"(feat...)\"")
    #     return matchObj.group(1)

    # If there are no matches, return the input as is
    return song_name

def get_song_data(sp, genius):
    global adding_to_db

    try:
        current_playback = sp.current_playback()['item']

        song_data = {
            'rawsongname': current_playback['name'],
            'songname': format_song_name(str(current_playback['name'])),
            'songid': current_playback['id'],
            'album': current_playback['album']['name'],
            'albumid': current_playback['album']['id'],
            'albumartistid': current_playback['artists'][0]['id'],
            'artist': get_artists(current_playback['artists'], 'name'),
            'artistid': get_artists(current_playback['artists'], 'id'),
            'albumart': get_art(current_playback), # list: [large, medium, small]
            'videolink': '0'
        }

        # Get lyrics from genius or the database
        if db.query_db('SELECT SONGID FROM SONG WHERE SONGID = ?', (song_data['songid'],)) == []:
            if adding_to_db != True:
                print('Song: %s not found in database. Adding...' % song_data['songname'])
                adding_to_db = True
                genius_data = get_lyrics(genius, song_data)
                db.query_db('INSERT INTO SONG (SONGID, SONGNAME, LYRICS, URL) VALUES (?, ?, ?, ?)', (song_data['songid'], song_data['songname'], genius_data[0], genius_data[1]))
            else:
                return None
        else:
            print('Song: %s found in database.' % song_data['songname'])

        # Save the database
        db.get_db().commit()

        # Save the lyrics in the dictionary with <br> newline characters
        song_data['lyrics'] = db.query_db('SELECT LYRICS FROM SONG WHERE SONGID = ?', (song_data['songid'],))[0]['lyrics'].replace('\n', '<br>')

        # Convert the genius URL into a HTML link
        song_data['lyricsurl'] = '<a href=\'{0}\' target=\'_blank\' rel=\'noopener noreferrer\'>Lyrics from Genius</a>'.format(db.query_db('SELECT URL FROM SONG WHERE SONGID = ?', (song_data['songid'],))[0][0])

        # Convert the song name into a link
        song_data['songlink'] = '<a href=\'https://open.spotify.com/track/{0}\' target=\'_blank\' rel=\'noopener noreferrer\'>{1}</a>'.format(song_data['songid'], song_data['rawsongname'])

        # Convert album name to a link
        song_data['albumlink'] = '<a href=\'https://open.spotify.com/album/{0}\' target=\'_blank\' rel=\'noopener noreferrer\'>{1}</a>'.format(song_data['albumid'], song_data['album'])

        # Generate an img tag for the album art
        song_data['albumartimage'] = '<img src={0} />'.format(song_data['albumart'][1])

        # Convert the artists into links
        out = ''
        for s, t in zip(song_data['artistid'], song_data['artist']):
            out += ('<a href=\'https://open.spotify.com/artist/{0}\' target=\'_blank\' rel=\'noopener noreferrer\'>{1}</a>'.format(s, t))
            out += ', '
        song_data['artistlinks'] = out[0:-2]

        adding_to_db = False
        return song_data
    except TypeError:
        print("No song is currently playing.")
        return "nothing playing" # eh should work

def set_lyrics(songid, songname, lyrics):
    db.query_db('UPDATE SONG SET LYRICS = ? WHERE SONGID = ? AND SONGNAME = ?', (lyrics, str(songid), str(songname)))
    db.get_db().commit()
    print(songid)
    print(db.query_db('SELECT LYRICS FROM SONG WHERE SONGID = ?', (songid,) ))
