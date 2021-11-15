import os
import argparse

from loguru import logger

import my_utily
import data_backup

@logger.catch
def argParse():
    parser = argparse.ArgumentParser(prog="Api 數據備份工具",
                                     description="Events、Users及Items 等各表備份， 詳請參閱README.md")
    parser.add_argument("project", type=str,
                        help="project name")
    parser.add_argument("tables", 
                        type=str,
                        help="Table name")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="debug mode")
    args = parser.parse_args()
    return parser.parse_args()



if __name__ == '__main__':
    root_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)))
    args = argParse()
    tables = ['events','users','items']
    if args.tables in tables: 
        logger.add(f"{root_path}/../log/dataBackUp.log", rotation="400 MB",level="INFO")
        token = my_utily.TokenGetter().get_token()
        data = data_backup.ApiBackUP()
        data.types = args.tables
        data.project = args.project
        data.token = token
        totle = data.run()
    else:
        logger.warning("Tables Should be 'events / users / itmes'")
    
