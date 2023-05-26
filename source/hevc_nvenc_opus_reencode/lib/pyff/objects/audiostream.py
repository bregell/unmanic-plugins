#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    audiostream.py

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

class AudioStream(MediaStream):
    def __init__(self, index, codec, bitrate, channels, channel_layout):
        MediaStream.__init__(self, index, codec, bitrate)
        self.__channels = channels
        self.__channel_layout = channel_layout

    @property
    def channels(self):
        return self.__channels

    @channels.setter
    def channels(self, channels):
        if type(channels) is not int:
            raise TypeError("Channels must be interger")
        self.__channels = channels

    @property
    def channel_layout(self):
        return self.__channel_layout

    @channel_layout.setter
    def channel_layout(self, channel_layout):
        self.__channel_layout = channel_layout

    def getInfo(self):
        txt = ""
        txt += MediaStream.getInfo(self) + ", "
        txt += "Channels: {}, Channel Layout: {}".format(self.channels, self.channel_layout)
        return txt
