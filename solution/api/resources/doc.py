from flask import send_file
from flask_restful import Resource


class DocResource(Resource):
    def get(self):
        return send_file('docs/openapi.yaml', mimetype='text/yaml')