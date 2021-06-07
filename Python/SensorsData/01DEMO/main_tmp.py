import random
import datetime
import argparse

import sensorsanalytics
from loguru import logger


# source_list = ["Yahoo", "Google", "FB", "Line", "KOL", "官網", "線下", "email"]
source_list = ["Yahoo", "Google", "Facebook", "Line", "專屬KOL連結", "官方網站"]

@logger.catch
def argParse():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=str,
                        help="project name")
    parser.add_argument("-t", "--times",
                        type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
                        help="custom times, ex: 2021-05-01")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="debug mode")
    args = parser.parse_args()
    return parser.parse_args()

@logger.catch
def fake_data_maker(i,times):
    if times:
        pass
    else:
        times = datetime.datetime.now(),
    distinct_id = 'admindemo123'
    properties = {
        '$time' : datetime.datetime.now(times),
        '$ip' : '122.116.200.11',
        'cost_amount' : random.randint(3000, 10000),
        '$utm_source' : source_list[i]
    }
    sa.track(distinct_id, 'AdCost', properties, is_login_id=True)

@logger.catch
def run(project,times):
    logger.info(f"Start...Project -> {project}")
    for i in range(0,len(source_list)):
        fake_data_maker(i,times)
    logger.success("Done")

if __name__ == "__main__":
    args = argParse()
    project = args.project
    times = args.times
    logger.add(f"log/adCostMaker.log",  rotation="100 MB")
    url = f'http://127.0.0.1:8106/sa?project={project}'
    SA_SERVER_URL = url
    SA_REQUEST_TIMEOUT = 100000
    consumer = sensorsanalytics.DefaultConsumer(SA_SERVER_URL, SA_REQUEST_TIMEOUT)
    sa = sensorsanalytics.SensorsAnalytics(consumer,enable_time_free = True)
    run(project,times)
    sa.close()

    