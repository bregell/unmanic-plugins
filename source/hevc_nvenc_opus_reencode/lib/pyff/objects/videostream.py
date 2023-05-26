#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    videostream.py

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

from .mediastream import MediaStream

class VideoStream(MediaStream):
    def __init__(self, index, codec, bitrate, width, height):
        MediaStream.__init__(self, index, codec, bitrate)
        self.__height = height
        self.__width = width

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, height):
        if type(height) is not int:
            raise TypeError("Height is not integer")
        if height < 0:
            raise ValueError("Height should be a positive number over zero")
        self.__height = height

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, width):
        if type(width) is not int:
            raise TypeError("Width is not integer")
        if width < 0:
            raise ValueError("Width should be a positive number over zero")
        self.__width = width

    def getInfo(self):
        txt = ""
        txt += MediaStream.getInfo(self) + ", "
        txt += "Width: {}, Heigth {}".format(self.width, self.height)
        return txt
