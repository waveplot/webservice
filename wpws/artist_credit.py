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

from flask.ext.restful import Resource
import wpschema

from wpws import db


class ArtistCreditResource(Resource):

    def get(self, _id):

        res = db.session.query(wpschema.ArtistCredit).filter_by(id=_id).first()

        res = {
            'id': res.id,
            'name': res.name,
            'credit': str(res.created),
        }

        return res


def create_api(api):
    api.add_resource(ArtistCreditResource, '/api/artist_credit/<int:_id>')
