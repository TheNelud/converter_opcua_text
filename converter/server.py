import datetime
import time
import threading

from . import logInfo, parser
from opcua import Server, ua


class Server_OPCUA_txt:
    def __init__(self):
        self.var = None
        self.logging = logInfo.get_logger(__name__)
        self.config = parser.get_config()
        self.flag = 0

        self.lastFile = parser.last_file(self.config['path'])

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

        self.mainTags = parser.getMainTags(self.config['path'])
        self.dictTags = []
        self.count = 0

        for element in self.mainTags:
            # print(element['value'])
            self.var = self.myobj.add_variable(self.idx, element['tag'], element['value'],
                                               parser.get_ua_type(element['value']))
            self.datavalue = ua.DataValue(variant=float_or_str(element['value']))
            self.datavalue.SourceTimestamp = datetime.datetime.strptime(element['date'], '%d-%b-%Y %H:%M:%S') - datetime.timedelta(hours=5)
            if element['Status'] == 'Bad':
                self.datavalue.StatusCode = ua.StatusCode(ua.StatusCodes.Bad)
            self.var.set_value(self.datavalue)
            self.count += 1
            self.dictTags.append(self.var)
        self.logging.info("Создание тегов: " + str(self.count))

    def restart(self):
        self.logging.warning('Остановка сервера')
        self.server.stop()
        # time.sleep(60)
        self.logging.warning('Запуск сервера')
        self.start()

    def chekingCreationTxt(self):
        while True:
            self.newFile = parser.getMainTags(self.config['path'])
            if self.lastFile != self.newFile:
                self.logging.warning("Появился новый файл! Удаление старого дерева и создание нового дерева данных")
                self.server.delete_nodes(self.dictTags)
                self.lastFile = self.newFile
                self.main_tags()
                self.life_server_tag()
            else:
                self.logging.info("Нет новых файлов")
                self.life_server_tag()
                time.sleep(int(self.config["UPDATE_RATE"]))



    def start(self):
        # Запускаем сервер ,создаем ветку данных
        # В цикле проверяем обновления текстового файла в директории,
        # если обновился , удаяем старую ветку и создаем новую
        # Если нет новых файлов , проверяем каждые UPDATE_RATE

        try:
            self.server.start()
            self.main_tags()
            self.chekingCreationTxt()



        except KeyboardInterrupt:
            self.logging.warning('Закрытие программы')
        self.server.stop()
