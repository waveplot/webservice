
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api

import wpschema
import base64

VERSION = b'DAMSON'

db = SQLAlchemy()


def add_cors_header(response):
    # https://github.com/jfinkels/flask-restless/issues/223
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = \
        'HEAD, GET, POST, PATCH, PUT, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, X-Requested-With, Content-Type, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response


def create_app(config):
    app = Flask(__name__)
    app.config.update(config)
    app.after_request(add_cors_header)

    db.app = app
    db.init_app(app)

    # Test API for Tracks
    api = Api(app)

    import wpws.waveplot
    wpws.waveplot.create_api(api)

    return app
