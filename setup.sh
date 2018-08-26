#!/bin/bash

python app.py
#gunicorn --workers 10 --bind 0.0.0.0:80 wsgi
