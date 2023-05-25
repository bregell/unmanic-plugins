from .media import Media
from .season import Season

class Series(Media):
    def __init__(self, title, seasons = None):
        Media.__init__(self, title)
        self.seasons = [] if seasons == None else seasons

    @property
    def seasons(self):
        return self.__seasons

    @seasons.setter
    def seasons(self, seasons):
        if type(seasons) is not list:
            raise TypeError("Seasons is not list")
        if len(seasons) > 0:
            if type(seasons[0]) is not Season:
                raise TypeError("Season is not Season")
        self.__seasons = seasons

    def addSeason(self, season):
        if type(season) is not Season:
            raise TypeError("Season is not Season")
        self.__seasons.append(season)
        season.series = self

    def getInfo(self):
        txt = [Media.getInfo(self)]
        for season in self.seasons:
            txt.append([season.getInfo()])
        return ", ".join(txt)