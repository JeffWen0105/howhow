
from loguru import logger

import query



if __name__ == "__main__":
    logger.add(f"query.log",level="INFO")
    q = query.Query()
    q.run()