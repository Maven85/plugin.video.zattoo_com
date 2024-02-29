# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import xbmcaddon
import sys

addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
SESSION = addon.getSetting('session')
params = dict(part.split('=') for part in sys.argv[2][1:].split('&') if len(part.split('=')) == 2)
mode = params.get('mode', '')

if mode == 'watch':
    from resources.lib.functions import get_kodi_version
    from resources.lib.watch import get_stream_url
    import xbmcplugin
    import xbmcgui
    stream = get_stream_url(params.get('id', ''), params['level'], params['drm'], SESSION)
    listitem = xbmcgui.ListItem(path=stream['url'])
    if addon.getSetting('streaming_protocoll').lower() in ['dash', 'dash_widevine']:
        listitem.setContentLookup(False)
        listitem.setMimeType('application/dash+xml')
        listitem.setProperty('inputstream', 'inputstream.adaptive')
        if stream.get('license_url'):
            listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            listitem.setProperty('inputstream.adaptive.license_key', '%s||R{SSM}|' % (stream['license_url']))

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
elif mode == 'epg':
    from resources.lib.epg import list_epg_item
    pid = params.get('id', '')
    pg_hash = addon.getSetting('pg_hash')
    list_epg_item(pid, SESSION, pg_hash)
else:
    from resources.lib.channels import list_channels
    USE_FANARTS = addon.getSetting('showFanart') == 'true'
    pg_hash = addon.getSetting('pg_hash')
    list_channels(SESSION, pg_hash, USE_FANARTS)
