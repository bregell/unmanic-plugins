class Media(object):
    def __init__(self, title):
        self.title = title

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        if type(title) is not str:
            raise TypeError("Title is not string")
        self.__title = title

    def getInfo(self):
        txt = "Title: {}".format(self.title)
        return txt