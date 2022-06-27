import os
import traceback
from datetime import date

from flask import Blueprint, request, render_template, redirect, jsonify
from flask_login import login_required

from framework import scheduler, socketio
from framework.logger import get_logger

from .logic import Logic
from .logic_normal import LogicNormal
from .logic_queue import LogicQueue
from .model import ModelSetting

package_name = __name__.split(".", maxsplit=1)[0]
logger = get_logger(package_name)

#########################################################
# 플러그인 공용
#########################################################
blueprint = Blueprint(
    package_name,
    package_name,
    url_prefix=f"/{package_name}",
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)

menu = {
    "main": [package_name, "유튜브"],
    "sub": [["setting", "설정"], ["request", "요청"], ["scheduler", "스케줄링"], ["log", "로그"]],
    "category": "vod",
}

plugin_info = {
    "version": "2.1.1",
    "name": "youtube",
    "category_name": "vod",
    "developer": "joyfuI",
    "description": "YouTube 다운로드",
    "home": "https://github.com/joyfuI/youtube",
    "more": "",
}


def plugin_load():
    Logic.plugin_load()
    LogicQueue.queue_load()


def plugin_unload():
    Logic.plugin_unload()


#########################################################
# WEB Menu
#########################################################
@blueprint.route("/")
def home():
    return redirect(f"/{package_name}/request")


@blueprint.route("/<sub>")
@login_required
def first_menu(sub):
    try:
        arg = {
            "package_name": package_name,
            "template_name": f"{package_name}_{sub}",
            "package_version": plugin_info["version"],
        }

        if sub == "setting":
            arg.update(ModelSetting.to_dict())
            arg["scheduler"] = str(scheduler.is_include(package_name))
            arg["is_running"] = str(scheduler.is_running(package_name))
            return render_template(f"{package_name}_{sub}.html", arg=arg)

        elif sub == "request":
            arg["url"] = request.args.get("url", "")
            arg["save_path"] = ModelSetting.get("default_save_path")
            arg["filename"] = ModelSetting.get("default_filename")
            arg["preset_list"] = LogicNormal.get_preset_list()
            arg["date_after"] = date.today()
            return render_template(f"{package_name}_{sub}.html", arg=arg)

        elif sub == "scheduler":
            arg["save_path"] = ModelSetting.get("default_save_path")
            arg["filename"] = ModelSetting.get("default_filename")
            arg["preset_list"] = LogicNormal.get_preset_list()
            arg["date_after"] = date.today()
            return render_template(f"{package_name}_{sub}.html", arg=arg)

        elif sub == "log":
            return render_template("log.html", package=package_name)
    except Exception as e:
        logger.error("Exception:%s", e)
        logger.error(traceback.format_exc())
    return render_template("sample.html", title=f"{package_name} - {sub}")


#########################################################
# For UI
#########################################################
@blueprint.route("/ajax/<sub>", methods=["POST"])
@login_required
def ajax(sub):
    try:
        logger.debug("AJAX: %s, %s", sub, request.values)
        ret = {"ret": "success"}

        # 공통 요청
        if sub == "setting_save":
            ret = ModelSetting.setting_save(request)

        elif sub == "scheduler":
            ret = request.form["scheduler"]
            logger.debug("scheduler:%s", ret)
            if ret == "true":
                Logic.scheduler_start()
            else:
                Logic.scheduler_stop()

        elif sub == "one_execute":
            ret = Logic.one_execute()

        elif sub == "reset_db":
            ret = Logic.reset_db()

        # UI 요청
        elif sub == "analysis":
            url = request.form["url"]
            data = LogicNormal.analysis(url)
            if data["errorCode"] == 0:
                ret["data"] = data
            else:
                ret["ret"] = "warning"
                ret["msg"] = "분석 실패"

        elif sub == "add_download":
            count = LogicNormal.download(request.form)
            ret["msg"] = f"{count}개를 큐에 추가하였습니다."

        elif sub == "list_scheduler":
            ret["data"] = LogicNormal.get_scheduler()

        elif sub == "add_scheduler":
            if LogicNormal.add_scheduler(request.form):
                ret["msg"] = "스케줄을 저장하였습니다."
            else:
                ret["ret"] = "warning"
                ret["msg"] = "플레이리스트가 아닙니다."

        elif sub == "del_scheduler":
            LogicNormal.del_scheduler(request.form["id"])
            ret["msg"] = "삭제하였습니다."

        elif sub == "del_archive":
            LogicNormal.del_archive(request.form["id"])
            ret["msg"] = "삭제하였습니다."

        return jsonify(ret)
    except Exception as e:
        logger.error("Exception:%s", e)
        logger.error(traceback.format_exc())


#########################################################
# socketio
#########################################################
def socketio_emit(cmd, data):
    socketio.emit(cmd, data, namespace=f"/{package_name}", broadcast=True)
