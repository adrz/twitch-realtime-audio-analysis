# -*- coding: utf-8 -*-

from flask import Flask
from src.api import api_blueprint


app = Flask(__name__)
app.register_blueprint(api_blueprint)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
