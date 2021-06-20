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
import time
import sys
import subprocess

import requests
from formatImporter import sensorsanalytics
from loguru import logger


class SaDeleter():
    def __init__(self):
        pass

    @property
    def sql(self):
        return self._sql

    @sql.setter
    def sql(self, sql):
        self._sql = sql

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, project):
        self._project = project

    @property
    def sa_ip(self):
        return self._sa_ip

    @sa_ip.setter
    def sa_ip(self, sa_ip):
        self._sa_ip = sa_ip

    def pipline(self):
        self.init_sa()
        self.get_data()
        self.delete_data()
        self.format_importer()

    @logger.catch
    def init_sa(self):
        SA_BULK_SIZE = 4096
        command = f"rm -rf tmp/*"
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, timeout=5)
        try:
            requests.get(f"{self.url}/sa?project={self.project}" ,timeout = 5)
        except Exception as _:
            logger.error(f"ERR : 發送失敗，請檢查數據接收地址設定，程式終止 -> : {_}")
            exit(1)
        consumer = sensorsanalytics.ConcurrentLoggingConsumer(
            'tmp/data.log', SA_BULK_SIZE)
        self.sa = sensorsanalytics.SensorsAnalytics(consumer)

    @logger.catch
    def get_data(self):
        headers = {
            'sensorsdata-token': f'{self.token}',
        }
        params = (
            ('project', f'{self.project}'),
            ('q', f'{self.sql}'),
            ('format', f'json'),
        )
        logger.debug(f"URL : {self.sa_ip}, Project : {self.project}, SQL : {self.sql}")
        logger.info("取得使用者資訊中.....")
        try:
            response = requests.post(
                f'{self.sa_ip}/api/sql/query', params=params, headers=headers,timeout = 60)
            self.rawdata = response.text.split('\n')
        except Exception as _:
            logger.error(f"ERR  請檢查神策Web伺服器是否正確，程式終止 -> : {_}")

    @logger.catch
    def delete_data(self):
        user_name = []
        for _ in range(0, len(self.rawdata)):
            try:
                user_name.append(json.loads(self.rawdata[_])['first_id'])
            except:
                pass
        if len(user_name) > 0:
            x = 0
            for _ in user_name:
                self.sa.profile_delete(_)
                x += 1
            logger.success(f"總計刪除{x}筆資料")
            self.sa.close()
        else:
            logger.error("無此條件，請重新設定.....程序結束")
            self.sa.close()
            exit(1)

    @logger.catch
    def format_importer(self):
        logger.info("發送刪除數據.....")
        command = f"python3 bin/formatImporter/format_importer.py json --url '{self.url}/sa?project={self.project}' --path 'tmp/' "
        try:
            process = subprocess.run(
                command, shell=True, stdout=subprocess.PIPE, timeout=18000)
        except Exception as _:
            logger.warning(f"ERR : {_} ")
        if process.returncode == 0:
            logger.success(f"刪除數據發送成功....")
            command = f"rm -rf tmp/*"
            process = subprocess.run(
                command, shell=True, stdout=subprocess.PIPE, timeout=60)
            command = f"rm -rf bin/formatImporter/format_importer.log"
            process = subprocess.run(
                command, shell=True, stdout=subprocess.PIPE, timeout=60)
        else:
            logger.warning("ERR : 發送失敗，請檢查數據接收地址設定～～ ")
