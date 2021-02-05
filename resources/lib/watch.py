# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

try:
    from urllib.error import HTTPError
    from urllib.parse import urljoin
    from urllib.request import urlopen
except:
    from urllib2 import urlopen, HTTPError
    from urlparse import urljoin


def get_playlist_url(cid, SESSION):
    from .api import get_json_data
    try:
        json_data = get_json_data('https://zattoo.com/zapi/watch/live/%s' % cid, SESSION, {'stream_type':'hls', 'https_watch_urls':True})
    except HTTPError:
        from .api import login
        login()
        import xbmcaddon
        addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
        SESSION = addon.getSetting('session')
        json_data = get_json_data('https://zattoo.com/zapi/watch/live/%s' % cid, SESSION, {'stream_type':'hls', 'https_watch_urls':True})
    return json.loads(json_data)['stream']['url']


def get_stream_url(cid, SESSION, MAX_BITRATE):
    playlist_url = get_playlist_url(cid, SESSION)
    m3u8_data = urlopen(playlist_url).read().decode('utf-8')
    url_parts = [line for line in m3u8_data.split('\n') if '.m3u8' in line]
    prefix_url = urljoin(playlist_url, '/')
    if MAX_BITRATE == '3000000':
        suffix_url = url_parts[0]
    elif MAX_BITRATE == '1500000':
        if len(url_parts) == 4:
            suffix_url = url_parts[1]
        else:
            suffix_url = url_parts[0]
    elif MAX_BITRATE == '900000':
        if len(url_parts) == 4:
            suffix_url = url_parts[2]
        else:
            suffix_url = url_parts[1]
    else:
        suffix_url = url_parts[-1]
    return prefix_url + suffix_url