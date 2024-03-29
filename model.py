import os
import traceback
import random
import string
from datetime import datetime

from framework import app, db, path_data
from framework.logger import get_logger
from framework.util import Util

package_name = __name__.split(".", maxsplit=1)[0]
logger = get_logger(package_name)
app.config["SQLALCHEMY_BINDS"][package_name] = "sqlite:///%s" % os.path.join(
    path_data, "db", f"{package_name}.db"
)


class ModelSetting(db.Model):
    __tablename__ = f"{package_name}_setting"
    __table_args__ = {"mysql_collate": "utf8_general_ci"}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String, nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    @staticmethod
    def get(key):
        try:
            return (
                db.session.query(ModelSetting).filter_by(key=key).first().value.strip()
            )
        except Exception as e:
            logger.error("Exception:%s %s", e, key)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_int(key):
        try:
            return int(ModelSetting.get(key))
        except Exception as e:
            logger.error("Exception:%s %s", e, key)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_bool(key):
        try:
            return ModelSetting.get(key) == "True"
        except Exception as e:
            logger.error("Exception:%s %s", e, key)
            logger.error(traceback.format_exc())

    @staticmethod
    def set(key, value):
        try:
            item = (
                db.session.query(ModelSetting)
                .filter_by(key=key)
                .with_for_update()
                .first()
            )
            if item is not None:
                item.value = value.strip()
                db.session.commit()
            else:
                db.session.add(ModelSetting(key, value.strip()))
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            logger.error("Error Key:%s Value:%s", key, value)

    @staticmethod
    def to_dict():
        try:
            return Util.db_list_to_dict(db.session.query(ModelSetting).all())
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def setting_save(req):
        try:
            for key, value in req.form.items():
                if key in ["scheduler", "is_running"]:
                    continue
                if key.startswith("tmp_"):
                    continue
                logger.debug("Key:%s Value:%s", key, value)
                entity = (
                    db.session.query(ModelSetting)
                    .filter_by(key=key)
                    .with_for_update()
                    .first()
                )
                entity.value = value
            db.session.commit()
            return True
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            return False

    @staticmethod
    def get_list(key):
        try:
            value = ModelSetting.get(key)
            values = [x.strip().strip() for x in value.replace("\n", "|").split("|")]
            values = Util.get_list_except_empty(values)
            return values
        except Exception as e:
            logger.error("Exception:%s %s", e, key)
            logger.error(traceback.format_exc())


class ModelScheduler(db.Model):
    __tablename__ = f"{package_name}_scheduler"
    __table_args__ = {"mysql_collate": "utf8_general_ci"}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    last_time = db.Column(db.DateTime, nullable=False)
    url = db.Column(db.String, nullable=False)
    title = db.Column(db.String)
    uploader = db.Column(db.String)
    uploader_url = db.Column(db.String)
    count = db.Column(db.Integer, nullable=False)
    save_path = db.Column(db.String, nullable=False)
    filename = db.Column(db.String, nullable=False)
    format = db.Column(db.String, nullable=False)
    convert_mp3 = db.Column(db.Boolean, nullable=False)
    subtitle = db.Column(db.String)
    date_after = db.Column(db.Date)
    playlistreverse = db.Column(db.Boolean, nullable=False)
    key = db.Column(db.String)

    def __init__(self, data):
        self.last_time = datetime.now()
        self.url = data["webpage_url"]
        self.title = data["title"]
        self.uploader = data["uploader"]
        self.uploader_url = data["uploader_url"]
        self.count = data["count"]
        self.save_path = data["save_path"]
        self.filename = data["filename"]
        self.format = data["format"]
        self.convert_mp3 = data["convert_mp3"]
        self.subtitle = data["subtitle"]
        self.date_after = data["date_after"]
        self.playlistreverse = data["playlistreverse"]
        self.key = "".join([random.choice(string.ascii_lowercase) for _ in range(5)])

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    @staticmethod
    def get_list(by_dict=False):
        try:
            tmp = db.session.query(ModelScheduler).all()
            if by_dict:
                tmp = [x.as_dict() for x in tmp]
            return tmp
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def find(db_id):
        try:
            return db.session.query(ModelScheduler).filter_by(id=db_id).first()
        except Exception as e:
            logger.error("Exception:%s %s", e, db_id)
            logger.error(traceback.format_exc())

    @staticmethod
    def create(data):
        try:
            entity = ModelScheduler(data)
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            return None

    def update(self, data=None):
        try:
            if data is None:
                self.last_time = datetime.now()
            elif isinstance(data, int):
                self.count = data
            else:
                if "save_path" in data:
                    self.save_path = data["save_path"]
                if "filename" in data:
                    self.filename = data["filename"]
                if "format" in data:
                    self.format = data["format"]
                if "convert_mp3" in data:
                    self.convert_mp3 = data["convert_mp3"]
                if "subtitle" in data:
                    self.subtitle = data["subtitle"]
                if "date_after" in data:
                    self.date_after = data["date_after"]
                if "playlistreverse" in data:
                    self.playlistreverse = data["playlistreverse"]
            db.session.commit()
            return True
        except Exception as e:
            logger.error("Exception:%s %s", e, self.id)
            logger.error(traceback.format_exc())
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            logger.error("Exception:%s %s", e, self.id)
            logger.error(traceback.format_exc())
            return False


class ModelQueue(db.Model):
    __tablename__ = f"{package_name}_queue"
    __table_args__ = {"mysql_collate": "utf8_general_ci"}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, nullable=False)
    url = db.Column(db.String, nullable=False)
    save_path = db.Column(db.String, nullable=False)
    filename = db.Column(db.String, nullable=False)
    format = db.Column(db.String, nullable=False)
    convert_mp3 = db.Column(db.Boolean, nullable=False)
    subtitle = db.Column(db.String)
    date_after = db.Column(db.Date)
    playlistreverse = db.Column(db.Boolean, nullable=False)
    key = db.Column(db.String)
    index = db.Column(db.Integer)

    def __init__(self, data):
        self.created_time = datetime.now()
        self.url = data["webpage_url"]
        self.save_path = data["save_path"]
        self.filename = data["filename"]
        self.format = data["format"]
        self.convert_mp3 = data["convert_mp3"]
        self.subtitle = data["subtitle"]
        self.date_after = data["date_after"]
        self.playlistreverse = data["playlistreverse"]
        self.key = "".join([random.choice(string.ascii_lowercase) for _ in range(5)])
        self.index = None

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    @staticmethod
    def get_list(by_dict=False):
        try:
            tmp = db.session.query(ModelQueue).all()
            if by_dict:
                tmp = [x.as_dict() for x in tmp]
            return tmp
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def find(db_id):
        try:
            return db.session.query(ModelQueue).filter_by(id=db_id).first()
        except Exception as e:
            logger.error("Exception:%s %s", e, db_id)
            logger.error(traceback.format_exc())

    @staticmethod
    def peek():
        entity = None
        try:
            entity = db.session.query(ModelQueue).first()
        except Exception as e:
            logger.error("Exception:%s %s", e, entity)
            logger.error(traceback.format_exc())
        return entity

    @staticmethod
    def is_empty():
        try:
            return db.session.query(ModelQueue).count() == 0
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def create(data):
        try:
            entity = ModelQueue(data)
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            return None

    def set_index(self, index):
        try:
            self.index = index
            db.session.commit()
            return True
        except Exception as e:
            logger.error("Exception:%s %s", e, self.id)
            logger.error(traceback.format_exc())
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            logger.error("Exception:%s %s", e, self.id)
            logger.error(traceback.format_exc())
            return False
