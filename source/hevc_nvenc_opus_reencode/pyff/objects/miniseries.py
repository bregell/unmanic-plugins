from .media import Media
from .episode import Episode

class MiniSeries(Media):
    def __init__(self, title, episodes = None):
        Media.__init__(self, title)
        self.episodes = [] if episodes == None else episodes

    @property
    def episodes(self):
        return self.__episodes

    @episodes.setter
    def episodes(self, episodes):
        if type(episodes) is not list:
            raise TypeError("episodes is not list")
        if len(episodes) > 0:
            if type(episodes[0]) is not Episode:
                raise TypeError("episodes is not Episode")
        self.__episodes = episodes

    def addEpisode(self, episodes):
        if type(episodes) is not Episode:
            raise TypeError("episodes is not Episode")
        self.__episodes.append(episodes)
        episodes.series = self

    def getInfo(self):
        txt = [Media.getInfo(self)]
        for episode in self.episodes:
            txt.append([episode.getInfo()])
        return ", ".join(txt)