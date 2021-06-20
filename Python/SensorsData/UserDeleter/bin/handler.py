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

import requests
from loguru import logger

import utils
import deleter


class PipeLine():
    def __init__(self):
        self.config = utils.Config()
        self.root_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)))
        self.config_file_path = os.path.join(
            self.root_path, "../conf/config.ini")
        self.config = self.config.get_config(
            section="sa", config_path=self.config_file_path)
        self.username = None
        self.password = None
        self.sql = None
        self.limit = None

    @logger.catch
    def conf_check(self):
        """
        設定檔檢查
        """
        logger.debug("檢查 config.ini 語法是否正確...")
        check_list = ['sa_url', 'project', 'user_name',
                      'passwd', 'sa_source_link_url']
        for i in check_list:
            logger.debug(f"檢查 {i} 是否存在...")
            if i not in self.config.keys():
                logger.critical(f"{i} 區塊遺失，請檢查 conf/config.ini 設定檔")
                return False
        return True

    @logger.catch
    def conf_parser(self):
        """
        設定檔解析
        """
        self.sql = self.config["sql"]
        self.limit = self.config["limit"]
        if self.sql:
            self.sql = self.sql.split(";")[0]
            a, b = '\n', ' '
            logger.info(f"使用自定義刪除條件 -> 條件為:  {self.sql.strip().replace(a,b)}")
            self.sql = f"where  {self.sql.strip().replace(a,b)}"
        if self.limit:
            try:
                self.limit = int(self.limit)
                if self.limit > 100000:
                    self.limit = 100000
                    logger.warning(f"一次最多只能刪除10萬筆..")
                if self.limit < 1:
                    self.limit = 1
                    logger.warning(f"最少會刪除1筆..")
            except Exception as _:
                logger.error(f"ERR , limit 請輸入數字或空白 -> {_}")
                exit(1)
        else:
            self.limit = 1

    @logger.catch
    def get_token(self):
        """
        取得sensorsdata-toke
        """
        uri = f'/api/v2/auth/login'
        data = {
            "account_name": self.config['user_name'],
            "password": self.config['passwd']
        }
        params = {
            'project': self.config['project'],
            'is_global': 'true'
        }
        token = self.request(params, uri, data)
        return token

    @logger.catch
    def request(self, params, uri, data):
        """
        送出請求
        """
        headers = {'content-type': 'application/json'}
        try:
            response = requests.post(
                self.config['sa_url'] + uri, params=params, data=json.dumps(data), headers=headers, verify=False ,timeout = 5)
        except Exception as _:
            logger.error(f"ERR  請檢查神策Web伺服器是否正確，程式終止 -> {_}")
            exit(1)
        if response.status_code == 200:
            token = json.loads(response.text)["session_id"]
            return token
        else:
            logger.error(f"回傳狀態：{response.status_code}, {response.text}")
            logger.error(f"請檢查項目、帳號及密碼是否正確....")
            exit(1)

    @logger.catch
    def run(self):
        """
        執行主程序
        """
        if self.conf_check():
            self.conf_parser()
            sad = deleter.SaDeleter()
            sad.url = self.config['sa_source_link_url']
            sad.project = self.config['project']
            sad.sa_ip = self.config['sa_url']
            sad.sql = f"SELECT first_id FROM users {self.sql} limit {self.limit}"
            sad.token = self.get_token()
            sad.pipline()
            return True, self.config['project']
        else:
            return False, ""
