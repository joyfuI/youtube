# -*- coding: utf-8 -*-
#########################################################
# python
from datetime import datetime

# third-party
import requests

# sjva 공용, 패키지
from system.model import ModelSetting as SystemModelSetting
#########################################################

HOST_URL = 'http://localhost:%s' % SystemModelSetting.get('port')

class APIYoutubeDL(object):
    ERROR_CODE = {
        0: '성공',
        1: '필수 요청 변수가 없음',
        2: '잘못된 동영상 주소',
        3: '인덱스 범위를 벗어남',
        4: '키 값이 일치하지 않음',
        5: '허용되지 않은 값이 있음',
        10: '실패'
    }

    STATUS = {
        'READY': '준비',
        'START': '분석중',
        'DOWNLOADING': '다운로드중',
        'ERROR': '실패',
        'FINISHED': '변환중',
        'STOP': '중지',
        'COMPLETED': '완료'
    }

    @staticmethod
    def info_dict(plugin, url):
        data = {
            'plugin': plugin,
            'url': url
        }
        if SystemModelSetting.get_bool('auth_use_apikey'):  # APIKEY
            data['apikey'] = SystemModelSetting.get('auth_apikey')
        return requests.post('%s/youtube-dl/api/info_dict' % HOST_URL, data=data).json()

    @staticmethod
    def download(plugin, key, url, filename=None, save_path=None, format_code=None, preferedformat=None,
                 preferredcodec=None, preferredquality=None, archive=None, start=None):
        data = {
            'plugin': plugin,
            'key': key,
            'url': url
        }
        if filename:
            data['filename'] = filename
        if save_path:
            data['save_path'] = save_path
        if format_code:
            data['format'] = format_code
        if preferedformat:
            data['preferedformat'] = preferedformat
        if preferredcodec:
            data['preferredcodec'] = preferredcodec
        if preferredquality:
            data['preferredquality'] = preferredquality
        if archive:
            data['archive'] = archive
        if start:
            data['start'] = start
        if SystemModelSetting.get_bool('auth_use_apikey'):  # APIKEY
            data['apikey'] = SystemModelSetting.get('auth_apikey')
        return requests.post('%s/youtube-dl/api/download' % HOST_URL, data=data).json()

    @staticmethod
    def start(plugin, index, key):
        data = {
            'plugin': plugin,
            'index': index,
            'key': key
        }
        if SystemModelSetting.get_bool('auth_use_apikey'):  # APIKEY
            data['apikey'] = SystemModelSetting.get('auth_apikey')
        return requests.post('%s/youtube-dl/api/start' % HOST_URL, data=data).json()

    @staticmethod
    def stop(plugin, index, key):
        data = {
            'plugin': plugin,
            'index': index,
            'key': key
        }
        if SystemModelSetting.get_bool('auth_use_apikey'):  # APIKEY
            data['apikey'] = SystemModelSetting.get('auth_apikey')
        return requests.post('%s/youtube-dl/api/stop' % HOST_URL, data=data).json()

    @staticmethod
    def status(plugin, index, key):
        data = {
            'plugin': plugin,
            'index': index,
            'key': key
        }
        if SystemModelSetting.get_bool('auth_use_apikey'):  # APIKEY
            data['apikey'] = SystemModelSetting.get('auth_apikey')
        res = requests.post('%s/youtube-dl/api/status' % HOST_URL, data=data).json()
        if res['start_time']:
            res['start_time'] = datetime.strptime(res['start_time'], '%Y-%m-%dT%H:%M:%S')
        if res['end_time']:
            res['end_time'] = datetime.strptime(res['end_time'], '%Y-%m-%dT%H:%M:%S')
        return res
