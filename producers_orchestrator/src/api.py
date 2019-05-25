# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import jsonify
from .orchestrator import ProducersOrchestrator


api_blueprint = Blueprint('streams', __name__)
orchestrator = ProducersOrchestrator()


@api_blueprint.route('/get_streams')
def list_all():
    return jsonify(orchestrator.get_streamers())


# TODO check error send code 200, or...
@api_blueprint.route('/add/<name>')
def add_stream(name: str):
    orchestrator.add(name)
    return jsonify({'added': name})


@api_blueprint.route('/del/<name>')
def rm_stream(name: str):
    orchestrator.delete(name)
    return jsonify({'removed': name})
