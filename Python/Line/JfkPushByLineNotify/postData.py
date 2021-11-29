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

from logging import log
import os
import time
import json
import argparse

import requests
from loguru import logger
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient


class JkfContextGetting():

    def __init__(self):
        if not os.getenv('JKFcookie'):
            logger.critical(f"環境變數：JKFcookie 沒有設定，請參考 README.MD，請先完成設定")
            os._exit(1) 

        self.headers = {
            'authority': 'www.jkforum.net',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44',
            'referer': 'https://www.jkforum.net',
            'accept-language': 'zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cookie': os.getenv('JKFcookie'),
        }
        self.data = []

    @logger.catch
    def start_get_requests(self, headers, url):
        response = requests.get(url=url, headers=headers)
        return response.text

    @logger.catch
    def bs4_soup(self, data):
        soup = bs(data, 'html.parser')
        return soup

    @logger.catch
    def get_context_page(self, data_dict):
        rawdata = self.start_get_requests(
            headers=self.headers, url=f"{data_dict['url']}")
        soup = self.bs4_soup(rawdata)
        site_imgs = [i.get("file") for i in soup.select(".zoom")]
        data = {
            "imgs": site_imgs,
            "title": data_dict["title"],
            "hashId": data_dict["hashId"],
            "url": data_dict["url"]
        }
        return data

    @logger.catch
    def run(self, data_dict):
        data = self.get_context_page(data_dict)
        return data


class NotifyPost:

    def __init__(self, token):
        self.headers = {
            'Authorization': f'Bearer {token}'
        }
        self.url = "https://notify-api.line.me/api/notify"

    @logger.catch
    def post_data(self, data):
        payload = {
            'message': data['title'],
        }
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload)
        if len(data['imgs']) ==0:
            logger.critical(f"爬取失敗... 請檢查 Cookies 或是更換 user-agent (第45行) ～～")
            os._exit(1)
        logger.info(f"{data['title']} ->總計{len(data['imgs']) -1}張圖")
        for i in range(0,len(data['imgs'])):
            payload = {
                'message': f"\n第:{i+1}張美女圖，總計{len(data['imgs'])}張圖",
                'imageFullsize': data['imgs'][i],
                'imageThumbnail': data['imgs'][i],
                'notificationDisabled': True
            }
            response = requests.request(
                "POST", self.url, headers=self.headers, data=payload)
            time.sleep(1)
        logger.success("發送成功 ～")

@logger.catch
def argParse():
    parser = argparse.ArgumentParser(prog="發送網路美女圖工具",
                                     description="讀取 Mongodb (預設本地）metadata，並爬取美女圖後發送至 Line上， 詳請參閱README.md")
    parser.add_argument("HashId", type=str,
                        help="HashId")
    args = parser.parse_args()
    return parser.parse_args()

@logger.catch
def get_detail(uid):
    jkf_context_getting = JkfContextGetting()
    rawdata = collection.find_one({"hashId": uid})
    if rawdata:
        data = jkf_context_getting.run(rawdata)
        return data
    else:
        return False

@logger.catch
def post_data(data):
    notify_post = NotifyPost(token)
    notify_post.post_data(data)


@logger.catch
def run(uid):
    data = get_detail(uid)
    if data:
        post_data(data)
    else:
        logger.warning(f"找不到對應 id ...")


if __name__ == "__main__":
    if not os.getenv('myMongoIP'):
        my_mongo_ip = "127.0.0.1"
    else:
        my_mongo_ip = os.getenv('myMongoIP')
    args = argParse()
    logger.add("logs/howhow.log",level="INFO", rotation="350 MB")
    client = MongoClient(my_mongo_ip, 27017)
    db = client["howhow"]
    collection = db["JKF"]
    token = os.getenv('LineToken')
    if not token:
        logger.critical(f"環境變數： LineToken 沒有設定，請參考 README.MD，請先完成設定")
        os._exit(1)
    HashId = args.HashId
    run(HashId)
    client.close()

