#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    basefile.py

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

import os

import humanize

class BaseFile(object):
    def __init__(self, name, size = 0):
        self.name = name
        self.size = size

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if type(name) is not str:
            raise TypeError("Name is not string")
        self.__name = name

    @property
    def path(self):
        return os.path.dirname(self.name)

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        if type(size) is not int:
            raise TypeError("Size is not integer")
        if size < 0:
            raise ValueError("Size shoudl be a positive number")
        self.__size = size

    def getInfo(self):
        txt = "File: {}, Size: {}".format(self.name, humanize.naturalsize(self.size, binary=True))
        return txt