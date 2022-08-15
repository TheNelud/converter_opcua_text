import datetime
import time

from . import logInfo, parser
from opcua import Server, ua


class Server_OPCUA_txt:
    def __init__(self):
        self.var = None
        self.logging = logInfo.get_logger(__name__)
        self.config = parser.get_config()
        self.flag = 0
        self.serverTag = 0

        # Конфигурация сервера
        try:
            self.server = Server()
            self.server.set_endpoint(self.config['UA_HOST'])
            self.server.set_server_name(self.config["UA_SERVER_NAME"])
            self.idx = self.server.register_namespace(self.config["UA_ROOT_NAMESPACE"])
            self.myobj = self.server.nodes.objects.add_folder(self.idx, "DATA")
        except TypeError as e:
            self.logging.warning("Ошибка при создание сервера: " + str(e))

        # Пульсирующий тэг(SERVER LIFE)
        try:
            self.tagLifeServer = self.myobj.add_variable(self.idx, 'Life Server', False, ua.VariantType.Boolean)
        except AttributeError as e:
            self.logging.warning("Сервер не создан" + str(e))
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

    def main_tags(self):
        def float_or_str(value):
            try:
                return float(value)
            except:
                return str(value)

        while True:
            self.count = 0
            self.mainTags = parser.getMainTags(self.config['path'])

            dictTags = []
            for element in self.mainTags:
                self.var = self.myobj.add_variable(self.idx, element['tag'], element['value'], parser.get_ua_type(element['value']))
                self.datavalue = ua.DataValue(variant=float_or_str(element['value']))
                self.datavalue.SourceTimestamp = datetime.datetime.strptime(element['date'], '%d-%b-%Y %H:%M:%S')
                if element['Status'] == 'Bad':
                    self.datavalue.StatusCode = ua.StatusCode(ua.StatusCodes.Bad)
                self.var.set_value(self.datavalue)
                self.count += 1
                dictTags.append(self.var)

                # print(element)
            self.logging.info("Создание тегов: " + str(self.count))
            if len(dictTags) != len(self.mainTags):
                self.server.delete_nodes(dictTags)
            time.sleep(30)



    def restart(self):
        self.logging.warning('Остановка сервера')
        self.server.stop()
        time.sleep(10)
        self.logging.warning('Запуск сервера')
        self.start()

    def start(self):

        try:
            self.server.start()
            self.main_tags()
            # self.life_server_tag()
        except KeyboardInterrupt:
            self.logging.warning('Закрытие программы')
        self.server.stop()
