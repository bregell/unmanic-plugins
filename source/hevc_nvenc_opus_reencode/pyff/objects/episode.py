from .media import Media

class Episode(Media):
    def __init__(self, title, episode, length, season = None):
        Media.__init__(self, title)
        self.episode = episode
        self.length = length
        self.season = season

    @property
    def episode(self):
        return self.__episode

    @episode.setter
    def episode(self, episode):
        if type(episode) is int:
            self.__episode = episode
        elif type(episode) is list and len(episode) > 0 and type(episode[0]) is int:
            if (episode[1] == (episode[0] + 1)):
                self.__episode = episode
            else:
                self.__episode = episode[0]
        else:
            raise TypeError("Episode is not integer or list of integer")

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, length):
        if type(length) is not float:
            raise TypeError("Length is not float")
        self.__length = length

    def getInfo(self):
        txt = "Episode: {}, Length: {}".format(self.episode, self.length)
        return txt