# spotify-lyrics

Gets current track from Spotify, gets the lyrics from Genius and outputs to a Flask app.

## Dependencies

* [spotipy](https://github.com/plamere/spotipy) - Used for getting current song data from Spotify; MAKE SURE YOU BUILD FROM SOURCE DON'T USE PACAKAGE MANAGER
  * [Requests](https://github.com/kennethreitz/requests) - Required by spotipy
* [LyricsGenius](https://github.com/johnwmillr/LyricsGenius) - Used for getting lyrics from Genius
* [Flask](http://flask.pocoo.org/docs/1.0/)
  * [Werkzeug](http://werkzeug.pocoo.org/)
  * [Jinja2](http://jinja.pocoo.org/)
  * [MarkupSafe](https://pypi.org/project/MarkupSafe/) - Comes with Jinja2
  * [ItsDangerous](https://pythonhosted.org/itsdangerous/)
  * [Click](http://click.pocoo.org/)
* [SimpleJSON](https://simplejson.readthedocs.io/) - Used for reading the tokens file

## Set up

The following set up guide is written under the assumption that you are using a Unix based shell. If not, I *highly* recommend you get one. I use Ubuntu through [WSL (Windows Subsystem for Linux)](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

### Code adjustments

* Change the `username` string on line 16 of `./spogen/lyrics.py` to your Spotify username.

### Console

Run . ./int.sh

### Tokens

At the moment, tokens must be manually added. Support for oAuth 2.0 is planned to be implemented soon.

* Duplicate `./tokens.dummy.json` and rename it to `tokens.json`.
* Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and log in.
* Create a new app. Name it whatever, I called it `spotify-lyrics`. Set the redirect URI to `http://localhost/`
* Now if you go into the app, you can get the client id and secret. You'll want to copy those into `tokens.json`. Also set your redirect URI in `tokens.json` to `http://localhost/` as well.
* Go to the [Genius API Clients](https://genius.com/api-clients) page and create an API client.
* For the app name, again doesn't really matter, but you should name it the same as the Spotify one. Set the "App Website URL" to `http://localhost/` or the [Github page](https://github.com/danielhp02/spotify-lyrics/).
* Copy the client access token into `tokens.json`.

## Running the program

To run, use `flask run`. If everything is set up correctly, it **should** work.
