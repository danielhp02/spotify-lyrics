import sys
import json
import spotipy
import spotipy.util as util
import lyricsgenius

scope = 'user-read-playback-state'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

# Define functions
def get_artist(song):
    artists = []
    for artist in song['artists']:
        artists.append(artist['name'])
    return artists

def get_track(sp, text_output=False): # if text_output is False, it will output a dict
    # print(type(sp.current_playback()))
    current_playback = sp.current_playback()

    if current_playback is not None:
        current_playback = current_playback['item']
        return {'name':  current_playback['name'],
                'artist': get_artist(current_playback)}
    else:
        return {'name':  None,
                'artist': None}

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

# Load tokens
with open('./tokens.json', 'r') as json_file:
    tokens = json.load(json_file)

# Authenticate Spotify and Genius
token = util.prompt_for_user_token(username, scope, tokens["spotify"]['client_id'], tokens["spotify"]['client_secret'], tokens["spotify"]['redirect_uri'])
genius = lyricsgenius.Genius(tokens["genius"]["token"])

if token:
    sp = spotipy.Spotify(auth=token)

    current_song = {'name':  None,
                    'artist': None}
    running = True
    try:
        while running:
            last_song = current_song
            current_song = get_track(sp)

            if last_song['name'] != current_song['name']:
                print_track(current_song)
                genius_song = genius.search_song(current_song["name"], current_song["artist"][0])
                print(genius_song.lyrics)

    except KeyboardInterrupt:
        print("\nClosing...")
        sys.exit()
else:
    print("Can't get token for", username)
