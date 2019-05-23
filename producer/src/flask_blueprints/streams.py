from flask import Blueprint
from flask import jsonify

blueprint = Blueprint('streams', __name__)

@blueprint.route('/')
def list_all():
    return jsonify({})

@blueprint.route('/add/<name>')
def add_stream(name: str):
    return jsonify({'added': name})
