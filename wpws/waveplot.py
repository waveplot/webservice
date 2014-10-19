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

import base64
import datetime
import uuid
import zlib

import sqlalchemy.orm.exc
from flask.ext.restful import Resource, reqparse, abort
import wpschema._waveplot
from wpschema import Editor, WavePlot, Edit, WavePlotContext

from wpws import db, VERSION
from wpws.urls import waveplot_url


def _get_unique_gid():
    generated_gid = uuid.uuid4()
    query = db.session.query(WavePlot)
    while query.filter_by(gid=generated_gid).first() is not None:
        generated_gid = uuid.uuid4()

    return generated_gid


def _create_edit(editor, waveplot):
    new_edit = Edit(
        time=datetime.datetime.utcnow().isoformat(),
        type=0,
        editor_id=editor.id,
        waveplot_gid=waveplot.gid,
    )

    db.session.add(new_edit)


class WavePlotResource(Resource):
    def get(self, gid):

        res = db.session.query(wpschema.WavePlot).filter_by(gid=gid).one()

        res = {
            'gid': str(res.gid),
            'duration': str(res.duration),
            'source_type': res.source_type,
            'sample_rate': res.sample_rate,
            'bit_depth': res.bit_depth,
            'bit_rate': res.bit_rate,
            'num_channels': res.num_channels,
            'dr_level': res.dr_level,
            'image_hash': base64.b64encode(res.image_hash),
            'full': base64.b64encode(res.full),
            'preview': base64.b64encode(res.preview),
            'thumbnail':  base64.b64encode(res.thumbnail),
            'sonic_hash': res.sonic_hash,
            'version': res.version,
        }

        return res


class WavePlotListResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self, track_gid=None, recording_gid=None, release_gid=None,
            artist_credit_id=None):
        args = self.get_parser.parse_args()

        results = db.session.query(wpschema.WavePlot).order_by('gid')
        if track_gid is not None:
            contexts = db.session.query(WavePlotContext).filter_by(
                track_gid=track_gid
            ).all()
            results = [context.waveplot for context in contexts]
        elif recording_gid is not None:
            contexts = db.session.query(WavePlotContext).filter_by(
                recording_gid=recording_gid).all()
            results = [context.waveplot for context in contexts]
        elif recording_gid is not None:
            contexts = db.session.query(WavePlotContext).filter_by(
                release_gid=release_gid
            ).all()
            results = [context.waveplot for context in contexts]
        elif recording_gid is not None:
            contexts = db.session.query(WavePlotContext).filter_by(
                artist_credit_id=artist_credit_id
            ).all()
            results = [context.waveplot for context in contexts]
        else:
            results = results.offset(args.offset).limit(args.limit).all()

        res = {
            'start': args.offset,
            'count': len(results),
            'objects': [
                {
                    'url': waveplot_url(wp.gid),
                    'gid': str(wp.gid),
                    'duration': str(wp.duration),
                    'source_type': wp.source_type,
                    'sample_rate': wp.sample_rate,
                    'bit_depth': wp.bit_depth,
                    'bit_rate': wp.bit_rate,
                    'num_channels': wp.num_channels,
                    'dr_level': wp.dr_level,
                    'image_hash': base64.b64encode(wp.image_hash),
                    'thumbnail':  base64.b64encode(wp.thumbnail),
                    'sonic_hash': wp.sonic_hash,
                    'version': wp.version,
                }
                for wp in results
            ],
        }

        return res

    post_parser = reqparse.RequestParser()
    post_parser.add_argument(
        'version', type=str, required=True, choices=[VERSION],
        help='WavePlot version mismatch. Please check client.'
    )
    post_parser.add_argument(
        'key', type=bytes, required=True,
        help=('Editor key must be supplied with all POST requests. '
              'Please check client.')
    )
    post_parser.add_argument('data', type=bytes, required=True,
                             help='WavePlot data missing from POST request.')
    post_parser.add_argument('duration', type=int, required=True,
                             help='Duration value missing from POST request.')
    post_parser.add_argument(
        'source_type', type=bytes, required=True,
        help='Source type value missing from POST request.'
    )
    post_parser.add_argument(
        'sample_rate', type=int, required=True,
        help='Sample rate value missing from POST request.'
    )
    post_parser.add_argument('bit_depth', type=int, required=True,
                             help='Bit depth value missing from POST request.')
    post_parser.add_argument('bit_rate', type=int, required=True,
                             help='Bit rate value missing from POST request.')
    post_parser.add_argument(
        'num_channels', type=int, required=True,
        help='Number of audio channels missing from POST request.'
    )
    post_parser.add_argument('dr_level', type=float, required=True,
                             help='DR value missing from POST request.')

    def post(self):
        args = self.post_parser.parse_args()

        editor = db.session.query(Editor)
        try:
            editor = editor.filter_by(key=args.key).one()
        except sqlalchemy.orm.exc.NoResultFound:
            abort(401, message='No such editor key.')

        if not editor.active:
            abort(401, message='Editor has not been activated.')

        wp = wpschema._waveplot.WavePlot()
        wp.full = zlib.decompress(base64.b64decode(args.data))

        image_hash = wp.get_image_hash().digest()

        existing = db.session.query(WavePlot)
        existing = existing.filter_by(image_hash=image_hash).first()
        if existing is not None:
            res = WavePlotResource()
            return res.get(existing.gid)

        wp.generate_preview()
        wp.generate_thumbnail()
        wp.generate_sonic_hash()

        new_wp = WavePlot(
            gid=_get_unique_gid(),
            duration=datetime.timedelta(seconds=args.duration),
            source_type=args.source_type,
            sample_rate=args.sample_rate,
            bit_depth=args.bit_depth,
            bit_rate=args.bit_rate,
            num_channels=args.num_channels,
            dr_level=int(args.dr_level * 10),
            image_hash=image_hash,
            full=wp.full,
            preview=wp.preview,
            thumbnail=wp.thumbnail,
            sonic_hash=wp.sonic_hash,
            version=args.version,
        )

        # Insert the WavePlot and associated edit into the DB
        db.session.add(new_wp)
        _create_edit(editor, new_wp)

        db.session.commit()

        res = WavePlotResource()
        return res.get(new_wp.gid)


def create_api(api):
    api.add_resource(WavePlotResource, '/api/waveplot/<string:gid>')
    api.add_resource(
        WavePlotListResource, '/api/waveplot',
        '/api/track/<string:track_gid>/waveplots',
        '/api/recording/<string:recording_gid>/waveplots',
        '/api/release/<string:release_gid>/waveplots',
        '/api/artist_credit/<string:artist_credit_id>/waveplots',
    )
