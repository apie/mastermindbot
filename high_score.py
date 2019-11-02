#!/usr/bin/env python3
import os
import datetime
from pydblite import Base

#db openen via losse functie
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def sort_high_scores(elem):
    return (int(elem['score']), elem['duration'], elem['date'])

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

def get_high_scores(user_id=None):
    print('get_high_scores')
    db = Base(os.path.join(SCRIPT_DIR, 'high_scores.db'))
    db.create('user_id', 'score', 'duration', 'date', mode="open")
    global_top = [
        {
            'user_id': r['user_id'],
            'user': get_user_name(r['user_id']),
            'date': r['date'].strftime('%d-%m-%Y'),
            'duration': str(r['duration']).split('.')[0],
            'score': r['score'],
        }
        for r in sorted([ r for r in db ], key=sort_high_scores)
    ]
    return {
        'my_top': [r for r in global_top if r['user_id'] == user_id][:5],
        'global_top': global_top[:5],
    }

def get_print_high_scores():
    return [
        '{user} {score:02} {duration} {date}'.format(
            user=r['user'],
            score=r['score'],
            date=r['date'].strftime('%d-%m-%Y'),
            duration=str(r['duration']).split('.')[0],
        )
        for r in get_high_scores()['global_top']
    ]

def print_high_scores():
    for score in get_print_high_scores():
      print(score)

if __name__ == '__main__':
    print_high_scores()

