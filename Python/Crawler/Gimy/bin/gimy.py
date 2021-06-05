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
import datetime
import codecs

import requests
from bs4 import BeautifulSoup as bs
from loguru import logger


class GimyScrapy():
    """
    Gimy 劇迷網站爬取核心程式
    """

    def __init__(self):
        self.in_time = datetime.datetime.now().strftime("%Y-%m-%d")
        logger.add(f"../log/GimyScrapy-{self.in_time}.log")

        self.headers = {
            'authority': 'gimy.one',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://gimy.one',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,id;q=0.6',
        }

        self.hostname = 'https://gimy.one'
        self.video_id = None           # self.video_id = '200069344'
        self.vidoes = []
        self.file_path = '../output/Default_gimy'

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        self._file_path = file_path

    @property
    def video_id(self):
        return self._video_id

    @video_id.setter
    def video_id(self, video_id):
        self._video_id = video_id

    @logger.catch
    def run(self, total=1):
        """
        執行程式入口
        """
        if self.video_id:
            total += 1
            for i in range(1, total):
                num = str(i).rjust(3, '0')
                ifame, num = self.get_iframe(num, total)
                video = self.get_vidoe(ifame, num)
                self.vidoes.append(video)
                time.sleep(0.5)
            self.saveToJson()
            logger.success("結束爬取程序...")
            return True
        else:
            logger.critical("未設定影片ID...")
            return False

    @logger.catch
    def get_iframe(self, num, total):
        """
        取得 Iframe 網址
        """
        response = requests.get(
            f'{self.hostname}/v/{self.video_id}/10{num}000.html', headers=self.headers)
        t = (int(num)/(total - 1)) * 100
        logger.info(f"正在爬取: {num}， 總計需爬取: {total - 1}， 進度為： {t:.5} %")
        data = bs(response.text, 'html.parser')
        ifame = data.select('iframe')[0].get('src')
        logger.info(f"取得 {num} -> Ifame URL: {ifame}")
        return ifame, num

    @logger.catch
    def get_vidoe(self, ifame, num):
        """
        抓取 m3u8 路徑
        """
        response = requests.get(
            f'{self.hostname}{ifame}', headers=self.headers)
        data = bs(response.text, 'html.parser')
        video = data.select('source')[0].get('src')
        logger.info(f"取得 {num} -> Video Url : {video}")
        return video

    @logger.catch
    def saveToJson(self):
        '''
        將資料以Json格式存放本機
        '''
        if self.vidoes != []:
            itme_dict = {}
            for i in range(0, len(self.vidoes)):
                itme_dict[i + 1] = self.vidoes[i]
            row_json = json.dumps(itme_dict, ensure_ascii=False)
            file = codecs.open(
                f"{self.file_path}-{self.in_time}.json", 'w', encoding='utf-8')
            file.write(row_json)
            logger.success(f"資料存放於: {self.file_path}-{self.in_time}.json")
        else:
            logger.critical(" ERR: 未爬取到數據.....")
