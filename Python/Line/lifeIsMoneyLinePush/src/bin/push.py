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

import copy
import json

import requests
from loguru import logger

def raw_json():
    data = json.loads("""
    {"to":"","messages":[{"type":"flex","altText":"優惠推送來拉，小資族省起來～","contents":{"type":"bubble","hero":{"type":"image","url":"https://cdn.pixabay.com/photo/2017/11/24/10/43/ticket-2974645_1280.jpg","size":"full","aspectRatio":"20:13","aspectMode":"cover"},"body":{"type":"box","layout":"vertical","contents":[{"type":"box","layout":"vertical","margin":"lg","spacing":"sm","contents":[]}]},"footer":{"type":"box","layout":"vertical","spacing":"sm","contents":[{"type":"button","style":"link","height":"sm","action":{"type":"uri","label":"HowHowWen の 官網","uri":"https://jeffwen0105.com/lifemoneylinepush"}}],"flex":0}}}]}
    """)
    return data

def raw_message():
    messages_list = json.loads("""
    {"type":"box","layout":"baseline","spacing":"sm","contents":[{"type":"text","text":"情報：","wrap":true,"color":"#8E8E8E","size":"xs","flex":0,"style":"normal","margin":"none"},{"type":"text","text":"","wrap":true,"color":"#0080FF","size":"xs","flex":1,"action":{"type":"uri","label":"action","uri":""},"decoration":"underline","margin":"none","offsetEnd":"xs"}]}
    """)
    return messages_list

class BotPush():
    def __init__(self):
        self.title = []
        self.url = []
        self.Token = ""
        self.push_uid = ""

    @logger.catch
    def json_maker(self):
        logger.info(f"產生Json格式")
        data = raw_json()
        data['to'] = self.push_uid
        messages_list = data['messages'][0]["contents"]['body']['contents'][0]['contents']
        message = raw_message()
        for i in range(0, len(self.title)):
            message['contents'][1]['text'] = f"{self.title[i].split('情報')[1].split(']')[1]}"
            message['contents'][1]['action']['uri'] = f"{self.url[i]}"
            
            tmp = copy.deepcopy(message)
            messages_list.append(tmp)
        logger.debug(f"總計有 {len(self.title)} 個情報 -> {self.title[0]} ....")
        return json.dumps(data, ensure_ascii=False)

    @logger.catch
    def push(self, data):
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.Token}"
        }
        res = requests.post(url, data=data.encode("UTF-8"), headers=headers)
        if res.status_code == 200:
            return True, None
        else:
            return False, res.text

    @logger.catch
    def run(self):
        data = self.json_maker()
        status, _ = self.push(data=data)
        return status, _
