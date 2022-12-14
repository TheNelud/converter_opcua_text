import os
import os.path
import xml.etree.ElementTree as ET
import converter.logInfo as logInfo
from opcua import ua

logger = logInfo.get_logger(__name__)


# Возвращаем нужный нам тип, один фиг пришлось менять в библиотеке uatype.py
def get_ua_type(value):
    if value.__class__.__name__ == 'int':
        return ua.uatypes.VariantType.Int32
    elif value.__class__.__name__ == 'float':
        return ua.uatypes.VariantType.Float
    elif value.__class__.__name__ == 'bool':
        return ua.uatypes.VariantType.Boolean
    elif value.__class__.__name__ == 'str':
        return ua.uatypes.VariantType.String
    elif value.__class__.__name__ == 'double':
        return ua.uatypes.VariantType.Float
    else:
        return None


# Чтение файла конфигурации, для создания сервера
def get_config(configFile='cfg.xml'):
    try:
        tree = ET.parse(configFile)
        root = tree.getroot()
        res = {}
        for child in root:
            res[child.tag] = child.text
        logger.info("Чтение конфигурация.")
        return res
    except Exception:
        logger.warning("Ошибка при чтение файла конфигурации.")


# Чекаем в выбранной директории последний текстовый файл
# def last_file(directory):
#     return os.path.join(directory, 'RTP_Values')

def last_file(directory):
    files = [os.path.join(directory, _) for _ in os.listdir(directory) if _.endswith('.txt')]
    if len(files) > 0:
        return max(files, key=os.path.getctime)
    else:
        return False


# Проверка на дупликаты
def dublicates(list):
    if list != False:
        result = []
        for i in range(len(list)):
            result.append(list[i]['tag'])
        setResult = set(result)
        for elem in setResult:
            if result.count(elem) > 1:
                indices = [i for i, x in enumerate(result) if x == elem]
                list.pop(indices[0])
        return list
    else:
        return False


# Разбираем текстовый файл
def get_file(dir):
    res = []
    fl = last_file(dir)
    _file = open(fl, 'r', encoding='UTF-8')
    if fl != False:
        for line in _file:
            line = line.strip()
            res.append(dict(zip(("tag", "date", "value", "Status"), line.split(","))))

        for i in range(len(res)):
            if 'Status' in res[i]:
                res[i]['Status'] = 'Bad'
            else:
                res[i]['Status'] = 'Good'
        _file.close()
        return res
    else:
        logger.warning("Текстовый файл не найден")
        return False


def getMainTags(path):
    return dublicates(get_file(path))


# if __name__ == "__main__":
#     config = get_config()
#
#     count1 = 0
#     for elem in get_file(config['path']):
#         count1 += 1
#     print(count1)
#
#     count = 0
#     for elem in getMainTags(config['path']):
#         count += 1
#     print(count)
