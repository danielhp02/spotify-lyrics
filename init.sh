#!/bin/bash

export FLASK_APP=spogen
export FLASK_ENV=development
export FLASK_DEBUG=0
if [ ! -e instance/flaskr.sqlite ]
then
   flask init-db
fi
flask run --host=0.0.0.0
