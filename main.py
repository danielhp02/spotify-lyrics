import json
import spotipy
import spotipy.util as util

scope = 'user-read-playback-state'
username = 'dandalf21'

def get_artist(song):
    artists = []
    for artist in song['artists']:
        artists.append(artist['name'])
    return artists
# tokens = json.loads('./tokens.json')
with open('./tokens.json', 'r') as json_file:
    tokens = json.load(json_file)

token = util.prompt_for_user_token(username, scope, tokens['client_id'], tokens['client_secret'], tokens['redirect_uri'])
if token:
    sp = spotipy.Spotify(auth=token)
    current_playback = sp.current_playback()['item']
    current_song = {'name':  current_playback['name'],
                    'artist': get_artist(current_playback)}
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
else:
    print("Can't get token for", username)
