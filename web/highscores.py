from flask import Flask
from jinja2 import Environment, PackageLoader, select_autoescape

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
#from mastermind
import high_score

app = Flask(__name__)
env = Environment(
    loader=PackageLoader('highscores', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('mastermind.html')

@app.route("/mastermind")
def mastermind():
  return template.render(highscores=high_score.get_print_high_scores())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
