import hashlib
import time

from .. import constants
from ..json_store import LoginTokenStore

__author__ = 'bromix'


class AccessManager(object):
    def __init__(self, context):
        self._settings = context.get_settings()
        self.jstore = LoginTokenStore(context)
        self.json = self.jstore.load()
        self.sync_tokens()

    def has_login_credentials(self):
        """
        Returns True if we have a username and password.
        :return: True if username and password exists
        """
        username = self._settings.get_string(constants.setting.LOGIN_USERNAME, '')
        password = self._settings.get_string(constants.setting.LOGIN_PASSWORD, '')
        return username != '' and password != ''

    def remove_login_credentials(self):
        self._settings.set_string(constants.setting.LOGIN_USERNAME, '')
        self._settings.set_string(constants.setting.LOGIN_PASSWORD, '')

    def get_login_credentials(self):
        """
        Returns the username and password (Tuple)
        :return: (username, password)
        """
        username = self._settings.get_string(constants.setting.LOGIN_USERNAME, '')
        password = self._settings.get_string(constants.setting.LOGIN_PASSWORD, '')
        return username, password

    def is_new_login_credential(self, update_hash=True):
        """
        Returns True if username or/and password are new.
        :return:
        """
        username = self._settings.get_string(constants.setting.LOGIN_USERNAME, '')
        password = self._settings.get_string(constants.setting.LOGIN_PASSWORD, '')

        m = hashlib.md5()
        m.update(username.encode('utf-8') + password.encode('utf-8'))
        current_hash = m.hexdigest()
        old_hash = self._settings.get_string(constants.setting.LOGIN_HASH, '')
        if current_hash != old_hash:
            if update_hash:
                self._settings.set_string(constants.setting.LOGIN_HASH, current_hash)
            return True

        return False

    def sync_tokens(self):
        access_token = self._settings.get_string(constants.setting.ACCESS_TOKEN, '')
        refresh_token = self._settings.get_string(constants.setting.REFRESH_TOKEN, '')
        token_expires = self._settings.get_int(constants.setting.ACCESS_TOKEN_EXPIRES, -1)
        json_access_token = self.json['access_manager'].get('access_token', '')
        json_refresh_token = self.json['access_manager'].get('refresh_token', '')
        json_token_expires = self.json['access_manager'].get('token_expires', -1)
        if not access_token or not refresh_token:
            if json_access_token and json_token_expires and json_refresh_token:
                self.update_access_token(json_access_token, json_token_expires, json_refresh_token)
        else:
            if not json_access_token or not json_token_expires or not json_refresh_token:
                self.update_access_token(access_token, token_expires, refresh_token)

    def get_access_token(self):
        """
        Returns the access token for some API
        :return: access_token
        """
        return self._settings.get_string(constants.setting.ACCESS_TOKEN, '')

    def get_refresh_token(self):
        """
        Returns the refresh token
        :return: refresh token
        """
        return self._settings.get_string(constants.setting.REFRESH_TOKEN, '')

    def has_refresh_token(self):
        return self.get_refresh_token() != ''

    def is_access_token_expired(self):
        """
        Returns True if the access_token is expired otherwise False.
        If no expiration date was provided and an access_token exists
        this method will always return True
        :return:
        """

        # with no access_token it must be expired
        if not self._settings.get_string(constants.setting.ACCESS_TOKEN, ''):
            return True

        # in this case no expiration date was set
        expires = self._settings.get_int(constants.setting.ACCESS_TOKEN_EXPIRES, -1)
        if expires == -1:
            return False

        now = int(time.time())
        return expires <= now

    def update_access_token(self, access_token, unix_timestamp=None, refresh_token=None):
        """
        Updates the old access token with the new one.
        :param access_token:
        :return:
        """
        self.json['access_manager']['access_token'] = access_token
        self._settings.set_string(constants.setting.ACCESS_TOKEN, access_token)
        if unix_timestamp is not None:
            self.json['access_manager']['token_expires'] = int(unix_timestamp)
            self._settings.set_int(constants.setting.ACCESS_TOKEN_EXPIRES, int(unix_timestamp))

        if refresh_token is not None:
            self.json['access_manager']['refresh_token'] = refresh_token
            self._settings.set_string(constants.setting.REFRESH_TOKEN, refresh_token)

        self.jstore.save(self.json)
