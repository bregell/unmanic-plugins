#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    stream.py

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

class Stream(object):
    def __init__(self, index, codec):
        self.index = index
        self.codec = "" if codec == None else codec

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index):
        if type(index) is not int:
            raise TypeError("Index is not integer")
        self.__index = index

    @property
    def codec(self):
        return self.__codec

    @codec.setter
    def codec(self, codec):
        if type(codec) is not str:
            raise TypeError("Codec is not string")
        self.__codec = codec


    def getInfo(self):
        txt = "Index: {}, Codec: {}".format(self.index, self.codec)
        return txt