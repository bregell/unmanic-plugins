from .media import Media

class Movie(Media):
    def __init__(self, title, length):
        Media.__init__(self, title)
        self.length = length

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, length):
        if type(length) is not float:
            raise TypeError("Length is not float")
        self.__length = length

    def getInfo(self):
        txt = "Length: {}".format(self.length)
        return txt