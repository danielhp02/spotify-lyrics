#!/bin/bash

export FLASK_APP=spogen
export FLASK_ENV=development
if [ ! -e instance/flaskr.sqlite ]
then
   flask init-db
fi
flask run
