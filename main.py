import threading

import converter.logInfo as logInfo
from converter.server import Server_OPCUA_txt

logger = logInfo.get_logger(__name__)

def main():
    logger.info("Сервер стартует")
    Server_OPCUA_txt().start()


if __name__ == "__main__":
    main()


