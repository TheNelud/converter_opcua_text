import datetime
import logging
import sys
import time
from threading import Timer

import converter
from . import logInfo, parser
from opcua import Server, ua
from opcua.ua import NodeId, NodeIdType


class Server_OPCUA_txt:
    def __init__(self):
        self.var = None
        self.logging = logInfo.get_logger(__name__) # инииализирую логирование
        self.config = parser.get_config()           # конфигурационный файл
        self.flag = 0                               # флаг для пульсирующего сигнала

        # Конфигурация сервера
        try:
            self.server = Server()                                                          # создаем экземпляр обьекта Server
            self.server.set_endpoint(self.config['UA_HOST'])                                # хост под которым будет работать сервер
            self.server.set_server_name(self.config["UA_SERVER_NAME"])                      # имя сервера
            self.idx = self.server.register_namespace(self.config["UA_ROOT_NAMESPACE"])     # название простраства имен
            self.myobj = self.server.nodes.objects.add_folder(self.idx, "DATA")             # создаем ветку DATA в которой будет находится теги

        except TypeError as e:
            self.logging.warning("Ошибка при создание сервера: " + str(e))

        # Пульсирующий тэг(SERVER LIFE)
        try:
            self.tagLifeServer = self.myobj.add_variable(self.idx, 'Life Server', False, ua.VariantType.Boolean) # создаем обьект пульсирующего сигнала в пространстве имен idx,
                                                                                                                 # именем 'Live server', значением False, типом данных Boolean
        except AttributeError as e:
            self.logging.warning("Сервер не создан" + str(e))

    # Функция запускает отдельный поток каждые 5 минут на обновление тега Live Server
    def life_server_tag(self):

        if self.flag != 1:
            self.flag = 1
            self.tagLifeServer.set_value(True)  # обновление тега Live Server
        else:
            self.flag = 0
            self.tagLifeServer.set_value(False) # обновление тега Live Server
        timer = Timer(5, self.life_server_tag)
        timer.start()

    #Функция фовращает либо FLOAT или String
    def float_or_str(self, value):
        try:
            return int(value)
        except:
            try:
                return float(value)
            except:
                return str(value)



    #функция
    def add_variable_tag(self, element):
        nodeID = NodeId(identifier=element['tag'], namespaceidx=self.idx)
        return self.myobj.add_variable(nodeID, element['tag'], element['value'],
                                       parser.get_ua_type(element['value']))


    def create_tree(self, tags):
        self.montags = []
        self.montags.clear()

        for element_tree in tags:
            try:
                var = self.add_variable_tag(element_tree)
                self.montags.append(var)
                self.update_value(var, element_tree)
            except:
                continue

        self.logging.info('Создание дерева')
        # return montags

    def update_value(self, var, element_tree):
        try:
            try:
                timestamp = datetime.datetime.strptime(element_tree['date'], '%d-%b-%Y %H:%M:%S') - datetime.timedelta(hours=5)
            except:
                timestamp = datetime.datetime.now()
            datavalue = ua.DataValue(variant=self.float_or_str(element_tree['value']))
            # datavalue = ua.DataValue(variant=element_tree['value'])
            try:
                datavalue.SourceTimestamp = timestamp
            except:
                datavalue.SourceTimestamp = datetime.datetime.now()
            if (element_tree['Status'] == 'Bad'):
                datavalue.StatusCode = ua.StatusCode(ua.StatusCodes.Bad)
            var.set_value(datavalue, parser.get_ua_type(element_tree['value']))
        except KeyError:
            self.logging.warning("Ошибка при обновление тега")
            return False

        # self.logging.info('Обновление значений тегов')

    def restart(self):
        self.logging.warning('Остановка сервера')
        self.server.stop()
        self.logging.warning('Запуск сервера')
        self.start()

    def chekingCreationTxt(self):

        lastTags = parser.getMainTags(self.config['path'])
        self.create_tree(lastTags)
        # print(self.montags)

        while True:
            newTags = parser.getMainTags(self.config['path'])
            if lastTags != newTags:
                for elem in newTags:
                    var = self.server.get_node('ns=2;s={}'.format(elem['tag']))
                    if var in self.montags:
                        self.update_value(var, elem)
                    else:
                        self.server.delete_nodes(self.montags)
                        self.create_tree(newTags)

                self.logging.info('Обновление значений тегов')
                lastTags = newTags

            else:
                # self.logging.info("Нет новых файлов")
                time.sleep(int(self.config['UPDATE_RATE']))

    def start(self):
        self.life_server_tag()
        try:
            self.server.start()
            self.logging.warning('Старт сервера')
            self.chekingCreationTxt()

        except KeyboardInterrupt:
            self.logging.warning('Закрытие программы')

        self.server.stop()
