from .basefile import BaseFile
from .subtitlestream import SubtitleStream

class SubtitleFile(BaseFile, SubtitleStream):
    def __init__(self, name, codec = None, language = None, encoding = None):
        BaseFile.__init__(self, name)
        SubtitleStream.__init__(self, 0, codec, language)
        self.encoding = "" if encoding == None else encoding

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        if type(encoding) is not str:
            raise TypeError("Encoding is not string")
        self.__encoding = encoding

    def getInfo(self):
        txt = []
        txt.extend([BaseFile.getInfo(self)])
        txt.extend([SubtitleStream.getInfo(self)])
        txt.extend(["Encoding: {}".format(self.encoding)])
        return ", ".join(txt)