# -*- coding: utf-8 -*-
#########################################################
# python
import time
import traceback
import threading

# third-party

# sjva 공용

# 패키지
from .plugin import package_name, logger
from .model import ModelSetting, ModelQueue
from .api_youtube_dl import APIYoutubeDL
#########################################################

class LogicQueue(object):
    __thread = None

    @staticmethod
    def queue_load():
        threading.Thread(target=LogicQueue.queue_start).start()

    @staticmethod
    def queue_start():
        try:
            time.sleep(10)  # youtube-dl 플러그인이 언제 로드될지 모르니 일단 10초 대기
            for i in ModelQueue.get_list():
                save_path = ModelSetting.get('save_path')
                logger.debug('queue add %s', i.url)
                ret = APIYoutubeDL.download(package_name, i.key, i.url, i.filename, save_path, i.format, None,
                                            'mp3' if i.convert_mp3 else None, None, None, False)
                if ret['errorCode'] == 0:
                    i.set_index(ret['index'])
                else:
                    logger.debug('queue add fail %s', ret['errorCode'])
                    i.delete()

            LogicQueue.__thread = threading.Thread(target=LogicQueue.thread_function)
            LogicQueue.__thread.daemon = True
            LogicQueue.__thread.start()
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def thread_function():
        try:
            while not ModelQueue.is_empty():
                entity = ModelQueue.peek()
                logger.debug('queue download %s', entity.url)
                ret = APIYoutubeDL.start(package_name, entity.index, entity.key)
                if ret['errorCode'] == 0:
                    while True:
                        time.sleep(10)  # 10초 대기
                        ret = APIYoutubeDL.status(package_name, entity.index, entity.key)
                        if ret['status'] in ('COMPLETED', 'ERROR', 'STOP'):
                            break
                else:
                    logger.debug('queue download fail %s', ret)
                entity.delete()
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def add_queue(url, options):
        try:
            options['webpage_url'] = url
            entity = ModelQueue.create(options)
            save_path = ModelSetting.get('save_path')
            ret = APIYoutubeDL.download(package_name, entity.key, url, entity.filename, save_path, entity.format, None,
                                        'mp3' if entity.convert_mp3 else None, None, None, False)
            if ret['errorCode'] == 0:
                entity.set_index(ret['index'])
            else:
                logger.debug('queue add fail %d', ret['errorCode'])
                entity.delete()
                return None

            if not LogicQueue.__thread.is_alive():
                LogicQueue.__thread = threading.Thread(target=LogicQueue.thread_function)
                LogicQueue.__thread.daemon = True
                LogicQueue.__thread.start()
            return entity
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return None
