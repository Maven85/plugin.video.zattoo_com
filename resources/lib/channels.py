# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import xbmcplugin
import xbmcgui
import json
from datetime import datetime, timedelta

from .api import get_json_data

try:
    from urllib.error import URLError, HTTPError
    from urllib.parse import urlencode
except:
    from urllib2 import URLError, HTTPError
    from urllib import urlencode

URI = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])


def round_seconds(seconds_to_round, round_to_nearest_seconds=300):
    if seconds_to_round <= 60:
        return 60
    if seconds_to_round < 500:
        return seconds_to_round - (seconds_to_round % 60)
    important_range = seconds_to_round % round_to_nearest_seconds
    half_round_range = round_to_nearest_seconds >> 1
    if important_range < half_round_range:
        seconds_to_round -= important_range
    else:
        seconds_to_round = seconds_to_round + (round_to_nearest_seconds - important_range)
    return seconds_to_round


def list_channels(session, pg_hash, use_fanart=False, force_login=False):
    s_epoch_datetime = datetime(1970, 1, 1)
    utc_now = datetime.utcnow()
    s_datetime = utc_now.replace(minute=0, second=0, microsecond=0) - s_epoch_datetime
    s_utc = int(s_datetime.total_seconds())
    e_utc = int((s_datetime + timedelta(hours=6)).total_seconds())
    if not pg_hash or not session or force_login:
        from .api import login
        login()
        import xbmcaddon
        addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
        pg_hash = addon.getSetting('pg_hash')
        session = addon.getSetting('session')
    try:
        json_data = json.loads(get_json_data('https://zattoo.com/zapi/v4/cached/%s/channels?' % pg_hash, session))
        guide_data = json.loads(get_json_data('https://zattoo.com/zapi/v3/cached/%s/guide?start=%s&end=%s' % (pg_hash, s_utc, e_utc), session))
    except HTTPError:
        from .api import login
        login()
        import xbmcaddon
        addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
        pg_hash = addon.getSetting('pg_hash')
        session = addon.getSetting('session')
        json_data = json.loads(get_json_data('https://zattoo.com/zapi/v4/cached/%s/channels?' % pg_hash, session))
        guide_data = json.loads(get_json_data('https://zattoo.com/zapi/v3/cached/%s/guide?start=%s&end=%s' % (pg_hash, s_utc, e_utc), session))
    except URLError:
        from .functions import warning
        warning('Keine Netzwerkverbindung!')
        return
    except:
        from .functions import warning
        warning('TV Daten konnten nicht geladen werden!')
        return

    if json_data['channels']:
        from .functions import set_videoinfo, set_streaminfo, get_kodi_version
        from xbmc import getInfoLabel
        import xbmcaddon
        kodi_version = get_kodi_version()
        current_timestamp = int((utc_now.replace(second=0, microsecond=0) - s_epoch_datetime).total_seconds())
        addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
        streaming_protocol = addon.getSetting('streaming_protocol').lower()
        replay_availability = addon.getSetting('replay_availability') == 'true'
        for channel in json_data['channels']:
            for quality in channel['qualities']:
                if quality['availability'] == 'available':
                    id = channel['cid']
                    level = quality.get('level', 'sd')
                    drm_required = quality.get('drm_required', False)
                    if level == 'hd' and drm_required and streaming_protocol in ['hls', 'dash']:
                        level = 'sd'
                    epg_now = None
                    epg_next = None
                    for index, epg_data in enumerate(guide_data.get('channels').get(id)):
                        if epg_data.get('s') < current_timestamp and epg_data.get('e') > current_timestamp:
                            epg_now = epg_data
                            if len(guide_data.get('channels').get(id)) > index + 1:
                                epg_next = guide_data.get('channels').get(id)[index + 1]
                            break

                    channel_name = quality['title']
                    title = '[B][COLOR blue]%s[/COLOR][/B]' % channel_name
                    plot = ''
                    duration_in_seconds = 0
                    art = None
                    cmi = None
                    if epg_now:
                        s_now = datetime.fromtimestamp(epg_now['s']).strftime('%H:%M')
                        title = '[COLOR red]%s[/COLOR] %s %s' % (s_now, title, epg_now['t'])
                        subtitle = epg_now['et']
                        if subtitle:
                            title = '%s: %s' % (title, subtitle)

                        art = dict(thumb='http://thumb.zattic.com/%s/500x288.jpg?r=%s' % (id, current_timestamp))
                        if use_fanart:
                            try:
                                fanart = channel['now']['i'].replace('format_480x360.jpg', 'format_1280x720.jpg')
                            except:
                                fanart = 'http://thumb.zattic.com/%s/1280x720.jpg' % id
                            art.update(dict(fanart=fanart))
                        duration_in_seconds = round_seconds(epg_now['e'] - current_timestamp)
                        cmi = [
                            ('EPG Daten laden', 'RunPlugin(plugin://plugin.video.zattoo_com/?mode=epg&id=%s)' % epg_now['id'])
                        ]
                        if replay_availability and epg_now['r_e'] == True:
                            cmi.append(('Von Beginn abspielen', 'RunPlugin(plugin://plugin.video.zattoo_com/?%s)' % (urlencode(dict(mode='replay', id=id, sid=epg_now['id'], title=(title or channel_name), art=art)))))

                    if epg_next:
                        s_next = datetime.fromtimestamp(epg_next['s']).strftime('%H:%M')
                        e_next = datetime.fromtimestamp(epg_next['e']).strftime('%H:%M')
                        plot = '%s[B][COLOR blue]Danach: %s - %s (%i Min.)[/COLOR][/B]\n%s' % (
                                plot, s_next, e_next, (epg_next['e'] - epg_next['s']) / 60, epg_next['t'])
                        plotsubtitle = epg_next['et']
                        if plotsubtitle:
                            plot = '%s: %s' % (plot, plotsubtitle)

                    item = xbmcgui.ListItem(title)
                    item = set_videoinfo(item, dict(title=title or channel_name, plot=plot), kodi_version)
                    item.setProperty('IsPlayable', 'true')
                    if art:
                        item.setArt(art)
                    if cmi:
                        item.addContextMenuItems(cmi)
                    if duration_in_seconds > 0:
                        item = set_streaminfo(item, dict(duration=duration_in_seconds), kodi_version)
                    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url='%s?mode=watch&id=%s&level=%s&drm=%s' % (URI, id, level, drm_required), listitem=item)
                    break
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
