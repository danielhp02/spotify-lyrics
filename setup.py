from setuptools import find_packages, setup

setup(  name='spotify-lyrics',
        version='0.1',
        description='',
        author='Daniel H-P and Mitch H',
        url='https://github.com/danielhp02/spotify-lyrics/',
        packages=find_packages(),
        install_requires=['spotipy', 'lyricsgenius', 'flask', 'simplejson'])