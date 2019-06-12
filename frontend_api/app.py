# -*- coding: utf-8 -*-

from flask import Flask
from flask_restplus import Api
from src.transcript import api as transcript_api
from werkzeug.contrib.fixers import ProxyFix
from flask_cors import CORS


api = Api(
    title='Api for transcript',
    version='1.0',
    description='Api to retrieve transcript data from twitch-streamer',
)

api.add_namespace(transcript_api)


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api.init_app(app)
CORS(app)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8283, debug=True)
