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
    cid = params.get('id', '')
    stream_url = get_stream_url(cid, SESSION)
    listitem = xbmcgui.ListItem(path=stream_url)
    if get_kodi_version() >= 21:
        listitem.setContentLookup(False)
        listitem.setMimeType('application/dash+xml')
        listitem.setProperty('inputstream', 'inputstream.adaptive')

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
