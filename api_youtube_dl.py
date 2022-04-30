# 최종 업데이트 20220430
from typing import Optional
from datetime import datetime

import requests

from system.model import ModelSetting as SystemModelSetting

HOST_URL = f"http://localhost:{SystemModelSetting.get('port')}"


class APIYoutubeDL(object):
    ERROR_CODE = {
        0: "성공",
        1: "필수 요청 변수가 없음",
        2: "잘못된 동영상 주소",
        3: "인덱스 범위를 벗어남",
        4: "키 값이 일치하지 않음",
        5: "허용되지 않은 값이 있음",
        10: "실패",
    }

    STATUS = {
        "READY": "준비",
        "START": "분석중",
        "DOWNLOADING": "다운로드중",
        "ERROR": "실패",
        "FINISHED": "변환중",
        "STOP": "중지",
        "COMPLETED": "완료",
    }

    @staticmethod
    def info_dict(plugin: str, url: str) -> dict:
        data = {"plugin": plugin, "url": url}
        if SystemModelSetting.get_bool("auth_use_apikey"):  # APIKEY
            data["apikey"] = SystemModelSetting.get("auth_apikey")
        return requests.post(f"{HOST_URL}/youtube-dl/api/info_dict", data=data).json()

    @staticmethod
    def download(
        plugin: str,
        key: str,
        url: str,
        filename: Optional[str] = None,
        save_path: Optional[str] = None,
        format_code: Optional[str] = None,
        preferedformat: Optional[str] = None,
        preferredcodec: Optional[str] = None,
        preferredquality: Optional[int] = None,
        dateafter: Optional[str] = None,
        playlist: Optional[str] = None,
        archive: Optional[str] = None,
        start: Optional[bool] = None,
        cookiefile: Optional[str] = None,
    ) -> dict:
        data = {"plugin": plugin, "key": key, "url": url}
        if filename:
            data["filename"] = filename
        if save_path:
            data["save_path"] = save_path
        if format_code:
            data["format"] = format_code
        if preferedformat:
            data["preferedformat"] = preferedformat
        if preferredcodec:
            data["preferredcodec"] = preferredcodec
        if preferredquality:
            data["preferredquality"] = preferredquality
        if dateafter:
            data["dateafter"] = dateafter
        if playlist:
            data["playlist"] = playlist
        if archive:
            data["archive"] = archive
        if start:
            data["start"] = start
        if cookiefile:
            data["cookiefile"] = cookiefile
        if SystemModelSetting.get_bool("auth_use_apikey"):  # APIKEY
            data["apikey"] = SystemModelSetting.get("auth_apikey")
        return requests.post(f"{HOST_URL}/youtube-dl/api/download", data=data).json()

    @staticmethod
    def thumbnail(
        plugin: str,
        key: str,
        url: str,
        filename: Optional[str] = None,
        save_path: Optional[str] = None,
        all_thumbnails: Optional[bool] = None,
        dateafter: Optional[str] = None,
        playlist: Optional[str] = None,
        archive: Optional[str] = None,
        start: Optional[bool] = None,
        cookiefile: Optional[str] = None,
    ) -> dict:
        data = {"plugin": plugin, "key": key, "url": url}
        if filename:
            data["filename"] = filename
        if save_path:
            data["save_path"] = save_path
        if all_thumbnails:
            data["all_thumbnails"] = all_thumbnails
        if dateafter:
            data["dateafter"] = dateafter
        if playlist:
            data["playlist"] = playlist
        if archive:
            data["archive"] = archive
        if start:
            data["start"] = start
        if cookiefile:
            data["cookiefile"] = cookiefile
        if SystemModelSetting.get_bool("auth_use_apikey"):  # APIKEY
            data["apikey"] = SystemModelSetting.get("auth_apikey")
        return requests.post(f"{HOST_URL}/youtube-dl/api/thumbnail", data=data).json()

    @staticmethod
    def sub(
        plugin: str,
        key: str,
        url: str,
        filename: Optional[str] = None,
        save_path: Optional[str] = None,
        all_subs: Optional[bool] = None,
        sub_lang: Optional[str] = None,
        auto_sub: Optional[bool] = None,
        dateafter: Optional[str] = None,
        playlist: Optional[str] = None,
        archive: Optional[str] = None,
        start: Optional[bool] = None,
        cookiefile: Optional[str] = None,
    ) -> dict:
        data = {"plugin": plugin, "key": key, "url": url}
        if filename:
            data["filename"] = filename
        if save_path:
            data["save_path"] = save_path
        if all_subs:
            data["all_subs"] = all_subs
        if sub_lang:
            data["sub_lang"] = sub_lang
        if auto_sub:
            data["auto_sub"] = auto_sub
        if dateafter:
            data["dateafter"] = dateafter
        if playlist:
            data["playlist"] = playlist
        if archive:
            data["archive"] = archive
        if start:
            data["start"] = start
        if cookiefile:
            data["cookiefile"] = cookiefile
        if SystemModelSetting.get_bool("auth_use_apikey"):  # APIKEY
            data["apikey"] = SystemModelSetting.get("auth_apikey")
        return requests.post(f"{HOST_URL}/youtube-dl/api/sub", data=data).json()

    @staticmethod
    def start(plugin: str, index: int, key: str) -> dict:
        data = {"plugin": plugin, "index": index, "key": key}
        if SystemModelSetting.get_bool("auth_use_apikey"):  # APIKEY
            data["apikey"] = SystemModelSetting.get("auth_apikey")
        return requests.post(f"{HOST_URL}/youtube-dl/api/start", data=data).json()

    @staticmethod
    def stop(plugin: str, index: int, key: str) -> dict:
        data = {"plugin": plugin, "index": index, "key": key}
        if SystemModelSetting.get_bool("auth_use_apikey"):  # APIKEY
            data["apikey"] = SystemModelSetting.get("auth_apikey")
        return requests.post(f"{HOST_URL}/youtube-dl/api/stop", data=data).json()

    @staticmethod
    def status(plugin: str, index: int, key: str) -> dict:
        data = {"plugin": plugin, "index": index, "key": key}
        if SystemModelSetting.get_bool("auth_use_apikey"):  # APIKEY
            data["apikey"] = SystemModelSetting.get("auth_apikey")
        res = requests.post(f"{HOST_URL}/youtube-dl/api/status", data=data).json()
        if res["start_time"]:
            res["start_time"] = datetime.strptime(
                res["start_time"], "%Y-%m-%dT%H:%M:%S"
            )
        if res["end_time"]:
            res["end_time"] = datetime.strptime(res["end_time"], "%Y-%m-%dT%H:%M:%S")
        return res
