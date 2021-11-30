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
import copy
import time
import hashlib
import argparse
import datetime

import requests
from loguru import logger
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs


class JkfGetting():

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
    def get_main_page(self, pages):      
        rawdata = self.start_get_requests(
            headers=self.headers, url=f"https://www.jkforum.net/forum-520-{pages}.html")
        logger.info(f"Start get page -> https://www.jkforum.net/forum-520-{pages}.html")
        soup = self.bs4_soup(rawdata)
        small_imgs_list = [i.get('style').split(';')[2].split(
            'url')[-1].split("\'")[1] for i in soup.select("#waterfall .z")]
        domain = 'https://www.jkforum.net/'
        small_urls_list = [domain + i.get("href")
                           for i in soup.select(".xw0 a")]
        small_title_list = [i.get("title") for i in soup.select(".xw0 a")]
        small_date_list = [ i.get("title") for i in soup.select(".xs0 + .xs0 span")]
        # 日期判斷
        if len(small_date_list) != len(small_title_list):
            [
                small_date_list.append(i.text)
                for i in soup.select(".xs0 + .xs0")
                if "天前" not in i.text
            ]
        hash_ids_list = []
        for i in small_title_list:
            hash_object = hashlib.sha256(bytes(i, 'UTF-8'))
            hex_dig = hash_object.hexdigest()
            hash_ids_list.append(hex_dig)
        data = self.make_dict(
            url_list=small_urls_list,
            title_list=small_title_list,
            hash_id_list=hash_ids_list,
            img_list=small_imgs_list,
            date_list=small_date_list
        )
        logger.info(f"Get Data count(1) -> {len(data)}")
        return data

    @logger.catch
    def make_dict(self, url_list, title_list, hash_id_list, img_list, date_list):
        data = []
        _ = 0
        c  = lambda s: datetime.datetime.strptime(s, '%Y-%m-%d')
        while _ < len(hash_id_list):
            data.append({
                "hashId": hash_id_list[_],
                "title": title_list[_],
                "img": img_list[_],
                "url": url_list[_],
                'dateTime':  c(date_list[_]),
                'createdAt' : datetime.datetime.now()
            })
            _ += 1
        return data

    @logger.catch
    def run(self, pages=1):
        self.data = self.get_main_page(pages)

@logger.catch
def argParse():
    parser = argparse.ArgumentParser(prog="JKF主頁面爬蟲工具",
                                     description="將JKF 網路美女主頁爬取並寫入至 Mongo (預設為本地)， 詳請參閱README.md")
    parser.add_argument("pages", type=int,
                        help="How Many Pages You Want ??")
    args = parser.parse_args()
    return parser.parse_args()

@logger.catch
def start(pages):
    jkf_getting = JkfGetting()
    jkf_getting.run(pages)
    insert_data = copy.deepcopy(jkf_getting.data)
    logger.info(f"Start insert Data to MongoDB")
    insert_data_fun(insert_data)

@logger.catch
def insert_data_fun(data):
    try:
        for i in data:
            try:
                collection.insert_one(i)
                logger.success(f"{i}")
            except Exception as _:
                logger.debug(f"ERR {_}")
    except Exception as _:
        print(_)

@logger.catch
def run(times=1):
    if times < 1:
        times = 1
    for i in range(1, times+1):
        start(i)
        time.sleep(0.5)
    logger.success("SUCCESS ~~")


if __name__ == "__main__":
    if not os.getenv('myMongoIP'):
        my_mongo_ip = "127.0.0.1"
    else:
        my_mongo_ip = os.getenv('myMongoIP')
    logger.add("logs/howhow.log",level="INFO", rotation="350 MB")
    args = argParse()
    client = MongoClient(my_mongo_ip, 27017)
    db = client["howhow"]
    collection = db["JKF"]
    collection.create_index("hashId", unique=True)
    pages = int(args.pages)
    run(pages)
    client.close()

