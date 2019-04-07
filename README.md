# spotify-lyrics
Gets current track from Spotify, gets the lyrics from Genius and outputs to a Flask app.

## Dependencies
* [spotipy](https://github.com/plamere/spotipy) - Used for getting current song data from Spotify
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
* Navigate to the application directory ([whatever]/spotify-lyrics)
* Run the following commands to set up Flask:
```
export FLASK_APP="spogen"
export FLASK_ENV=development
```
* Set up the database with `flask init-db`

## Running the program
To run, use `flask run`. If everything is set up correctly, it **should** work.
