import os
import traceback
import time
import sqlite3
from threading import Thread

from framework import db, scheduler, path_data
from framework.logger import get_logger
from framework.job import Job
from framework.util import Util

from .model import ModelSetting, ModelQueue
from .logic_normal import LogicNormal

package_name = __name__.split('.')[0]
logger = get_logger(package_name)


class Logic(object):
    db_default = {
        'db_version': '4',
        'interval': '360',
        'auto_start': 'False',
        'default_save_path': os.path.join(path_data, 'download', package_name),
        'default_filename': '%(title)s-%(id)s.%(ext)s',
        'cookiefile_path': ''
    }

    @staticmethod
    def db_init():
        try:
            for key, value in Logic.db_default.items():
                if db.session.query(ModelSetting).filter_by(key=key).count() == 0:
                    db.session.add(ModelSetting(key, value))
            db.session.commit()
            Logic.migration()
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def plugin_load():
        try:
            logger.debug('%s plugin_load', package_name)
            Logic.db_init()  # DB 초기화

            # archive 파일 저장 폴더 생성
            path = os.path.join(path_data, 'db', package_name)
            if not os.path.isdir(path):
                os.makedirs(path)

            if ModelSetting.get_bool('auto_start'):
                Logic.scheduler_start()

            # 편의를 위해 json 파일 생성
            from .plugin import plugin_info
            Util.save_from_dict_to_json(plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def plugin_unload():
        try:
            logger.debug('%s plugin_unload', package_name)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def scheduler_start():
        try:
            logger.debug('%s scheduler_start', package_name)
            interval = ModelSetting.get('interval')
            job = Job(package_name, package_name, interval, Logic.scheduler_function, '유튜브 새로운 영상 다운로드', False)
            scheduler.add_job_instance(job)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def scheduler_stop():
        try:
            logger.debug('%s scheduler_stop', package_name)
            scheduler.remove_job(package_name)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def scheduler_function():
        try:
            LogicNormal.scheduler_function()
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def one_execute():
        try:
            if scheduler.is_include(package_name):
                if scheduler.is_running(package_name):
                    ret = 'is_running'
                else:
                    scheduler.execute_job(package_name)
                    ret = 'scheduler'
            else:
                def func():
                    time.sleep(2)
                    Logic.scheduler_function()

                Thread(target=func, args=()).start()
                ret = 'thread'
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            ret = 'fail'
        return ret

    @staticmethod
    def reset_db():
        try:
            db.session.query(ModelQueue).delete()
            db.session.commit()
            return True
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return False

    @staticmethod
    def migration():
        try:
            db_version = ModelSetting.get_int('db_version')
            connect = sqlite3.connect(os.path.join(path_data, 'db', '%s.db' % package_name))

            if db_version < 2:
                cursor = connect.cursor()
                cursor.execute("SELECT * FROM youtube_setting WHERE key = 'save_path'")
                save_path = cursor.fetchone()[2]
                cursor.execute("UPDATE youtube_setting SET value = ? WHERE key = 'default_save_path'", (save_path,))
                cursor.execute("DELETE FROM youtube_setting WHERE key = 'save_path'")
                cursor.execute("ALTER TABLE youtube_scheduler ADD save_path VARCHAR")
                cursor.execute("UPDATE youtube_scheduler SET save_path = ?", (save_path,))
                cursor.execute("ALTER TABLE youtube_queue ADD save_path VARCHAR")
                cursor.execute("UPDATE youtube_queue SET save_path = ?", (save_path,))

            if db_version < 3:
                cursor = connect.cursor()
                cursor.execute("ALTER TABLE youtube_scheduler ADD date_after DATE")
                cursor.execute("UPDATE youtube_scheduler SET date_after = ?", (None,))
                cursor.execute("ALTER TABLE youtube_queue ADD date_after DATE")
                cursor.execute("UPDATE youtube_queue SET date_after = ?", (None,))

            if db_version < 4:
                cursor = connect.cursor()
                cursor.execute("ALTER TABLE youtube_scheduler ADD subtitle VARCHAR")
                cursor.execute("UPDATE youtube_scheduler SET subtitle = ?", (None,))
                cursor.execute("ALTER TABLE youtube_queue ADD subtitle VARCHAR")
                cursor.execute("UPDATE youtube_queue SET subtitle = ?", (None,))
                cursor.execute("ALTER TABLE youtube_scheduler ADD playlistreverse BOOLEAN")
                cursor.execute("UPDATE youtube_scheduler SET playlistreverse = ?", (False,))
                cursor.execute("ALTER TABLE youtube_queue ADD playlistreverse BOOLEAN")
                cursor.execute("UPDATE youtube_queue SET playlistreverse = ?", (False,))

            connect.commit()
            connect.close()
            ModelSetting.set('db_version', Logic.db_default['db_version'])
            db.session.flush()
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
