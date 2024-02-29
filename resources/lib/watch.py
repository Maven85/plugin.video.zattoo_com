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


def get_stream_url(cid, level, drm, SESSION):
    from .api import get_json_data
    from .functions import get_kodi_version
    import xbmcaddon
    data = {'https_watch_urls': True}
    addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
    streaming_protocoll = addon.getSetting('streaming_protocoll').lower()
    if streaming_protocoll in ['dash', 'dash_widevine']:
        data['timeshift'] = 10800
        if streaming_protocoll == 'dash' or level == 'sd' or drm == 'False':
            streaming_protocoll = 'dash'
        else:
            streaming_protocoll = 'dash_widevine'
    else:
        streaming_protocoll = 'hls7'
    data['stream_type'] = streaming_protocoll
    try:
        json_data = get_json_data('https://zattoo.com/zapi/watch/live/%s' % cid, SESSION, data)
    except HTTPError:
        from .api import login
        login()
        SESSION = addon.getSetting('session')
        json_data = get_json_data('https://zattoo.com/zapi/watch/live/%s' % cid, SESSION, data)
    return json.loads(json_data)['stream']
