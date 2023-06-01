#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    series.py

    Written by:               Johan Oñate Bregell <johan@bregell.se>
    Date:                     28 Nov 2018, (17:46)

    Copyright:
        Copyright (C) 2018 Johan Oñate Bregell

        This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
        Public License as published by the Free Software Foundation, version 3.

        This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
        implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
        for more details.

        You should have received a copy of the GNU General Public License along with this program.
        If not, see <https://www.gnu.org/licenses/>.
"""

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