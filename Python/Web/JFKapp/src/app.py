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

import os
import json
import subprocess

from flask import Flask, render_template, request, session
from flask_cors import CORS
from flask_restful import Resource, Api
from loguru import logger

import db
import myPyMongo

logger.add("logs/howhow.log",level="INFO", rotation="350 MB")
app = Flask(__name__, static_folder="app/static/",
            template_folder="app/static/")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "howhow_love_you_1991"
api = Api(app)
CORS(app)
query = db.MyDB()
query.remove_data()

if not os.getenv('userName'):
    user_name = 'howhow'
else:
    user_name = os.getenv('userName')
if not os.getenv('userPasswd'):
    user_passwd = '800105'
else:
    user_passwd = os.getenv('userPasswd')

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        if name != user_name:
            return render_template("home.html", state=404)
        if password == user_passwd:
            session['name'] = user_name
            return render_template("home.html", state=200)
        else:
            return render_template("home.html", state=404)
    else:
        return render_template("home.html", state=200)

@app.route('/logout')
def logout():
    session.clear()
    query = db.MyDB()
    query.remove_data()
    return render_template("home.html", state=200)

class Info(Resource):
    def get(self, number=0):
        number = int(number)
        query = myPyMongo.PyMongoDB()
        getData = query.find(number)
        if getData:
            return {"Info": {"Message": "Get an Info", "output": getData}}, 200
        else:
            return {}, 200

    def post(self, number):
        data = request.get_json()
        query = db.MyDB()
        if query.select_data():
            return {"Info": {"Message": "Server Busy ...", "output": "503"}}, 503
        else:
            query.insert_data()
            command = f"python3 postData.py {data['hashId']}"
            process = subprocess.run(
                command, shell=True, stdout=subprocess.PIPE, timeout=240)
            if process.returncode == 0:
                query.remove_data()
                return {"Info": {"Message": "SUCCESS ~~", "output": "200"}}, 200
            else:
                query.remove_data()
                return {"Info": {"Message": "Something Error，請查看後端 Log ..", "output": "500"}}, 500


    def delete(self, number):
        query = db.MyDB()
        query.remove_data()
        return {}, 200


api.add_resource(Info, '/info/<string:number>')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
