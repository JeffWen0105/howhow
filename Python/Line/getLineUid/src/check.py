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

import datetime

from loguru import logger

import db

def check():
    query = db.MyDB()
    info = query.select_data()
    if info != "":
        right_now = datetime.datetime.now()
        get_time = (datetime.datetime.strptime(info[-1], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=6))
        try:
            if right_now > get_time :
                query.remove_data()
                logger.warning("Deleted by Crontab , something Warn...")
        except Exception as _:
            logger.critical(f"_")


if __name__ == "__main__":
    logger.add("log/line_err.log")
    check()
    
 
