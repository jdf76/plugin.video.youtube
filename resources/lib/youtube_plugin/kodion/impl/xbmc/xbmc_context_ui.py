__author__ = 'bromix'

from six import string_types

import xbmc
import xbmcgui

from ..abstract_context_ui import AbstractContextUI
from .xbmc_progress_dialog import XbmcProgressDialog
from .xbmc_progress_dialog_bg import XbmcProgressDialogBG
from ... import constants
from ... import utils


class XbmcContextUI(AbstractContextUI):
    def __init__(self, xbmc_addon, context):
        AbstractContextUI.__init__(self)

        self._xbmc_addon = xbmc_addon

        self._context = context
        self._view_mode = None

    def create_progress_dialog(self, heading, text=None, background=False):
        if background and self._context.get_system_version().get_version() > (12, 3):
            return XbmcProgressDialogBG(heading, text)

        return XbmcProgressDialog(heading, text)

    def set_view_mode(self, view_mode):
        if isinstance(view_mode, string_types):
            view_mode = self._context.get_settings().get_int(constants.setting.VIEW_X % view_mode, 50)

        self._view_mode = view_mode

    def get_view_mode(self):
        if self._view_mode is not None:
            return self._view_mode

        return self._context.get_settings().get_int(constants.setting.VIEW_DEFAULT, 50)

    def get_skin_id(self):
        return xbmc.getSkinDir()

    def on_keyboard_input(self, title, default='', hidden=False):
        # fallback for Frodo
        if self._context.get_system_version().get_version() <= (12, 3):
            keyboard = xbmc.Keyboard(default, title, hidden)
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                text = utils.to_unicode(keyboard.getText())
                return True, text
            else:
                return False, u''

        # Starting with Gotham (13.X > ...)
        dialog = xbmcgui.Dialog()
        result = dialog.input(title, utils.to_unicode(default), type=xbmcgui.INPUT_ALPHANUM)
        if result:
            text = utils.to_unicode(result)
            return True, text

        return False, u''

    def on_numeric_input(self, title, default=''):
        dialog = xbmcgui.Dialog()
        result = dialog.input(title, str(default), type=xbmcgui.INPUT_NUMERIC)
        if result:
            return True, int(result)

        return False, None

    def on_yes_no_input(self, title, text, nolabel='', yeslabel=''):
        dialog = xbmcgui.Dialog()
        return dialog.yesno(title, text, nolabel=nolabel, yeslabel=yeslabel)

    def on_ok(self, title, text):
        dialog = xbmcgui.Dialog()
        return dialog.ok(title, text)

    def on_remove_content(self, content_name):
        text = self._context.localize(constants.localize.REMOVE_CONTENT) % utils.to_unicode(content_name)
        return self.on_yes_no_input(self._context.localize(constants.localize.CONFIRM_REMOVE), text)

    def on_delete_content(self, content_name):
        text = self._context.localize(constants.localize.DELETE_CONTENT) % utils.to_unicode(content_name)
        return self.on_yes_no_input(self._context.localize(constants.localize.CONFIRM_DELETE), text)

    def on_select(self, title, items=[]):
        _dict = {}
        _items = []
        i = 0
        for item in items:
            if isinstance(item, tuple):
                _dict[i] = item[1]
                _items.append(item[0])
            else:
                _dict[i] = i
                _items.append(item)

            i += 1

        dialog = xbmcgui.Dialog()
        result = dialog.select(title, _items)
        return _dict.get(result, -1)

    def show_notification(self, message, header='', image_uri='', time_milliseconds=5000):
        _header = header
        if not _header:
            _header = self._context.get_name()
        _header = utils.to_unicode(_header)

        _image = image_uri
        if not _image:
            _image = self._context.get_icon()

        _message = utils.to_unicode(message)
        _message = _message.replace(',', ' ')
        _message = _message.replace('\n', ' ')

        xbmc.executebuiltin(
            "Notification(%s, %s, %d, %s)" % (_header, _message, time_milliseconds, _image))

    def open_settings(self):
        self._xbmc_addon.openSettings()

    def refresh_container(self):
        xbmc.executebuiltin("Container.Refresh")

    @staticmethod
    def set_home_window_property(property_id, value):
        property_id = 'plugin.video.youtube-' + property_id
        xbmcgui.Window(10000).setProperty(property_id, value)

    @staticmethod
    def get_home_window_property(property_id):
        property_id = 'plugin.video.youtube-' + property_id
        return xbmcgui.Window(10000).getProperty(property_id) or None

    @staticmethod
    def clear_home_window_property(property_id):
        property_id = 'plugin.video.youtube-' + property_id
        xbmcgui.Window(10000).clearProperty(property_id)
