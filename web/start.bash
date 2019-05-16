#!/bin/bash
source venv/bin/activate
pip3 install -r setup/requirements.txt
gunicorn highscores:app --reload

