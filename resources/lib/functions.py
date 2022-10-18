# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from kodi_six.utils import PY2, py2_decode


def warning(text, title='Zattoo Live TV', time=4500, exit=False):
    import xbmc
    import xbmcaddon
    if PY2:
        from xbmc import translatePath as xbmcvfs_translatePath
    else:
        from xbmcvfs import translatePath as xbmcvfs_translatePath
    import os.path
    icon = py2_decode(os.path.join(xbmcvfs_translatePath(xbmcaddon.Addon('plugin.video.zattoo_com').getAddonInfo('path')), 'icon.png'))
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, text, time, icon))
    if exit:
        import sys
        sys.exit(0)


def set_videoinfo(listitem, infolabels, kodi_version):

    if kodi_version >= 20:
        videoinfotag = listitem.getVideoInfoTag()

        if infolabels.get('title') is not None:
            videoinfotag.setTitle(infolabels.get('title'))
        if infolabels.get('plot') is not None:
            videoinfotag.setPlot(infolabels.get('plot'))
    else:
        listitem.setInfo('video', infolabels)

    return listitem


def set_streaminfo(listitem, streamlabels, kodi_version):

        if kodi_version >= 20:
            videoinfotag = listitem.getVideoInfoTag()
            import xbmc
            videostream = xbmc.VideoStreamDetail()

            if streamlabels.get('duration') is not None:
                videostream.setDuration(streamlabels.get('duration'))

            videoinfotag.addVideoStream(videostream)
        else:
            listitem.addStreamInfo('video', streamlabels)

        return listitem
