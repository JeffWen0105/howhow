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

from loguru import logger

import db
import paser_data
import push


if __name__ == "__main__":
    logger.add("log/bot.log")
    query = db.MyDB()
    status, Token, uid = query.select_db()
    if status:
        get_data = paser_data.PttCrawler()
        bot = push.BotPush()
        bot.title, bot.url = get_data.run()
        bot.push_uid = uid
        bot.Token = Token
        status, _ = bot.run()
        if status:
            logger.success("成功推送，請至 Line 上查看～")
        else:
            logger.critical(f"Err: {_}")
            status = True
    else:
        logger.critical(f"請先建立 Token 及 line push id")
        status = False
    query.close_db()
    if status:
        exit(0)
    else:
        exit(1)
