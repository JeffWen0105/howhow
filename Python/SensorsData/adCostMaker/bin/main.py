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
import datetime
import argparse

from loguru import logger

import handler

@logger.catch
def argParse():
    parser = argparse.ArgumentParser(prog="adCostMaker 工具",
                                     description="寫入AdCost事件 ， 詳請參閱README.md")
    parser.add_argument("project", type=str,
                        help="project name")
    parser.add_argument("-t", "--times",
                        type=lambda s: datetime.datetime.strptime(
                            s, '%Y-%m-%d'),
                        help="custom times, ex: 2021-05-01  ")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="debug mode")
    args = parser.parse_args()
    return parser.parse_args()


if __name__ == "__main__":
    root_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)))
    args = argParse()
    logger.add(f"{root_path}/log/adCostMaker.log", rotation="100 MB",level="INFO")
    logger.info("程序開始...")
    ad = handler.PipeLine(args.project)
    status = ad.run(args)
    if status:
        logger.success(f"程序結束，請至神策數據的{args.project}項目查看")
    else:
        logger.error("程序異常結束..")