import os

import requests
from loguru import logger

import utils


class Query:

    def __init__(self):
        config = utils.config()
        root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))
        config_file_path = os.path.join(root_path, "../sql.ini")
        self.sa_config = config.get_config(
            section="sa", config_path=config_file_path)
        self.events_sql_config = config.get_config(
            section="events_sql", config_path=config_file_path)
        self.users_sql_config = config.get_config(
            section="users_sql", config_path=config_file_path)

    def request(self, uri, token, project, sql, format, times):
        url = f"http://{uri}:8107/api/sql/query?token={token}&project={project}"
        print("url", url)
        payload = {'q': f'{sql} /*MAX_QUERY_EXECUTION_TIME=1800*/',
                   'format': format}
        try:
            logger.info("RUNNING: {sql}")
            response = requests.request("POST", url, data=payload)
            if format == "event_json":
                file_name="event"
            else:
                file_name="profile"
            file = f"output/{file_name}_{times}.json"
            with open(file, "w", encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f'Saveing -> {file}')

        except Exception as _:
            logger.critical(f"ERR: {_} ; SQL syntax: {sql}")

    def get_event(self):
        sa = self.sa_config
        sa_ip = sa['ip']
        sa_token = sa['token']
        sa_project = sa['project']
        events_sql = self.events_sql_config
        times = 1
        for i in events_sql:
            self.request(uri=sa_ip, token=sa_token, project=sa_project,
                         sql=events_sql[i], format='event_json', times=times)
            times += 1
        logger.success("Event Done ~")

    def get_user(self):
        sa = self.sa_config
        sa_ip = sa['ip']
        sa_token = sa['token']
        sa_project = sa['project']
        users_sql = self.users_sql_config
        times = 1
        for i in users_sql:
            self.request(uri=sa_ip, token=sa_token, project=sa_project,
                         sql=users_sql[i], format='profile_json', times=times)
            times += 1
        logger.success("Profile Done ~")       

    def run(self):
        self.get_event()
        self.get_user()
