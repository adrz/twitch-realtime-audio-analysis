from flask import Flask
from src.flask_blueprints import streams

app = Flask(__name__)
app.register_blueprint(streams.blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0')