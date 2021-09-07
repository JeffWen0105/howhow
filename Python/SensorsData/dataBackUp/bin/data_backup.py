import math

import requests
from loguru import logger

class ApiBackUP():
    @property
    def types(self):
        return self._types

    @types.setter
    def types(self, types):
        self._types = types

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, project):
        self._project = project

    def get_counts(self):
        params = (
            ('token', self.token),
            ('project', self.project),
            ('q', f'SELECT count(*) FROM {self.sql_type} /*MAX_QUERY_EXECUTION_TIME=1800*/')
        )
        response = requests.post(
            'http://127.0.0.1:8107/api/sql/query', params=params)
        total = response.text.split('\n')[1]
        total = int(total)
        logger.info(f'總計有: {total:,} 數據..')
        return total

    def get_data(self):
        params = (
            ('token', self.token),
            ('project', self.project),
            ('q',f'SELECT * FROM {self.sql_type} order by  {self.order_col} limit 1,{self.my_times}/*MAX_QUERY_EXECUTION_TIME=1800*/'),
            ('format',f'{self.format_type}_json')
        )
        response = requests.post('http://127.0.0.1:8107/api/sql/query', params=params)
        file = f"output/{self.types}_0.json"
        with open(file, "w", encoding='utf-8') as f:
            f.write(response.text)
        logger.info(f'Saveing -> {file}')

        for i in range(1,self.times):
            params = (
                ('token', self.token),
                ('project', self.project),
                ('q',f'SELECT * FROM {self.sql_type} order by  {self.order_col} limit {self.my_times * i},{self.my_times}/*MAX_QUERY_EXECUTION_TIME=1800*/'),
                ('format',f'{self.format_type}_json')
            )
            response = requests.post('http://127.0.0.1:8107/api/sql/query', params=params)
            file = f"output/{self.types}_{i}.json"
            with open(file, "w", encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f'Saveing -> {file}')

    def run(self):
        if self.types == 'users':
            self.sql_type = 'users'
            self.format_type = 'profile'
            self.order_col = '$update_time'
        elif self.types == 'events':
            self.sql_type = 'events'
            self.format_type = 'event'
            self.order_col = 'date'
        elif self.types == 'items':
            self.sql_type = 'item'
            self.format_type = 'items'
            self.order_col = '$update_time'
        total = self.get_counts()
        self.my_times = 1000000
        self.times = math.ceil(total / self.my_times)
        logger.info(f"每一次查詢 {self.my_times:,} 筆, 需執行 {self.times:,} 次API查詢")
        self.get_data()
