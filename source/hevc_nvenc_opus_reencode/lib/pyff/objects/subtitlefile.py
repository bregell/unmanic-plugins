#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    subtitlefile.py

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

from .basefile import BaseFile
from .subtitlestream import SubtitleStream

class SubtitleFile(BaseFile, SubtitleStream):
    def __init__(self, name, codec = None, language = None, encoding = None):
        BaseFile.__init__(self, name)
        SubtitleStream.__init__(self, 0, codec, language)
        self.encoding = "" if encoding == None else encoding

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        if type(encoding) is not str:
            raise TypeError("Encoding is not string")
        self.__encoding = encoding

    def getInfo(self):
        txt = []
        txt.extend([BaseFile.getInfo(self)])
        txt.extend([SubtitleStream.getInfo(self)])
        txt.extend(["Encoding: {}".format(self.encoding)])
        return ", ".join(txt)