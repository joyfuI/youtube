import traceback
import time
from threading import Thread

from framework.logger import get_logger

from .model import ModelQueue
from .api_youtube_dl import APIYoutubeDL

package_name = __name__.split('.')[0]
logger = get_logger(package_name)


class LogicQueue(object):
    __thread = None

    @staticmethod
    def queue_load():
        Thread(target=LogicQueue.queue_start).start()

    @staticmethod
    def queue_start():
        try:
            time.sleep(10)  # youtube-dl 플러그인이 언제 로드될지 모르니 일단 10초 대기
            for i in ModelQueue.get_list():
                logger.debug('queue add %s', i.url)
                date_after = i.date_after.strftime('%Y%m%d') if i.date_after else None
                download = APIYoutubeDL.download(package_name, i.key, i.url, filename=i.filename, save_path=i.save_path,
                                                 format_code=i.format, preferredcodec='mp3' if i.convert_mp3 else None,
                                                 dateafter=date_after,
                                                 playlist='reverse' if i.playlistreverse else None, start=False)
                if i.subtitle is not None:
                    sub = APIYoutubeDL.sub(package_name, i.key, i.url, filename=i.filename, save_path=i.save_path,
                                           all_subs=False, sub_lang=i.subtitle, auto_sub=True, dateafter=date_after,
                                           playlist='reverse' if i.playlistreverse else None, start=True)
                else:
                    sub = 0
                if download['errorCode'] == 0 and sub['errorCode'] == 0:
                    i.set_index(download['index'])
                else:
                    logger.debug('queue add fail %s %s', download['errorCode'], sub['errorCode'])
                    i.delete()

            LogicQueue.__thread = Thread(target=LogicQueue.thread_function)
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
                start = APIYoutubeDL.start(package_name, entity.index, entity.key)
                if start['errorCode'] == 0:
                    while True:
                        time.sleep(10)  # 10초 대기
                        status = APIYoutubeDL.status(package_name, entity.index, entity.key)
                        if status['status'] in ('COMPLETED', 'ERROR', 'STOP'):
                            break
                else:
                    logger.debug('queue download fail %s', start['errorCode'])
                entity.delete()
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def add_queue(url, options):
        try:
            options['webpage_url'] = url
            entity = ModelQueue.create(options)
            date_after = entity.date_after.strftime('%Y%m%d') if entity.date_after else None
            download = APIYoutubeDL.download(package_name, entity.key, url, filename=entity.filename,
                                             save_path=entity.save_path, format_code=entity.format,
                                             preferredcodec='mp3' if entity.convert_mp3 else None, dateafter=date_after,
                                             playlist='reverse' if entity.playlistreverse else None, start=False)
            if entity.subtitle is not None:
                sub = APIYoutubeDL.sub(package_name, entity.key, url, filename=entity.filename,
                                       save_path=entity.save_path, all_subs=False, sub_lang=entity.subtitle,
                                       auto_sub=True, dateafter=date_after,
                                       playlist='reverse' if entity.playlistreverse else None, start=True)
            else:
                sub = 0
            if download['errorCode'] == 0 and sub['errorCode'] == 0:
                entity.set_index(download['index'])
            else:
                logger.debug('queue add fail %s %s', download['errorCode'], sub['errorCode'])
                entity.delete()
                return None

            if not LogicQueue.__thread.is_alive():
                LogicQueue.__thread = Thread(target=LogicQueue.thread_function)
                LogicQueue.__thread.daemon = True
                LogicQueue.__thread.start()
            return entity
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return None
