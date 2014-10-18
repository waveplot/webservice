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

from flask.ext.restful import Resource, reqparse
from wpschema import Recording, RecordingRedirect

from wpws import db
from wpws.urls import recording_url, artist_credit_url


class RecordingResource(Resource):
    def get(self, gid):

        res = db.session.query(Recording).filter_by(gid=gid).first()

        if res is None:
            res = db.session.query(RecordingRedirect).filter_by(gid=gid).one()
            res = db.session.query(Recording).filter_by(id=res.new_id).one()

        res = {
            'gid': str(res.gid),
            'name': res.name,
            'length': res.length,
            'last_updated': str(res.last_updated),
            'video': res.video,
            'artist_credit': artist_credit_url(res.artist_credit.id),
        }

        return res


class RecordingListResource(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self):
        args = self.get_parser.parse_args()

        results = db.session.query(Recording).order_by('name')
        results = results.offset(args.offset).limit(args.limit).all()

        res = {
            'start': args.offset,
            'count': len(results),
            'objects': [
                {
                    'url': recording_url(rec.gid),
                    'gid': str(rec.gid),
                    'name': rec.name,
                    'length': rec.length,
                    'last_updated': str(rec.last_updated),
                    'video': rec.video,
                    'artist_credit': {
                        'url': artist_credit_url(rec.artist_credit.id),
                        'name': rec.artist_credit.name,
                    }
                }
                for rec in results
            ],
        }

        return res


def create_api(api):
    api.add_resource(RecordingResource, '/api/recording/<string:gid>')
    api.add_resource(RecordingListResource, '/api/recording')
