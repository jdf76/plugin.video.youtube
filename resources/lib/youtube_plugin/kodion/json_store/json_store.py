# -*- coding: utf-8 -*-
"""
    Modified: Feb. 06, 2018 plugin.video.youtube

    Copyright (C) 2016 Twitch-on-Kodi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import json
from copy import deepcopy

import xbmcaddon
import xbmcvfs
import xbmc

from .. import logger


class JSONStore(object):
    def __init__(self, filename):
        addon_id = 'plugin.video.youtube'
        addon = xbmcaddon.Addon(addon_id)

        try:
            self.base_path = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
        except AttributeError:
            self.base_path = xbmc.translatePath(addon.getAddonInfo('profile'))

        self.filename = os.path.join(self.base_path, filename)

        self._data = None
        self.load()
        self.set_defaults()

    def set_defaults(self):
        raise NotImplementedError

    def save(self, data):
        if data != self._data:
            self._data = deepcopy(data)
            if not xbmcvfs.exists(self.base_path):
                if not self.make_dirs(self.base_path):
                    logger.log_debug('JSONStore Save |{filename}| failed to create directories.'.format(filename=self.filename.encode("utf-8")))
                    return
            with open(self.filename, 'w') as jsonfile:
                logger.log_debug('JSONStore Save |{filename}|'.format(filename=self.filename.encode("utf-8")))
                json.dump(self._data, jsonfile, indent=4, sort_keys=True)

    def load(self):
        if xbmcvfs.exists(self.filename):
            with open(self.filename, 'r') as jsonfile:
                data = json.load(jsonfile)
                self._data = data
                logger.log_debug('JSONStore Load |{filename}|'.format(filename=self.filename.encode("utf-8")))
        else:
            self._data = dict()

    def get_data(self):
        return deepcopy(self._data)

    def make_dirs(self, path):
        if not path.endswith('/'):
            path = ''.join([path, '/'])
        path = xbmc.translatePath(path)
        if not xbmcvfs.exists(path):
            try:
                r = xbmcvfs.mkdirs(path)
            except:
                pass
            if not xbmcvfs.exists(path):
                try:
                    os.makedirs(path)
                except:
                    pass
            return xbmcvfs.exists(path)

        return True
