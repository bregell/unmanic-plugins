from .episode import Episode
class Season(object):
    def __init__(self, season, episodes = None, series = None):
        self.season = season
        self.episodes = [] if episodes == None else episodes
        self.series = series

    @property
    def season(self):
        return self.__season

    @season.setter
    def season(self, season):
        if type(season) is not int:
            raise TypeError("Season is not int")
        self.__season = season

    @property
    def episodes(self):
        return self.__episodes

    @episodes.setter
    def episodes(self, episodes):
        if type(episodes) is not list:
            raise TypeError("Episodes is not list")
        if len(episodes) > 0:
            if type(episodes[0]) is not Episode:
                raise TypeError("Episode is not list")
        self.__episodes = episodes

    def addEpisode(self, episode):
        if type(episode) is not Episode:
            raise TypeError("Episode is not of type Episode")
        self.__episodes.append(episode)
        episode.season = self

    def getInfo(self):
        txt = ["Season: {}".format(self.season)]
        for ep in self.episodes:
            txt.extend([ep.getInfo()])
        return ", ".join(txt)