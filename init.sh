pip list | grep spotipy &> /dev/null
if [ $? != 0 ];
then
   git clone https://github.com/plamere/spotipy.git
   cd spotipy
   sudo python3 setup.py install
   cd ..
   rm -rf spotipy
fi

pip list | grep lyricsgenius &> /dev/null
if [ $? != 0 ];
then
   pip install lyricsgenius
fi

pip list | grep simplejson &> /dev/null
if [ $? != 0 ];
then
   pip install simplejson
fi

pip list | grep Flask &> /dev/null
if [ $? != 0 ];
then
   pip install simplejson
fi

export FLASK_APP=spogen
export FLASK_ENV=development
flask init-db
echo 'All done setting up! Now just use flask run.'