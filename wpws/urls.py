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

from wpws.config import SERVER


def recording_url(gid):
    return SERVER + '/api/recording/{}'.format(gid)


def release_url(gid):
    return SERVER + '/api/release/{}'.format(gid)


def medium_url(_id):
    return SERVER + '/api/medium/{}'.format(_id)


def artist_credit_url(_id):
    return SERVER + '/api/artist_credit/{}'.format(_id)


def track_url(gid):
    return SERVER + '/api/track/{}'.format(gid)


def waveplot_url(gid):
    return SERVER + '/api/waveplot/{}'.format(gid)
