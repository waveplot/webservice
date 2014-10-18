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
from wpschema import Release, ReleaseRedirect, WavePlotContext

from wpws import db
from wpws.urls import artist_credit_url, release_url, medium_url


class ReleaseResource(Resource):
    def get(self, gid):

        res = db.session.query(Release).filter_by(gid=gid).first()

        if res is None:
            res = db.session.query(ReleaseRedirect).filter_by(gid=gid).one()
            res = db.session.query(Release).filter_by(id=res.new_id).one()

        res = {
            'gid': str(res.gid),
            'name': res.name,
            'status': None if res.status is None else res.status.name,
            'packaging': None if res.packaging is None else res.packaging.name,
            'language': None if res.language is None else res.language.name,
            'script': None if res.script is None else res.script.name,
            'barcode': res.barcode,
            'last_updated': str(res.last_updated),
            'artist_credit': artist_credit_url(res.artist_credit.id),
            'media': [
                medium_url(medium.id) for medium in res.media
            ]
        }

        return res


class ReleaseListResource(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self):
        args = self.get_parser.parse_args()

        contexts = db.session.query(WavePlotContext.release_gid)
        results = db.session.query(Release).order_by('name').filter(Release.gid.in_(contexts))
        results = results.offset(args.offset).limit(args.limit).all()

        res = {
            'start': args.offset,
            'count': len(results),
            'objects': [
                {
                    'url': release_url(rel.gid),
                    'gid': str(rel.gid),
                    'name': rel.name,
                    'status': None if rel.status is None else rel.status.name,
                    'packaging': (
                        None if rel.packaging is None else rel.packaging.name
                    ),
                    'language': (
                        None if rel.language is None else rel.language.name
                    ),
                    'script': (
                        None if rel.script is None else rel.script.name
                    ),
                    'barcode': rel.barcode,
                    'last_updated': str(rel.last_updated),
                    'artist_credit': {
                        'url': artist_credit_url(rel.artist_credit.id),
                        'name': rel.artist_credit.name,
                    }
                }
                for rel in results
            ],
        }

        return res


def create_api(api):
    api.add_resource(ReleaseResource, '/api/release/<string:gid>')
    api.add_resource(ReleaseListResource, '/api/release')
