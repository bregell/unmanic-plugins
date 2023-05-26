#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    miniseries.py

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