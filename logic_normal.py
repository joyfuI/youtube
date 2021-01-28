# -*- coding: utf-8 -*-
#########################################################
# python
import os
import time
from datetime import date

# third-party

# sjva 공용
from framework import path_data

# 패키지
from .plugin import logger, package_name
from .model import ModelScheduler
from .logic_queue import LogicQueue
from .api_youtube_dl import APIYoutubeDL
#########################################################

class LogicNormal(object):
    @staticmethod
    def scheduler_function():
        for i in ModelScheduler.get_list():
            logger.debug('scheduler download %s', i.url)
            info_dict = APIYoutubeDL.info_dict(package_name, i.url)['info_dict']
            if info_dict is None or info_dict.get('_type') != 'playlist':
                continue
            ModelScheduler.find(i.id).update(len(info_dict['entries']))
            archive = os.path.join(path_data, 'db', package_name, '%d.txt' % i.id)
            date_after = i.date_after.strftime('%Y%m%d') if i.date_after else None
            download = APIYoutubeDL.download(package_name, i.key, i.url, filename=i.filename, save_path=i.save_path,
                                             format_code=i.format, preferredcodec='mp3' if i.convert_mp3 else None,
                                             dateafter=date_after, archive=archive, start=True)
            if download['errorCode'] == 0:
                index = download['index']
                while True:
                    time.sleep(10)  # 10초 대기
                    download = APIYoutubeDL.status(package_name, index, i.key)
                    if download['status'] == 'COMPLETED':
                        ModelScheduler.find(i.id).update()
                        break
                    elif download['status'] in ('ERROR', 'STOP'):
                        break
            else:
                logger.debug('scheduler download fail %s', download['errorCode'])

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
        date_after = form['date_after'].split('-')
        date_after = list(map(lambda i: int(i), date_after))
        year, month, day = date_after
        options = {
            'save_path': form['save_path'],
            'filename': form['filename'],
            'format': form['format'],
            'convert_mp3': bool(form['convert_mp3']) if str(form['convert_mp3']).lower() != 'false' else False,
            'date_after': date(year, month, day) if str(form['daterange']).lower() != 'false' else None
        }
        for i in form.getlist('download[]'):
            LogicQueue.add_queue(i, options)
        return len(form.getlist('download[]'))

    @staticmethod
    def get_scheduler():
        ret = []
        for i in ModelScheduler.get_list(True):
            i['last_time'] = i['last_time'].strftime('%m-%d %H:%M:%S')
            i['path'] = os.path.join(i['save_path'], i['filename'])
            ret.append(i)
        return ret

    @staticmethod
    def add_scheduler(form):
        date_after = form['date_after'].split('-')
        date_after = list(map(lambda i: int(i), date_after))
        year, month, day = date_after
        if form['db_id']:
            data = {
                'save_path': form['save_path'],
                'filename': form['filename'],
                'format': form['format'],
                'convert_mp3': bool(form['convert_mp3']) if str(form['convert_mp3']).lower() != 'false' else False,
                'date_after': date(year, month, day) if str(form['daterange']).lower() != 'false' else None
            }
            ModelScheduler.find(form['db_id']).update(data)
        else:
            info_dict = APIYoutubeDL.info_dict(package_name, form['url'])['info_dict']
            if info_dict is None or info_dict.get('_type') != 'playlist':
                return None
            data = {
                'webpage_url': info_dict['webpage_url'],
                'title': info_dict['title'],
                'uploader': info_dict.get('uploader', ''),
                'uploader_url': info_dict.get('uploader_url', ''),
                'count': len(info_dict['entries']),
                'save_path': form['save_path'],
                'filename': form['filename'],
                'format': form['format'],
                'convert_mp3': bool(form['convert_mp3']) if str(form['convert_mp3']).lower() != 'false' else False,
                'date_after': date(year, month, day) if str(form['daterange']).lower() != 'false' else None
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
