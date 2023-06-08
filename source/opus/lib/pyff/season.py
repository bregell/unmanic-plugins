#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    season.py

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