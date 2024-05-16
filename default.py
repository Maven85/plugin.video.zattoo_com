# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import xbmcaddon
import sys

try:
    from urllib.parse import parse_qs
except:
    from urlparse import parse_qs

addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
SESSION = addon.getSetting('session')
params = dict(parse_qs(sys.argv[2][1:]))
mode = params.get('mode', [''])[0]

if mode in ['watch', 'replay']:
    from resources.lib.watch import get_stream
    import xbmcgui
    stream = get_stream(mode, params['id'][0], params.get('sid', [''])[0], params.get('level', ['sd'])[0], params.get('drm', [False])[0], SESSION)
    listitem = xbmcgui.ListItem(path=stream['url'])
    if addon.getSetting('streaming_protocol').lower() in ['dash', 'dash_widevine']:
        from resources.lib.functions import get_kodi_version
        listitem.setContentLookup(False)
        listitem.setMimeType('application/dash+xml')
        listitem.setProperty('inputstream', 'inputstream.adaptive')
        if get_kodi_version() <= 20:
            listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        if stream.get('license_url'):
            listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            listitem.setProperty('inputstream.adaptive.license_key', '%s||R{SSM}|' % (stream['license_url']))

    if mode == 'replay':
        import xbmc
        from json import loads
        from resources.lib.functions import set_videoinfo, get_kodi_version
        listitem = set_videoinfo(listitem, dict(title=params.get('title', [''])[0]), get_kodi_version())
        art = loads(params.get('art', [''])[0].replace('\'', '"'))
        listitem.setArt(art)
        player = xbmc.Player()
        player.play(stream['url'], listitem)
    else:
        import xbmcplugin
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
elif mode == 'epg':
    from resources.lib.epg import list_epg_item
    pid = params.get('id', [''])[0]
    pg_hash = addon.getSetting('pg_hash')
    list_epg_item(pid, SESSION, pg_hash)
else:
    from resources.lib.channels import list_channels
    use_fanart = addon.getSetting('showFanart') == 'true'
    pg_hash = addon.getSetting('pg_hash')
    smart_hd = addon.getSetting('smart_hd')
    smart_hd_store = addon.getSetting('smart_hd_store')
    startup = addon.getSetting('startup') == 'true'
    list_channels(SESSION, pg_hash, use_fanart, smart_hd != smart_hd_store or startup)
    if startup:
        addon.setSetting('startup', 'false')
