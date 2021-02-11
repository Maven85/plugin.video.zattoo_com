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


def get_stream_url(cid, SESSION):
    from .api import get_json_data
    try:
        json_data = get_json_data('https://zattoo.com/zapi/watch/live/%s' % cid, SESSION, {'stream_type':'hls7', 'https_watch_urls':True})
    except HTTPError:
        from .api import login
        login()
        import xbmcaddon
        addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
        SESSION = addon.getSetting('session')
        json_data = get_json_data('https://zattoo.com/zapi/watch/live/%s' % cid, SESSION, {'stream_type':'hls7', 'https_watch_urls':True})
    return json.loads(json_data)['stream']['url']