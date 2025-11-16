from flask import Flask
from flask_frozen import Freezer

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello"

@app.route('/resource/test')
def resource():
    return "test"

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()