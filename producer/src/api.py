# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import jsonify
from .audiostreamers_manager import AudioStreamersManager


api_blueprint = Blueprint('streams', __name__)
manager = AudioStreamersManager()


@api_blueprint.route('/get_streams')
def list_all():
    return jsonify(manager.get_streamers())


# TODO check error send code 200, or...
@api_blueprint.route('/add/<name>')
def add_stream(name: str):
    manager.add_streamer(name)
    return jsonify({'added': name})


@api_blueprint.route('/del/<name>')
def rm_stream(name: str):
    manager.remove_streamer(name)
    return jsonify({'removed': name})
