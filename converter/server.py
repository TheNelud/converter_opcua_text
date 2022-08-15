import time

from . import logInfo, parser
from opcua import Server, ua


class Server_OPCUA_txt:
    def __init__(self):
        self.logging = logInfo.get_logger(__name__)
        self.config = parser.get_config()
        self.flag = 0

        self.server = Server()
        self.server.set_endpoint(self.config['UA_HOST'])
        self.server.set_server_name(self.config["UA_SERVER_NAME"])
        self.idx = self.server.register_namespace(self.config["UA_ROOT_NAMESPACE"])
        self.myobj = self.server.nodes.objects.add_folder(self.idx, "DATA")

    def life_server_tag(self, tag):
        try:
            if self.flag != 1:
                self.flag = 1
                tag.set_value(True)
            else:
                self.flag = 0
                tag.set_value(False)
        except Exception:
            self.logging.warning("Сервер мертв, пошел на перезапуск")
            self.restart()

    def restart(self):
        self.logging.warning('Остановка сервера')
        self.server.stop()
        self.logging.warning('Запуск сервера')
        self.start()

    def start(self):

        self.tagLifeServer = self.myobj.add_variable(self.idx,
                                                     'Life Server',
                                                     False,
                                                     ua.VariantType.Boolean)
        self.server.start()
        while True:

            self.life_server_tag(self.tagLifeServer)
            time.sleep(5)
