import time

from . import logInfo, parser
from opcua import Server, ua
import threading


class Server_OPCUA_txt:
    def __init__(self):
        self.logging = logInfo.get_logger(__name__)
        self.config = parser.get_config()
        self.flag = 0

        # Конфигурация сервера
        self.server = Server()
        self.server.set_endpoint(self.config['UA_HOST'])
        self.server.set_server_name(self.config["UA_SERVER_NAME"])
        self.idx = self.server.register_namespace(self.config["UA_ROOT_NAMESPACE"])
        self.myobj = self.server.nodes.objects.add_folder(self.idx, "DATA")

        # Пульсирующий тэг(SERVER LIFE)
        self.tagLifeServer = self.myobj.add_variable(self.idx, 'Life Server', False, ua.VariantType.Boolean)

    def life_server_tag(self):
        while True:
            time.sleep(5)
            try:
                if self.flag != 1:
                    self.flag = 1
                    self.tagLifeServer.set_value(True)
                else:
                    self.flag = 0
                    self.tagLifeServer.set_value(False)
            except Exception:
                self.logging.warning("Сервер мертв, пошел на перезапуск")
                self.restart()

    def restart(self):
        self.logging.warning('Остановка сервера')
        self.server.stop()
        time.sleep(10)
        self.logging.warning('Запуск сервера')
        self.start()

    def start(self):

        try:
            self.server.start()
            self.life_server_tag()
        except KeyboardInterrupt:
            self.logging.warning('Закрытие программы')
        self.server.stop()
