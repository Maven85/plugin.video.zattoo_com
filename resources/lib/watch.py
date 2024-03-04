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


def get_stream(cid, level, drm, SESSION):
    from .api import get_json_data
    import xbmcaddon
    data = {'https_watch_urls': True}
    addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
    streaming_protocol = addon.getSetting('streaming_protocol').lower()
    if streaming_protocol in ['dash', 'dash_widevine']:
        data['timeshift'] = 10800
        if streaming_protocol == 'dash' or level == 'sd' or drm == 'False':
            streaming_protocol = 'dash'
        else:
            streaming_protocol = 'dash_widevine'
            data['max_drm_lvl'] = addon.getSetting('drm_lvl')
            data['max_hdcp_type'] = 1 if addon.getSetting('hdcp_type') == '0' else 'Unprotected'
    else:
        streaming_protocol = 'hls7'
    data['stream_type'] = streaming_protocol
    try:
        json_data = get_json_data('https://zattoo.com/zapi/watch/live/%s' % cid, SESSION, data)
    except HTTPError:
        from .api import login
        login()
        SESSION = addon.getSetting('session')
        json_data = get_json_data('https://zattoo.com/zapi/watch/live/%s' % cid, SESSION, data)
    return json.loads(json_data)['stream']
