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

from loguru import logger

import utils
import maker


class PipeLine():
    def __init__(self, project):
        self.config = utils.Config()
        self.root_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)))
        self.config_file_path = os.path.join(
            self.root_path, "../conf/config.ini")
        self.project = project

    @logger.catch
    def conf_check(self):
        """
        設定檔檢查
        """
        try:
            logger.debug("檢查 config.ini 語法是否正確...")
            self.config = self.config.get_config(
                section=self.project, config_path=self.config_file_path)
            check_list = ['source', 'amount_min', 'amount_max']
            for i in check_list:
                logger.debug(f"檢查 {i} 是否存在 {self.project}...")
                if i not in self.config.keys():
                    logger.critical(f"該項目 {_} 區塊遺失，請檢查 conf/config.ini 設定檔")
                    return False
            return True

        except Exception as _:
            logger.critical(f"conf/config.ini 找到不該項目，請重新檢查, ERR: {_}")
            return False

    @logger.catch
    def conf_parser(self):
        """
        設定檔解析
        """
        logger.debug(f"{self.project} 參數解析中..")
        source = self.config["source"]
        source_list = [
            i.strip() for i in source.split(',')
        ]
        if source_list == [""]:
            source_list = ["Yahoo", "Google", "Facebook", "Line"]

        try:
            cost_min = int(self.config["amount_min"])
        except:
            cost_min = 3000
        try:
            cost_max = int(self.config["amount_max"])
        except:
            cost_max = 10000
        if cost_min > cost_max:
            cost_min, cost_max = cost_max, cost_min
        elif cost_min < 2:
            cost_min = 1
        elif cost_max > 10000000:
            cost_max = 10000000
        self.source_list = source_list
        self.cost_max = cost_max
        self.cost_min = cost_min
        logger.debug(
            f"source_list : {self.source_list}, cost_max : {self.cost_max}, cost_min : {self.cost_min}")

    @logger.catch
    def run(self, args):
        """
        執行主程序
        """
        if self.conf_check():
            self.conf_parser()
            if args.times:
                times = args.times
            else:
                times = ''
            if args.debug:
                logger.info("Debug模式啟動，數據不會寫入")
                mk = maker.Debug(self.project)
                for i in self.source_list:
                    mk.fake_data_maker(
                        source=i,
                        times=times,
                        cost_min=self.cost_min,
                        cost_max=self.cost_max
                    )
                mk.close()
            else:
                logger.info("使用一般模式，數據寫入神策")
                mk = maker.Default(self.project)
                for i in self.source_list:
                    mk.fake_data_maker(
                        source=i,
                        times=times,
                        cost_min=self.cost_min,
                        cost_max=self.cost_max
                    )
                mk.close()
            return True
        else:
            return False
