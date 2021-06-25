import subprocess

from loguru import logger

class TokenGetter:
    def get_token(self):
        sql = """
        sa_mysql -D metadata -e \"select password from user where username = 'admin' and is_global = 1;\"
        """
        try:
            process = subprocess.run(sql, shell=True, stdout=subprocess.PIPE,timeout=60)
            if process.returncode == 0:
                token = process.stdout.decode('UTF-8').split()[1]
                logger.info(f'Get token: {token}')
                return token
            else:
                logger.warning(f"Token 取得失敗: {process}")
                logger.critical("程序停止...")
                exit(1)
        except Exception as _:
                logger.warning(f"Token 取得失敗: {_}")
                logger.critical("程序停止...")
                exit(1)