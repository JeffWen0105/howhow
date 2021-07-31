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

import sys
import datetime

import requests
from bs4 import BeautifulSoup as bs
from loguru import logger

class PttCrawler:
    def __init__(self):
        self.domain = 'https://www.ptt.cc'
        self.title = []
        self.url = []

    @logger.catch
    def startRequests(self):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'}
        rs = requests.session()
        res = rs.get(url=self.domain+self.uri,
                     headers=header, cookies={'over18': '1'})
        if res.status_code != 200:
            logger.critical(f'response status is not 200 ({res.status_code})')
            return None
        else:
            html_data = res.text
            return html_data

    @logger.catch
    def parse(self, html_data):
        logger.info(f"解析數據中...")
        soup = bs(html_data, 'html.parser')
        self.uri = soup.findAll(attrs={"class": 'wide'})[1].get('href')
        yesterday = datetime.datetime.now()+datetime.timedelta(days=-1)
        today = datetime.datetime.now()
        for _ in soup.findAll(attrs={"class": ['r-list-sep', 'r-ent']}):
            if _.attrs['class'][0] == 'r-list-sep':
                break
            else:
                for all_div in _.findAll('div', attrs={"class": 'title'}):
                    title_tmp = all_div.text
                    title_tmp = title_tmp.replace(
                        '\n', '').replace('\u3000', '')
                    if '(本文已被刪除)' in title_tmp:
                        continue
                    if 'Re:' in title_tmp:
                        continue
                    if not '[情報]' in title_tmp:
                        continue
                    get_data = _.find(attrs={"class": 'date'}).text
                    if get_data == yesterday.strftime(" %-m/%d") or get_data == today.strftime(" %-m/%d"):
                        self.title.append(title_tmp)
                    for url_a in all_div.findAll('a'):
                        url_tmp = url_a.get('href')
                        url_tmp = f"https://www.ptt.cc{url_tmp}"
                        if get_data == yesterday.strftime(" %-m/%d") or get_data == today.strftime(" %-m/%d"):
                            self.url.append(url_tmp)

    @logger.catch
    def run(self):
        logger.info(f"開始爬取PTT-Lifeismoney版...")
        self.uri = '/bbs/Lifeismoney/index.html'
        get_times = 0
        while get_times < 3:
            data = self.startRequests()
            self.parse(data)
            get_times += 1
        if len(self.title) == 0 or self.url == 0:
            logger.critical("解析資料失敗，強制停止程序...")
            sys.exit(1)
        return self.title , self.url
