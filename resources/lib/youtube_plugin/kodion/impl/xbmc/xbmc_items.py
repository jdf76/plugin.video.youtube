# -*- coding: utf-8 -*-

__author__ = 'bromix'

import xbmcgui

from ...items import VideoItem, AudioItem, UriItem
from ... import utils
from . import info_labels


def to_video_item(context, video_item):
    context.log_debug('Converting VideoItem |%s|' % video_item.get_uri())
    major_version = context.get_system_version().get_version()[0]
    thumb = video_item.get_image() if video_item.get_image() else u'DefaultVideo.png'
    title = video_item.get_title() if video_item.get_title() else video_item.get_name()
    fanart = ''
    settings = context.get_settings()
    if major_version > 17:
        item = xbmcgui.ListItem(label=utils.to_unicode(title), offscreen=True)
    else:
        item = xbmcgui.ListItem(label=utils.to_unicode(title))
    if video_item.get_fanart() and settings.show_fanart():
        fanart = video_item.get_fanart()
    if major_version <= 12:
        item.setIconImage(thumb)
        item.setProperty("Fanart_Image", fanart)
    elif major_version <= 15:
        item.setArt({'thumb': thumb, 'fanart': fanart})
        item.setIconImage(thumb)
    else:
        item.setArt({'icon': thumb, 'thumb': thumb, 'fanart': fanart})

    if video_item.get_context_menu() is not None:
        item.addContextMenuItems(video_item.get_context_menu(), replaceItems=video_item.replace_context_menu())

    item.setProperty('inputstreamaddon', '')
    item.setProperty('inputstream.adaptive.manifest_type', '')
    if video_item.use_dash() and context.addon_enabled('inputstream.adaptive'):
        item.setContentLookup(False)
        item.setMimeType('application/xml+dash')
        item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        if video_item.get_headers():
            item.setProperty('inputstream.adaptive.stream_headers', video_item.get_headers())

        if video_item.get_license_key():
            item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            item.setProperty('inputstream.adaptive.license_key', video_item.get_license_key())

        # item.setProperty('inputstream.adaptive.manifest_update_parameter', '&start_seq=$START_NUMBER$')

    item.setProperty(u'IsPlayable', u'true')

    if video_item.subtitles:
        item.setSubtitles(video_item.subtitles)

    _info_labels = info_labels.create_from_item(context, video_item)

    # This should work for all versions of XBMC/KODI.
    if 'duration' in _info_labels:
        duration = _info_labels['duration']
        del _info_labels['duration']
        item.addStreamInfo('video', {'duration': duration})

    item.setInfo(type=u'video', infoLabels=_info_labels)
    return item


def to_audio_item(context, audio_item):
    context.log_debug('Converting AudioItem |%s|' % audio_item.get_uri())
    major_version = context.get_system_version().get_version()[0]
    thumb = audio_item.get_image() if audio_item.get_image() else u'DefaultAudio.png'
    title = audio_item.get_name()
    fanart = ''
    settings = context.get_settings()
    if major_version > 17:
        item = xbmcgui.ListItem(label=utils.to_unicode(title), offscreen=True)
    else:
        item = xbmcgui.ListItem(label=utils.to_unicode(title))
    if audio_item.get_fanart() and settings.show_fanart():
        fanart = audio_item.get_fanart()
    if major_version <= 12:
        item.setIconImage(thumb)
        item.setProperty("Fanart_Image", fanart)
    elif major_version <= 15:
        item.setArt({'thumb': thumb, 'fanart': fanart})
        item.setIconImage(thumb)
    else:
        item.setArt({'icon': thumb, 'thumb': thumb, 'fanart': fanart})

    if audio_item.get_context_menu() is not None:
        item.addContextMenuItems(audio_item.get_context_menu(), replaceItems=audio_item.replace_context_menu())

    item.setProperty(u'IsPlayable', u'true')

    item.setInfo(type=u'music', infoLabels=info_labels.create_from_item(context, audio_item))
    return item


def to_uri_item(context, base_item):
    context.log_debug('Converting UriItem')
    major_version = context.get_system_version().get_version()[0]
    if major_version > 17:
        item = xbmcgui.ListItem(path=base_item.get_uri(), offscreen=True)
    else:
        item = xbmcgui.ListItem(path=base_item.get_uri())
    item.setProperty(u'IsPlayable', u'true')
    return item


def to_item(context, base_item):
    if isinstance(base_item, UriItem):
        return to_uri_item(context, base_item)

    if isinstance(base_item, VideoItem):
        return to_video_item(context, base_item)

    if isinstance(base_item, AudioItem):
        return to_audio_item(context, base_item)

    return None
