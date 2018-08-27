#!/bin/bash
wget -N https://code.jquery.com/jquery-3.3.1.slim.js

python app.py
#gunicorn --workers 10 --bind 0.0.0.0:80 wsgi
