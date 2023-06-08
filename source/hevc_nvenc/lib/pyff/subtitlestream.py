#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    subtitlestream.py

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

from .stream import Stream

class SubtitleStream(Stream):
    def __init__(self, index, codec, language = None):
        Stream.__init__(self, index, codec)
        self.__language = "" if language == None else "unk"

    @property
    def language(self):
        return self.__language

    @language.setter
    def language(self, lang):
        if type(lang) is not str:
            raise TypeError("Language is not string")
        if len(lang) != 3:
            raise ValueError("Language should be 3 letters ISOXXX-X")
        self.__language = lang

    def getInfo(self):
        txt = ""
        txt += Stream.getInfo(self) + ", "
        txt += "Language: {}".format(self.language)
        return txt