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
from wpschema import Medium, Release

from wpws import db
from wpws.urls import release_url, medium_url


class MediumResource(Resource):
    def get(self, _id):

        res = db.session.query(Medium).filter_by(id=_id).first()

        res = {
            'id': res.id,
            'position': res.position,
            'format': res.format,
            'name': res.name,
            'last_updated': str(res.last_updated),
            'track_count': res.track_count,
            'release': release_url(res.release.gid)
        }

        return res


class MediumListResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self, release_gid=None):
        args = self.get_parser.parse_args()

        results = db.session.query(Medium)

        if release_gid is not None:
            release = db.session.query(Release).filter_by(
                gid=release_gid
            ).one()
            results = results.order_by('position').filter_by(release_id=release.id)
        else:
            results = results.order_by('id').offset(args.offset).limit(args.limit)

        results = results.all()

        res = {
            'start': args.offset,
            'count': len(results),
            'objects': [
                {
                    'url': medium_url(medium.id),
                    'id': medium.id,
                    'position': medium.position,
                    'format': medium.format,
                    'name': medium.name,
                    'last_updated': str(medium.last_updated),
                    'track_count': medium.track_count,
                    'release': release_url(medium.release.gid)
                }
                for medium in results
            ]
        }

        return res


def create_api(api):
    api.add_resource(MediumResource, '/api/medium/<int:_id>')
    api.add_resource(MediumListResource,
                     '/api/release/<string:release_gid>/media')
