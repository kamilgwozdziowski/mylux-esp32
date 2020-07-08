import ujson

class Config:
    def __init__(self, filename):
        f = open(filename)
        jsonFile = f.read()
        self._config = ujson.loads(jsonFile)

    def getAllConnfig(self):
        return self._config

    def getConfig(self, field):
        return self._config[field]