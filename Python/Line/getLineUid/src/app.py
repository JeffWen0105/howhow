# =======================================================================
# Author: Jeff
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# If not, see <http://www.gnu.org/licenses/>.
# =======================================================================

import json
import datetime

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import linebot
from flask import Flask, request, abort, render_template, jsonify
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_apscheduler import APScheduler
from loguru import logger

import db


class Config:
    SCHEDULER_API_ENABLED = False
    SCHEDULER_TIMEZONE = 'Asia/Taipei'


logger.add("log/line.log")
app = Flask(__name__, static_folder="app/static/",
            template_folder="app/static/")
app.config['TEMPLATES_AUTO_RELOAD'] = True
api = Api(app)
CORS(app)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


line_bot_api = LineBotApi("")
handler = WebhookHandler("")



@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


@app.route("/callback", methods=['POST'])
def callback():

    body = request.get_data(as_text=True)
    try:
        body = json.loads(body)
        parse_data(body)
    except Exception as _:
        pass
    return 'OK'

def make_rich_menu():
    query = db.MyDB()
    quertData = query.select_data()
    if quertData:
        try:
            global line_bot_api
            global handler
            line_bot_api = LineBotApi(quertData[0])
            handler = WebhookHandler(quertData[1])
            rich_menu_to_create = RichMenu(
                size=RichMenuSize(width=1200, height=810),
                selected=False,
                name="showMeUid",
                chat_bar_text="showMeUid",
                areas=[RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=1200, height=810),
                    action=PostbackAction(data="showMeUid", label="showMeUid")
                )]
            )
            rich_menu_id = line_bot_api.create_rich_menu(
                rich_menu=rich_menu_to_create)
            print(rich_menu_id)
            with open("/home/howhow/app/static/img/start.jpg", 'rb') as f:
                line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", f)
            line_bot_api.set_default_rich_menu(rich_menu_id)
            return rich_menu_id
        except Exception as _:
            logger.warning(f"Something happend : {_}")
            return {"Info": {"Message": "Get an Info", "ERR": str(_)}}, 400

def check_data():
    logger.info(f"Start Delete Data...{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
    query = db.MyDB()
    try:
        quertData = query.select_data()
        line_bot_api = LineBotApi(quertData[0])
        default_id = line_bot_api.get_default_rich_menu()
        line_bot_api.delete_rich_menu(default_id)
        logger.success("Delet Rich Menu...")
        line_bot_api.set_webhook_endpoint(quertData[3])
        logger.success("設定回原本callback...")

    except Exception as _:
        logger.warning(f"Something happend : {_}")
    query.remove_data()
    query = db.MyDB()
    quertData = query.select_data()
    scheduler.delete_job(id="01")
    logger.success("Delet scheduler..")


def parse_data(body):
    query = db.MyDB()
    quertData = query.select_data()
    try:
        rawdata = body
        if quertData:
            line_bot_api = LineBotApi(quertData[0])
            if rawdata['events'][0]['type'] == 'postback':
                if rawdata['events'][0]['postback']['data'] == 'showMeUid':
                    text = f"HI，您的 Line UserID 為: \n {rawdata['events'][0]['source']['userId']}  \n\nPowered by HowHowWen .."
                    pushId = rawdata['events'][0]['source']['userId']
                    line_bot_api.push_message(pushId, TextSendMessage(text=text))
            if rawdata['events'][0]['type'] == 'message':
                text = rawdata['events'][0]['message']['text']
                if text.replace(" ", '').upper() == "MYID":
                    if rawdata['events'][0]['source']['type'] == 'group':
                        text = f"HI，您的 Line GroupID 為: \n {rawdata['events'][0]['source']['groupId']}  \n\nPowered by HowHowWen .."
                        pushId = rawdata['events'][0]['source']['groupId']
                    elif rawdata['events'][0]['source']['type'] == 'room':
                        text = f"HI，您的 Line RoomID 為: \n {rawdata['events'][0]['source']['roomId']}  \n\nPowered by HowHowWen .."
                        pushId = rawdata['events'][0]['source']['roomId']
                    else:
                        text = f"HI，您的 Line UserID 為: \n {rawdata['events'][0]['source']['userId']}  \n\nPowered by HowHowWen .."
                        pushId = rawdata['events'][0]['source']['userId']
                    line_bot_api.push_message(pushId, TextSendMessage(text=text))
    except Exception as _:
        logger.warning(f"ParseData Warn: {_}")


class Info(Resource):
    def get(self):
        query = db.MyDB()
        quertData = query.select_data()
        if quertData:
            f = lambda x : len(x) * '*'
            d = lambda s: (datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S') 
            + datetime.timedelta(minutes=5) ).strftime('%Y-%m-%d %H:%M:%S')
            output = {
                "Token": f(quertData[0]),
                "Uid": f(quertData[1]),
                "name": quertData[2],
                "datatime": f"CST+8 {quertData[4]}",
                "endtime" : f"CST+8 {d(quertData[4])}"
            }
            return {"Info": {"Message": "Get an Info", "output": output}}, 200
        else:
            return {}, 200

    def post(self):
        query = db.MyDB()
        if not query.select_data():
            data = request.get_json()
            token = data['Token']
            secret = data['secret']
            name = data['name']    
            line_bot_api = LineBotApi(token)
            try:
                webhook = line_bot_api.get_webhook_endpoint()
            except:
                return {"Info": {"Message": "Token is not Right.."}}, 433
            query.insert_data(token, secret, name)
            your_end_point = webhook.endpoint
            query.update_data(token, your_end_point)
            line_bot_api.set_webhook_endpoint('https://lineuid.howhow.tk/callback')
            try:
                scheduler.add_job(
                    func=check_data,
                    trigger="interval",
                    minutes=5,
                    id="01",
                    name="howhow"
                )
                logger.success(f"AddJOB : -> scheduler")
            except Exception as _:
                logger.critical(f"Post Exception: {_}")
                query.remove_data()
                return {"Info": {"Message": "something wrong.."}}, 504
            make_rich_menu()
            logger.info(
                f"start scheduler...{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
            return {"product": {"Message": "Update a new Info"}}, 201
        else:
            return {"Info": {"Message": "Waiting..."}}, 433


api.add_resource(Info, '/info')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
