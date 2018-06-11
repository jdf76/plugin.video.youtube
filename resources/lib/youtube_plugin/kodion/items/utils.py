# coding=utf-8
__author__ = 'bromix'

from six import string_types

import json
import datetime
import time

from .video_item import VideoItem
from .directory_item import DirectoryItem
from .audio_item import AudioItem
from .image_item import ImageItem


def from_json(json_data):
    """
    Creates a instance of the given json dump or dict.
    :param json_data:
    :return:
    """

    def _from_json(_json_data):
        mapping = {'VideoItem': lambda: VideoItem(u'', u''),
                   'DirectoryItem': lambda: DirectoryItem(u'', u''),
                   'AudioItem': lambda: AudioItem(u'', u''),
                   'ImageItem': lambda: ImageItem(u'', u'')}

        item = None
        item_type = _json_data.get('type', None)
        for key in mapping:
            if item_type == key:
                item = mapping[key]()
                break

        if item is None:
            return _json_data

        data = _json_data.get('data', {})
        for key in data:
            if hasattr(item, key):
                setattr(item, key, data[key])

        return item

    if isinstance(json_data, string_types):
        json_data = json.loads(json_data)
    return _from_json(json_data)


def to_jsons(base_item):
    return json.dumps(to_json(base_item))


def to_json(base_item):
    """
    Convert the given @base_item to json
    :param base_item:
    :return: json string
    """

    def _to_json(obj):
        if isinstance(obj, dict):
            return obj.__dict__

        mapping = {VideoItem: 'VideoItem',
                   DirectoryItem: 'DirectoryItem',
                   AudioItem: 'AudioItem',
                   ImageItem: 'ImageItem'}

        for key in mapping:
            if isinstance(obj, key):
                return {'type': mapping[key], 'data': obj.__dict__}

        return obj.__dict__

    return _to_json(base_item)


def utc_to_local(dt):
    now = time.time()
    offset = datetime.datetime.fromtimestamp(now) - datetime.datetime.utcfromtimestamp(now)
    return dt + offset


def datetime_to_since(dt, context):
    now = datetime.datetime.now()
    diff = now - dt
    yesterday = now - datetime.timedelta(days=1)
    yyesterday = now - datetime.timedelta(days=2)
    use_yesterday = (now - yesterday).total_seconds() > 10800
    seconds = diff.total_seconds()

    if seconds > 0:
        if seconds < 60:
            return context.localize("30676")
        elif 60 <= seconds < 120:
            return context.localize("30677")
        elif 120 <= seconds < 3600:
            return context.localize("30678")
        elif 3600 <= seconds < 7200:
            return context.localize("30679")
        elif 7200 <= seconds < 10800:
            return context.localize("30680")
        elif 10800 <= seconds < 14400:
            return context.localize("30681")
        elif use_yesterday and dt.date() == yesterday.date():
            return u" ".join([context.localize("30682"), context.format_time(dt)])
        elif dt.date() == yyesterday.date():
            return context.localize("30683")
        elif 5400 <= seconds < 86400:
            return u" ".join([context.localize("30684"), context.format_time(dt)])
        elif 86400 <= seconds < 172800:
            return u" ".join([context.localize("30682"), context.format_time(dt)])
    return " ".join([context.format_date_short(dt), context.format_time(dt)])
