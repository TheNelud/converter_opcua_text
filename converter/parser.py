import xml.etree.ElementTree as ET
import os, os.path
from opcua import ua

class ParserText:
    def __init__(self):
        self.tree = ET.parse('config.xml')
        self.root = self.tree.getroot()
        self.resultConfig = {}
        self.resultFile = []
        self.file =  self.lastFile()

    def config(self):
        try:
            for element in self.root:
                self.resultConfig[element.tag] = element.text
            return self.resultConfig
        except EOFError as e:
            print("Error:" + str(e))

    def lastFile(self, directory):
        files = [os.path.join(directory, _) for _ in os.listdir(directory) if _.endswith('.txt')]
        if len(files) > 0:
            return max(files, key=os.path.getctime)
        else:
            return False

    def getFile(self):
        pass