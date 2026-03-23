"""
    audioaddict.api
    Utility classes for accessing the AudioAddict API.
"""

import requests
from audioaddict.exceptions import ListenKeyError


class AudioAddictApi(object):
    def __init__(self, network_key):
        self._base_url = "api.audioaddict.com/v1/%s" % network_key

    def channels(self):
        r1 = requests.get("https://%s/channels" % self._base_url)
        r1.raise_for_status()

        r2 = requests.get("https://%s/listen/channels" % self._base_url)
        r2.raise_for_status()

        all_channels = r1.json()
        listen_channel_keys = [x.get('key') for x in r2.json() if x.get('key')]

        channels = []
        for channel in all_channels:
            key = channel.get('key')
            if key and key in listen_channel_keys:
                channels.append(Channel(channel))

        channels.sort(key=lambda c: c.name)
        return channels

    def channel_by_key(self, key):
        r = requests.get("https://%s/channels/key/%s" % (self._base_url, key))
        r.raise_for_status()

        return Channel(r.json())

    def playlist(self, stream_key, channel_key, listen_key):
        r = requests.get("https://%s/listen/%s/%s?listen_key=%s" %
                         (self._base_url, stream_key, channel_key, listen_key))

        if r.status_code == 403:
            raise ListenKeyError()
        else:
            r.raise_for_status()

        return r.json()


class Channel(object):
    def __init__(self, parsed_json):
        self._channel = parsed_json

    def image_default(self):
        images = self._channel.get('images')
        if not images:
            return ""

        default_image = images.get('default')
        if not default_image:
            return ""

        url = "https:%s" % default_image
        url = url.split('{')[0]

        return url

    @property
    def key(self):
        return self._channel.get('key', '')

    @property
    def name(self):
        return self._channel.get('name', 'Unknown')

    @property
    def creation_timestamp(self):
        return self._channel.get('created_at', '')
