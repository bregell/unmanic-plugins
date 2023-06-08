#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    mediastream.py

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

import humanize

from .stream import Stream

class MediaStream(Stream):
    def __init__(self, index, codec, bitrate):
        Stream.__init__(self, index, codec)
        self.__bitrate = bitrate

    @property
    def bitrate(self):
        return self.__bitrate

    @bitrate.setter
    def bitrate(self, bitrate):
        if type(bitrate) is not int:
            raise TypeError("Bitrate is not integer")
        self.__bitrate = bitrate

    def getInfo(self):
        txt = ""
        txt += Stream.getInfo(self) + ", "
        txt += "Bitrate: {}/s".format(humanize.naturalsize(self.bitrate))
        return txt