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

import time
import subprocess

from flask import Flask, render_template, Response, abort, request
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_apscheduler import APScheduler
from loguru import logger

from bin import db

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__, static_folder="app/static/",
            template_folder="app/static/")
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
app.config.from_object(Config())
api = Api(app)
CORS(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
logger.add("log/bot.log")

@app.route("/", methods=["GET"])
def root():
    return render_template("index.html", log=flask_logger())

@app.route("/run", methods=["GET"])
def run():
    commed = """
            sh start.sh
        """
    process = subprocess.run(
        commed, shell=True, stdout=subprocess.PIPE, timeout=60)
    if process.returncode == 0:
        return render_template("index.html", log=flask_logger())
    return abort(404)


def flask_logger():
    with open('log/bot.log', 'r') as read_obj:
        lines = read_obj.readlines()
        lines = reversed(lines)
        i = 1
        for data in lines:
            if "SUCCESS" in data:
                category = "success"
                yield data, category
            elif "INFO" in data:
                category = "info"
                yield data, category
            elif "WARNING" in data:
                category = "warning"
                yield data, category
            elif "CRITICAL" in data:
                category = "danger"
                yield data, category
            else:
                if data != "":
                    category = "dark"
                    yield data, category
            i += 1
            if i > 15:
                break

@scheduler.task('cron', id='life_money', minute='30', hour='10')
def howhow_job():
    commed = """
            sh start.sh
        """
    process = subprocess.run(
        commed, shell=True, stdout=subprocess.PIPE, timeout=60)
    if process.returncode == 0:
        logger.success("排程結束...")

class Info(Resource):
    def get(self):
        query = db.MyDB()
        status, Token, uid = query.select_db()
        if status:
            output = {
            "Token": Token,
            "Uid": uid
            }
            return {"Info": {"Message": "Get an Info", "output": output}}, 200
        else:
            return {"Info": {"Message": "Can't find the Info"}}, 404

    def post(self):
        query = db.MyDB()
        data = request.get_json()
        Token = data['Token']
        uid = data['uid']
        query.insert_db(Token,uid)
        return {"product": {"Message": "Update a new Info"}}, 201

api.add_resource(Info, '/info')

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=5000)
