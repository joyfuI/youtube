# -*- coding: utf-8 -*-
#########################################################
# python
import os
import time

# third-party

# sjva 공용
from framework import path_data

# 패키지
from .plugin import logger, package_name
from .model import ModelSetting, ModelScheduler
from .logic_queue import LogicQueue
from .api_youtube_dl import APIYoutubeDL
#########################################################

class LogicNormal(object):
    @staticmethod
    def scheduler_function():
        for i in ModelScheduler.get_list():
            logger.debug('scheduler download %s', i.url)
            ret = APIYoutubeDL.info_dict(package_name, i.url)['info_dict']
            if ret.get('_type') != 'playlist':
                continue
            ModelScheduler.find(i.id).update(len(ret['entries']))

            save_path = ModelSetting.get('save_path')
            archive = os.path.join(path_data, 'db', package_name, '%d.txt' % i.id)
            ret = APIYoutubeDL.download(package_name, i.key, i.url, i.filename, save_path, i.format, None,
                                        'mp3' if i.convert_mp3 else None, None, archive, True)
            if ret['errorCode'] == 0:
                index = ret['index']
                while True:
                    time.sleep(10)  # 10초 대기
                    ret = APIYoutubeDL.status(package_name, index, i.key)
                    if ret['status'] == 'COMPLETED':
                        ModelScheduler.find(i.id).update()
                        break
                    elif ret['status'] in ('ERROR', 'STOP'):
                        break

    @staticmethod
    def get_preset_list():
        return [
            ['bestvideo+bestaudio/best', '최고 화질'],
            ['bestvideo[height<=1080]+bestaudio/best[height<=1080]', '1080p'],
            ['bestvideo[height<=720]+bestaudio/best[height<=720]', '720p'],
            ['worstvideo+worstaudio/worst', '최저 화질'],
            ['bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', '최고 화질(mp4)'],
            ['bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]', '1080p(mp4)'],
            ['bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]', '720p(mp4)'],
            ['bestaudio/best', '오디오만']
        ]

    @staticmethod
    def analysis(url):
        return APIYoutubeDL.info_dict(package_name, url)

    @staticmethod
    def download(form):
        options = {
            'filename': form['filename'],
            'format': form['format'],
            'convert_mp3': bool(form['convert_mp3']) if str(form['convert_mp3']).lower() != 'false' else False
        }
        for i in form.getlist('download[]'):
            LogicQueue.add_queue(i, options)
        return len(form.getlist('download[]'))

    @staticmethod
    def get_scheduler():
        ret = []
        for i in ModelScheduler.get_list(True):
            i['last_time'] = i['last_time'].strftime('%m-%d %H:%M:%S')
            ret.append(i)
        return ret

    @staticmethod
    def add_scheduler(form):
        if form['db_id']:
            data = {
                'filename': form['filename'],
                'format': form['format'],
                'convert_mp3': bool(form['convert_mp3']) if str(form['convert_mp3']).lower() != 'false' else False
            }
            ModelScheduler.find(form['db_id']).update(data)
        else:
            ret = APIYoutubeDL.info_dict(package_name, form['url'])['info_dict']
            if ret.get('_type') != 'playlist':
                return None
            data = {
                'webpage_url': ret['webpage_url'],
                'title': ret['title'],
                'uploader': ret.get('uploader', ''),
                'uploader_url': ret.get('uploader_url', ''),
                'count': len(ret['entries']),
                'filename': form['filename'],
                'format': form['format'],
                'convert_mp3': bool(form['convert_mp3']) if str(form['convert_mp3']).lower() != 'false' else False
            }
            ModelScheduler.create(data)
        return LogicNormal.get_scheduler()

    @staticmethod
    def del_scheduler(db_id):
        logger.debug('del_scheduler %s', db_id)
        ModelScheduler.find(db_id).delete()
        LogicNormal.del_archive(db_id)
        return LogicNormal.get_scheduler()

    @staticmethod
    def del_archive(db_id):
        archive = os.path.join(path_data, 'db', package_name, '%s.txt' % db_id)
        logger.debug('delete %s', archive)
        if os.path.isfile(archive):
            os.remove(archive)
