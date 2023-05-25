class Stream(object):
    def __init__(self, index, codec):
        self.index = index
        self.codec = "" if codec == None else codec

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index):
        if type(index) is not int:
            raise TypeError("Index is not integer")
        self.__index = index

    @property
    def codec(self):
        return self.__codec

    @codec.setter
    def codec(self, codec):
        if type(codec) is not str:
            raise TypeError("Codec is not string")
        self.__codec = codec


    def getInfo(self):
        txt = "Index: {}, Codec: {}".format(self.index, self.codec)
        return txt