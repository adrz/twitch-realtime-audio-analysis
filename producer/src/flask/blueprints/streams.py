from flask import Blueprint
from flask import jsonify
from src.flask.services import streams


blueprint = Blueprint('streams', __name__)

@blueprint.route('/')
def list_all():
    return jsonify(streams.get_streamers())

@blueprint.route('/add/<name>')
def add_stream(name: str):
    streams.add_streamer(name)
    return jsonify({'added': name})

@blueprint.route('/del/<name>')
def rm_stream(name: str):
    streams.remove_streamer(name)
    return jsonify({'removed': name})
