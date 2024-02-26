# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from kodi_six.utils import py2_encode
from hashlib import md5
from json import loads
from re import search, findall
from time import sleep
from uuid import UUID
import xbmc
import xbmcaddon

try:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
except:
    from urllib import urlencode
    from urllib2 import urlopen, Request, URLError, HTTPError

addon = xbmcaddon.Addon(id='plugin.video.zattoo_com')
standard_header = {
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://zattoo.com/client',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}
default_app_version = '3.2330.2'


def get_client_app_token():
    try:
        client_app_token_url = 'https://zattoo.com/client/token.json'
        html = urlopen('https://zattoo.com/login').read().decode('utf-8')
        for js_url in findall('<script.*?src="([^"]*\.js)"', html):
            js_content_url = 'https://zattoo.com{0}'.format(js_url) if not js_url.startswith('http') else js_url
            if not js_content_url.startswith('https://zattoo.com'):
                continue
            urlopen(js_content_url)
            js_content = urlopen(js_content_url).read().decode('utf-8')
            matches = findall('(token-[a-z0-9]*\.json)', js_content)
            if len(matches) == 1:
                client_app_token_url = '{0}/{1}'.format(js_content_url[:js_content_url.rindex('/')], matches[0])

        client_app_token_res = urlopen(client_app_token_url).read().decode('utf-8')
        client_app_token = loads(client_app_token_res).get('session_token')
        return client_app_token
    except URLError:
        from .functions import warning
        return warning('Apptoken konnte nicht ermittelt werden!', exit=True)
    except:
        return ''


def get_app_version():
    try:
        html = urlopen('https://zattoo.com/login').read().decode('utf-8')
        for js_url in findall('<script.*?src="([^"]*\.js)"', html):
            js_content_url = 'https://zattoo.com{0}'.format(js_url) if not js_url.startswith('http') else js_url
            if not js_content_url.startswith('https://zattoo.com'):
                continue
            js_content = urlopen(js_content_url).read().decode('utf-8')
            matches = findall('web-app@(\d+\.\d+\.\d+)', js_content)
            if len(matches) == 1:
                return matches[0]
    except URLError:
        from .functions import warning
        return warning('Appversion konnte nicht ermittelt werden!', exit=True)
    except:
        return ''
    xbmc.log('[{0}] warning: failed to detect app version'.format(addon.getAddonInfo('id')))
    return default_app_version


def uniq_id():
    if addon.getSetting('device_id'):
        return addon.getSetting('device_id')

    device_id = ''
    mac_addr = xbmc.getInfoLabel('Network.MacAddress')

    # hack response busy
    i = 0
    while not py2_encode(':') in mac_addr and i < 3:
        i += 1
        sleep(1)
        mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    if py2_encode(':') in mac_addr:
        device_id = str(UUID(md5(mac_addr.encode('utf-8')).hexdigest()))
    elif xbmc.getCondVisibility('System.Platform.Android'):
        device_id = str(UUID(md5(self.get_android_uuid().encode('utf-8')).hexdigest()))

    if not device_id:
        xbmc.log('It is not possible to get a system UUID creating a new UUID')
        device_id = _get_fake_uuid(xbmc.getCondVisibility('system.platform.linux') == False)

    if device_id == '':
        xbmc.log('[{0}] error: failed to get device id ({1})'.format(addon.getAddonInfo('id'), str(mac_addr)))
    addon.setSetting(id='device_id', value=device_id)
    return device_id


def get_android_uuid(self):
    from subprocess import PIPE as subprocess_PIPE, Popen as subprocess_Popen
    from re import sub as re_sub
    values = ''
    try:
        # Due to the new android security we cannot get any type of serials
        sys_prop = ['ro.product.board', 'ro.product.brand', 'ro.product.device', 'ro.product.locale'
                    'ro.product.manufacturer', 'ro.product.model', 'ro.product.platform',
                    'persist.sys.timezone', 'persist.sys.locale', 'net.hostname']
        # Warning net.hostname property starting from android 10 is deprecated return empty
        with subprocess_Popen(['/system/bin/getprop'], stdout=subprocess_PIPE) as proc:
            output_data = proc.communicate()[0].decode('utf-8')
        list_values = output_data.splitlines()
        for value in list_values:
            value_splitted = re_sub(r'\[|\]|\s', '', value).split(':')
            if value_splitted[0] in sys_prop:
                values += value_splitted[1]
    except Exception:
        pass
    return values


def _get_fake_uuid(with_hostname):
    import platform
    list_values = [xbmc.getInfoLabel('System.Memory(total)')]
    if with_hostname:
        try:
            list_values.append(platform.node())
        except Exception:
            pass
    return '_'.join(list_values)


def extract_session_id(cookie_dict):
    session_id = None
    if cookie_dict:
        for cookie in cookie_dict:
            match = search('beaker\.session\.id\s*=\s*([^\s;]*)', cookie)
            if match:
                session_id = match.group(1)
                break
    return session_id


def get_session_cookie():
    post_data = ('app_version={0}&client_app_token={1}&uuid={2}'.format(get_app_version(), get_client_app_token(), uniq_id())).encode('utf-8')
    req = Request('https://zattoo.com/zapi/v3/session/hello', post_data, standard_header)
    xbmc.log('[{0}]: post_data = {1}'.format(addon.getAddonInfo('id'), post_data))
    response = urlopen(req)
    return extract_session_id([value for key, value in response.headers.items() if key.lower() == 'set-cookie'])


def update_pg_hash(hash):
    addon.setSetting(id='pg_hash', value=hash)


def update_session(session):
    addon.setSetting(id='session', value=session)


def get_json_data(api_url, cookie, post_data=None):
    header = standard_header.copy()
    header.update({'Cookie': 'beaker.session.id=' + cookie})
    if post_data:
        post_data = urlencode(post_data).encode('utf-8')
    req = Request(api_url, post_data, header)
    response = urlopen(req)
    new_cookie = extract_session_id([value for key, value in response.headers.items() if key.lower() == 'set-cookie'])
    if new_cookie:
        update_session(new_cookie)
    return response.read()


def login():
    USER_NAME = addon.getSetting('username')
    PASSWORD = addon.getSetting('password')
    if not USER_NAME or not PASSWORD:
        from .functions import warning
        return warning('Bitte Benutzerdaten eingeben!', exit=True)
    handshake_cookie = get_session_cookie()
    try:
        login_json_data = get_json_data('https://zattoo.com/zapi/v3/account/login', handshake_cookie, {'login': USER_NAME, 'password': PASSWORD})
    except HTTPError:
        from .functions import warning
        return warning('Falsche Logindaten!', exit=True)
    import json
    pg_hash = json.loads(login_json_data)['power_guide_hash']
    update_pg_hash(pg_hash)
