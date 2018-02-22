#!/usr/bin/env python3
import os
import datetime
from pydblite import Base

#db openen via losse functie
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def sort_high_scores(elem):
    #TODO evt ook nog duration meenemen.
    return (int(elem['score']), elem['date'])

def update_user_table(user_id, first_name):
    db = Base(os.path.join(SCRIPT_DIR, 'users.db'))
    db.create('user_id', 'first_name', mode="open")
    if ((len(db(user_id=user_id)) == 0) or (len(db(user_id=user_id, first_name=first_name)) == 0)):
        db.insert(user_id=user_id,
                  first_name=first_name)
        db.commit()

def get_user_name(user_id):
    db = Base(os.path.join(SCRIPT_DIR, 'users.db'))
    db.create('user_id', 'first_name', mode="open")
    user = db(user_id=user_id)
    if not user:
        return None
    user = user.pop()
    return user['first_name']

def set_high_score(first_name, user_id, rounds, duration):
    rounds = int(rounds)
    print('h.set_high_score')
    print(first_name, user_id, rounds, duration)
    update_user_table(user_id, first_name)
    db = Base(os.path.join(SCRIPT_DIR, 'high_scores.db'))
    db.create('user_id', 'score', 'duration', 'date', mode="open")
    db.insert(user_id=user_id,
	      score=rounds,
	      duration=duration,
	      date=datetime.datetime.now())
    db.commit()

def get_high_scores(user_id):
    print('get_high_scores')
    db = Base(os.path.join(SCRIPT_DIR, 'high_scores.db'))
    db.create('user_id', 'score', 'duration', 'date', mode="open")
    my_top = []
    for r in sorted([r for r in db if r['user_id'] == user_id ], key=sort_high_scores):
        my_top.append({
            'date': r['date'].strftime('%d-%m-%Y'),
            'score': r['score'],
        })
    global_top = []
    for r in sorted([ r for r in db ], key=sort_high_scores):
        global_top.append({
            'user': get_user_name(r['user_id']),
            'score': r['score'],
        })
    return {
    	'my_top': my_top,
	'global_top': global_top,
    }

