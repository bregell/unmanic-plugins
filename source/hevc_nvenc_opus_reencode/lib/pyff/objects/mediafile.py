#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    mediafile.py

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

import subprocess
import json
import re

from .basefile import BaseFile
from .videostream import VideoStream
from .audiostream import AudioStream
from .subtitlestream import SubtitleStream
from .subtitlefile import SubtitleFile

class MediaFile(BaseFile):
    def __init__(self, name, size = 0, length = 0.0, v_streams = None, a_streams = None, s_streams = None, s_files = None):
        BaseFile.__init__(self, name, size)
        self.length = length
        self.v_streams  = ([] if v_streams  == None else v_streams)
        self.a_streams  = ([] if a_streams  == None else a_streams)
        self.s_streams  = ([] if s_streams  == None else s_streams)
        self.s_files    = ([] if s_files    == None else s_files)
        self.__info_populated = False

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, length):
        if type(length) is not float:
            raise TypeError("Length is not float")
        self.__length = length

    def getVideoStreams(self):
        return self.v_streams

    def appendVideoStream(self, v_stream):
        if type(v_stream) is not VideoStream:
            raise TypeError("Must be of type VideoStream")
        self.v_streams.append(v_stream)

    def getAudioStreams(self):
        return self.a_streams

    def appendAudioStream(self, a_stream):
        if type(a_stream) is not AudioStream:
            raise TypeError("Must be of type AudioStream")
        self.a_streams.append(a_stream)

    def getSubtitleStreams(self):
        return self.s_streams

    def appendSubtitleStream(self, s_stream):
        if type(s_stream) is not SubtitleStream:
            raise TypeError("Must be of type SubtitleStream")
        self.s_streams.append(s_stream)

    def getSubtitleFiles(self):
        return self.s_files

    def appendSubtitleFile(self, s_file):
        if type(s_file) is not SubtitleFile:
            raise TypeError("Must be of type SubtitleFile")
        self.s_files.append(s_file)

    def getInfo(self):
        # Check if info is populated
        if self.__info_populated == False:
            # Try to populate
            result, txt = self.__populate_file_info()
            if result == False:
                # Rasie exception
                raise Exception(txt)

        # Create info string
        txt = []
        txt.extend([BaseFile.getInfo(self)])
        txt.extend(["Length: {}".format(self.length)])
        for v_stream in self.getVideoStreams():
            txt.extend([v_stream.getInfo()])
        for a_stream in self.getAudioStreams():
            txt.extend([a_stream.getInfo()])
        for s_stream in self.getSubtitleStreams():
            txt.extend([s_stream.getInfo()])
        for s_file in self.getSubtitleFiles():
            txt.extend([s_file.getInfo()])
        return ", ".join(txt)

    def __populate_file_info(self, print_debug = False):
        # Command
        args = ["ffprobe", "-v", "quiet", "-hide_banner", "-show_format", "-show_streams", "-print_format", "json"]

        if ".vob" in self.name:
            args.extend(["-analyzeduration", "500M", "-probesize", "500M"])
        else:
            args.extend(["-analyzeduration", "250M", "-probesize", "250M"])

        args.extend(["-i",  self.name])

        # Get file info from ffprobe
        info_json = None
        try :
            pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            info_json, err = pipe.communicate()
        except:
            txt = "File: {} was unreadable, skipping.".format(self.name)
            self.log.error(txt)
            return False, txt

        data = info_json.decode('utf8')
        self.log.warning(data)
        json_data = json.loads(data)

        # Get file size
        self.size = int(json_data["format"]["size"])

        # Get media length
        self.length = 0.0
        if "duration" in json_data["format"]:
            self.length = float(json_data["format"]["duration"])

        # Search for video and audio info
        for item in json_data["streams"]:
            # Video
            if item["codec_type"] == "video":
                v_index = item["index"]
                v_codec = item["codec_name"]
                if v_codec in ["mjpeg"]:
                    continue
                v_bitrate = 0
                v_height = 0
                v_width = 0
                if "bit_rate" in item:
                    v_bitrate = int(item["bit_rate"])
                if "height" in item:
                    v_height = int(item["height"])
                if "width" in item:
                    v_width = int(item["width"])
                v_stream = VideoStream(v_index, v_codec, v_bitrate, v_width, v_height)
                self.appendVideoStream(v_stream)
                continue
            # Audio
            if item["codec_type"] == "audio":
                a_index = item["index"]
                a_codec = item["codec_name"]

                # No Channels
                a_channels = None
                if "channels" in item:
                    a_channels = int(item["channels"])

                # Channel layout
                a_channel_layout = None
                if "channel_layout" in item:
                    a_channel_layout = item["channel_layout"]

                # Fill in channels if missing and channel layout exists
                if a_channels == None and a_channel_layout != None:
                    if a_channel_layout == "stereo":
                        a_channels = 2
                    else:
                        n_ch = re.compile(r"([0-9]).([0-9])", re.I)
                        result = n_ch.search(a_channel_layout)
                        a_channels = int(result.group(1)) + int(result.group(2))

                # Fill in channel layout if missing and channels exists
                if a_channel_layout == None and a_channels != None:
                    if a_channels == 8:
                        a_channel_layout = "7.1"
                    elif a_channels == 7:
                        a_channel_layout = "6.1"
                    elif a_channels == 6:
                        a_channel_layout = "5.1"
                    elif a_channels == 2:
                        a_channel_layout = "stereo"
                    else:
                        a_channel_layout = "stereo"

                # Default to stereo if both channels and channel layout is missing
                if a_channel_layout == None and a_channels == None:
                    a_channel_layout = "stereo"
                    a_channels = 2

                # Bit rate
                a_bitrate_orig = None
                if "bit_rate" in item:
                    a_bitrate_orig = int(item["bit_rate"])
                if a_bitrate_orig == None:
                    a_bitrate = 64000 * a_channels
                else:
                    a_bitrate = min(a_bitrate_orig, 64000 * a_channels)

                # Append stream
                a_stream = AudioStream(a_index, a_codec, a_bitrate, a_channels, a_channel_layout)
                self.appendAudioStream(a_stream)
                continue
            # Subtitle
            if item["codec_type"] == "subtitle":
                language = "unk"
                if "tags" in item and "language" in item["tags"]:
                    language = item["tags"]["language"]
                s_stream = SubtitleStream(item["index"], item["codec_name"], language)
                self.appendSubtitleStream(s_stream)
                continue

        if self.getVideoStreams() == [] or self.getAudioStreams() == []:
            txt = "File: {} No audio and/or video codec could be found.".format(self.name)
            self.log.warning(txt)
            return False, txt

        # Special calculation for vido bitrate if missing from stream
        f_bitrate = int(json_data["format"]["bit_rate"])
        a_bitrate_total = 0
        v_bitrate_total = 0
        v_bitrate_missing = 0
        for a_stream in self.getAudioStreams():
            a_bitrate_total += a_stream.bitrate
        for v_stream in self.getVideoStreams():
            if v_stream.bitrate != 0:
                v_bitrate_total += v_stream.bitrate
            else:
                v_bitrate_missing += 1
        for v_stream in self.getVideoStreams():
            if v_stream.bitrate == 0:
                v_stream.bitrate = int((f_bitrate - v_bitrate_total - a_bitrate_total) / v_bitrate_missing)

        # Audio sanity (transparency level)
        for a_stream in self.getAudioStreams():
            a_bitrate = a_stream.bitrate
            if a_bitrate > 320000:
                a_stream.bitrate = 320000
            elif a_bitrate < 96000:
                a_stream.bitrate = 96000

        # Video sanity (transparency level)
        for v_stream in self.getVideoStreams():
            if v_stream.width == None:
                txt = "Unknown video width for: {}".format(self.name)
                self.log.warning(txt)
            elif v_stream.width <= 544:
                v_stream.bitrate = min(v_stream.bitrate, 1352000)
            elif v_stream.width <= 720:
                v_stream.bitrate = min(v_stream.bitrate, 1789000)
            elif v_stream.width <= 1280:
                v_stream.bitrate = min(v_stream.bitrate, 3977000)
            elif v_stream.width <= 1920:
                v_stream.bitrate = min(v_stream.bitrate, 8948000)
            elif v_stream.width <= 3840:
                v_stream.bitrate = min(v_stream.bitrate, 35795000)

        self.__info_populated = True
        return True, "Success"