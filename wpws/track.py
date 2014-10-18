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
from wpschema import Track, TrackRedirect, Recording, WavePlotContext

from wpws import db
from wpws.urls import recording_url, medium_url, artist_credit_url, track_url


class TrackResource(Resource):
    def get(self, gid):

        res = db.session.query(Track).filter_by(gid=gid).first()

        if res is None:
            res = db.session.query(TrackRedirect).filter_by(gid=gid).one()
            res = db.session.query(Track).filter_by(id=res.new_id).one()

        res = {
            'gid': str(res.gid),
            'position': res.position,
            'number': res.number,
            'name': res.name,
            'length': res.length,
            'last_updated': str(res.last_updated),
            'recording': recording_url(res.recording.gid),
            'medium': medium_url(res.medium.id),
            'artist_credit': artist_credit_url(res.artist_credit.id),
        }

        return res


class TrackListResource(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self, medium_id=None, waveplot_gid=None, recording_gid=None):
        args = self.get_parser.parse_args()

        results = db.session.query(Track).order_by('name')

        if medium_id is not None:
            results = results.filter_by(medium_id=medium_id)
        elif waveplot_gid is not None:
            results = db.session.query(Track).join(
                WavePlotContext,
                Track.gid == WavePlotContext.track_gid
            ).filter(WavePlotContext.waveplot_gid == waveplot_gid)
        elif recording_gid is not None:
            recording = db.session.query(Recording).filter_by(
                gid=recording_gid
            ).one()
            results = db.session.query(Track).filter_by(
                recording_id=recording.id
            )
        else:
            results = results.offset(args.offset).limit(args.limit)

        results = results.all()

        res = {
            'start': args.offset,
            'count': len(results),
            'objects': [
                {
                    'url': track_url(track.gid),
                    'gid': str(track.gid),
                    'position': track.position,
                    'number': track.number,
                    'name': track.name,
                    'length': track.length,
                    'last_updated': str(track.last_updated),
                    'recording': recording_url(track.recording.gid),
                    'medium': medium_url(track.medium.id),
                    'artist_credit': {
                        'url': artist_credit_url(track.artist_credit.id),
                        'name': track.artist_credit.name,
                    }
                }
                for track in results
            ],
        }

        return res


def create_api(api):
    api.add_resource(TrackResource, '/api/track/<string:gid>')
    api.add_resource(
        TrackListResource, '/api/track',
        '/api/medium/<int:medium_id>/tracks',
        '/api/waveplot/<string:waveplot_gid>/tracks',
        '/api/recording/<string:recording_gid>/tracks'
    )
