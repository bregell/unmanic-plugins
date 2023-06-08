#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    media.py

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