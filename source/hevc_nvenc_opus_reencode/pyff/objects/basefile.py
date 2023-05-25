import os
import humanize

class BaseFile(object):
    def __init__(self, name, size = 0):
        self.name = name
        self.size = size

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if type(name) is not str:
            raise TypeError("Name is not string")
        self.__name = name

    @property
    def path(self):
        return os.path.dirname(self.name)

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        if type(size) is not int:
            raise TypeError("Size is not integer")
        if size < 0:
            raise ValueError("Size shoudl be a positive number")
        self.__size = size

    def getInfo(self):
        txt = "File: {}, Size: {}".format(self.name, humanize.naturalsize(self.size, binary=True))
        return txt