# -*- coding: utf8 -*-

# Copyright (C) 2014  Ben Ockmore

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api


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
    import wpws.track
    import wpws.recording
    import wpws.release
    import wpws.medium
    import wpws.artist_credit
    wpws.waveplot.create_api(api)
    wpws.track.create_api(api)
    wpws.recording.create_api(api)
    wpws.release.create_api(api)
    wpws.medium.create_api(api)
    wpws.artist_credit.create_api(api)

    return app
