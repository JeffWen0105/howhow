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


import random
import datetime

import sensorsanalytics
from loguru import logger


class Default():
    def __init__(self, project):
        SA_SERVER_URL = f'http://127.0.0.1:8106/sa?project={project}'
        logger.debug(f"神策初始化，導入位置： {SA_SERVER_URL}")
        SA_REQUEST_TIMEOUT = 100000
        consumer = sensorsanalytics.DefaultConsumer(
            SA_SERVER_URL, SA_REQUEST_TIMEOUT)
        self.sa = sensorsanalytics.SensorsAnalytics(
            consumer, enable_time_free=True)

    @logger.catch
    def fake_data_maker(self,source, times, cost_min, cost_max):
        """
        一般模式寫入
        """
        if times:
            pass
        else:
            times = datetime.datetime.now()
        distinct_id = 'admindemo123'
        properties = {
            '$time': times,
            '$ip': '122.116.200.11',
            'cost_amount': random.randint(cost_min, cost_max),
            '$utm_source': source
        }
        self.sa.track(distinct_id, 'AdCost', properties, is_login_id=True)
        logger.debug(
            f"{distinct_id}, 'AdCost', {properties}, is_login_id=True")

    @logger.catch
    def close(self):
        self.sa.close()


class Debug():
    def __init__(self, project):
        SA_SERVER_URL = f'http://127.0.0.1:8106/sa?project={project}'
        logger.debug(f"神策初始化，導入位置： {SA_SERVER_URL}")
        SA_REQUEST_TIMEOUT = 100000
        SA_DEBUG_WRITE_DATA = True
        consumer = sensorsanalytics.DebugConsumer(
            SA_SERVER_URL, SA_DEBUG_WRITE_DATA, SA_REQUEST_TIMEOUT)
        self.sa = sensorsanalytics.SensorsAnalytics(
            consumer, enable_time_free=True)

    @logger.catch
    def fake_data_maker(self,source, times, cost_min, cost_max):
        """
        除錯模式
        """
        if times:
            pass
        else:
            times = datetime.datetime.now()
        distinct_id = 'admindemo123'
        properties = {
            '$time': times,
            '$ip': '122.116.200.11',
            'cost_amount': random.randint(cost_min, cost_max),
            '$utm_source': source
        }
        self.sa.track(distinct_id, 'AdCost', properties, is_login_id=True)

    @logger.catch
    def close(self):
        self.sa.close()
