__author__ = 'bromix'

from ...kodion.utils import FunctionCache


class ResourceManager(object):
    def __init__(self, context, youtube_client):
        self._context = context
        self._youtube_client = youtube_client
        self._channel_data = {}
        self._video_data = {}
        self._playlist_data = {}
        self._enable_channel_fanart = context.get_settings().get_bool('youtube.channel.fanart.show', True)

    def clear(self):
        self._context.get_function_cache().clear()

    def _get_channel_data(self, channel_id):
        return self._channel_data.get(channel_id, {})

    def _get_video_data(self, video_id):
        return self._video_data.get(video_id, {})

    def _get_playlist_data(self, playlist_id):
        return self._playlist_data.get(playlist_id, {})

    def _update_channels(self, channel_ids):
        result = {}
        json_data = {}

        channel_ids_to_update = []
        function_cache = self._context.get_function_cache()
        for channel_id in channel_ids:
            channel_data = function_cache.get_cached_only(self._get_channel_data, str(channel_id))
            if channel_data is None:
                self._context.log_debug("No data for channel '%s' cached" % channel_id)
                channel_ids_to_update.append(channel_id)
            else:
                self._context.log_debug("Found cached data for channel '%s'" % channel_id)
                result[channel_id] = channel_data

        if len(channel_ids_to_update) > 0:
            json_data = function_cache.get(FunctionCache.ONE_WEEK, self._youtube_client.get_channels, channel_ids_to_update)
            yt_items = json_data.get('items', [])
            for yt_item in yt_items:
                channel_id = str(yt_item['id'])
                self._channel_data[channel_id] = yt_item

                # this will cache the channel data
                result[channel_id] = function_cache.get(FunctionCache.ONE_WEEK, self._get_channel_data, channel_id)

        if self.handle_error(json_data):
            return result

        return result

    def _update_videos(self, video_ids):
        result = {}
        json_data = {}

        video_ids_to_update = []
        function_cache = self._context.get_function_cache()
        for video_id in video_ids:
            video_data = function_cache.get_cached_only(self._get_video_data, str(video_id))
            if video_data is None:
                self._context.log_debug("No data for video '%s' cached" % video_id)
                video_ids_to_update.append(video_id)
            else:
                self._context.log_debug("Found cached data for video '%s'" % video_id)
                result[video_id] = video_data

        if len(video_ids_to_update) > 0:
            json_data = function_cache.get(FunctionCache.ONE_MONTH, self._youtube_client.get_videos, video_ids_to_update)
            yt_items = json_data.get('items', [])
            for yt_item in yt_items:
                video_id = str(yt_item['id'])
                self._video_data[video_id] = yt_item

                # this will cache the channel data
                result[video_id] = function_cache.get(FunctionCache.ONE_MONTH, self._get_video_data, video_id)

        if self.handle_error(json_data):
            return result

    def _make_list_of_50(self, list_of_ids):
        list_of_50 = []
        pos = 0
        while pos < len(list_of_ids):
            list_of_50.append(list_of_ids[pos:pos + 50])
            pos += 50
        return list_of_50

    def get_videos(self, video_ids):
        list_of_50s = self._make_list_of_50(video_ids)

        result = {}
        for list_of_50 in list_of_50s:
            result.update(self._update_videos(list_of_50))
        return result

    def _update_playlists(self, playlists_ids):
        result = {}
        json_data = {}

        playlist_ids_to_update = []
        function_cache = self._context.get_function_cache()
        for playlist_id in playlists_ids:
            playlist_data = function_cache.get_cached_only(self._get_playlist_data, str(playlist_id))
            if playlist_data is None:
                self._context.log_debug("No data for playlist '%s' cached" % playlist_id)
                playlist_ids_to_update.append(playlist_id)
            else:
                self._context.log_debug("Found cached data for playlist '%s'" % playlist_id)
                result[playlist_id] = playlist_data

        if len(playlist_ids_to_update) > 0:
            json_data = function_cache.get(FunctionCache.ONE_DAY, self._youtube_client.get_playlists, playlist_ids_to_update)
            yt_items = json_data.get('items', [])
            for yt_item in yt_items:
                playlist_id = str(yt_item['id'])
                self._playlist_data[playlist_id] = yt_item

                # this will cache the channel data
                result[playlist_id] = function_cache.get(FunctionCache.ONE_DAY, self._get_playlist_data, playlist_id)

        if self.handle_error(json_data):
            return result

    def get_playlists(self, playlists_ids):
        list_of_50s = self._make_list_of_50(playlists_ids)

        result = {}
        for list_of_50 in list_of_50s:
            result.update(self._update_playlists(list_of_50))
        return result

    def get_related_playlists(self, channel_id):
        result = self._update_channels([channel_id])

        # transform
        item = None
        if channel_id != 'mine':
            item = result.get(channel_id, {})
        else:
            for key in result:
                item = result[key]
                break

        if item is None:
            return {}

        return item.get('contentDetails', {}).get('relatedPlaylists', {})

    def get_channels(self, channel_ids):
        list_of_50s = self._make_list_of_50(channel_ids)

        result = {}
        for list_of_50 in list_of_50s:
            result.update(self._update_channels(list_of_50))
        return result

    def get_fanarts(self, channel_ids):
        if not self._enable_channel_fanart:
            return {}

        result = self._update_channels(channel_ids)

        # transform
        for key in list(result.keys()):
            item = result[key]

            # set an empty url
            result[key] = u''
            images = item.get('brandingSettings', {}).get('image', {})
            banners = ['bannerTvMediumImageUrl', 'bannerTvLowImageUrl', 'bannerTvImageUrl']
            for banner in banners:
                image = images.get(banner, '')
                if image:
                    result[key] = image
                    break

        return result

    def handle_error(self, json_data):
        context = self._context
        if json_data and 'error' in json_data:
            message = json_data['error'].get('message', '')
            reason = json_data['error']['errors'][0].get('reason', '')
            title = '%s: %s' % (context.get_name(), reason)
            message_timeout = 5000
            if reason == 'quotaExceeded' or reason == 'dailyLimitExceeded':
                message_timeout = 7000
            context.get_ui().show_notification(message, title, time_milliseconds=message_timeout)
            error_message = 'Error reason: |%s| with message: |%s|' % (reason, message)
            raise Exception(error_message)

        return True
