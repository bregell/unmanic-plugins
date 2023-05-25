from .stream import Stream

class SubtitleStream(Stream):
    def __init__(self, index, codec, language = None):
        Stream.__init__(self, index, codec)
        self.__language = "" if language == None else "unk"

    @property
    def language(self):
        return self.__language

    @language.setter
    def language(self, lang):
        if type(lang) is not str:
            raise TypeError("Language is not string")
        if len(lang) != 3:
            raise ValueError("Language should be 3 letters ISOXXX-X")
        self.__language = lang

    def getInfo(self):
        txt = ""
        txt += Stream.getInfo(self) + ", "
        txt += "Language: {}".format(self.language)
        return txt