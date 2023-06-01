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

import os
import subprocess
import json
import re
from difflib import SequenceMatcher

from guessit import guessit as guessit

from .basefile import BaseFile
from .videostream import VideoStream
from .audiostream import AudioStream
from .subtitlestream import SubtitleStream
from .subtitlefile import SubtitleFile
from .season import Season
from .series import Series
from .movie import Movie
from .miniseries import MiniSeries
from .episode import Episode

class MediaFile(BaseFile):
    def __init__(self, name, log, size = 0, length = 0.0, v_streams = None, a_streams = None, s_streams = None, s_files = None):
        BaseFile.__init__(self, name, size)
        self.log = log
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
        self.v_streams.append(v_stream)

    def getAudioStreams(self):
        return self.a_streams

    def appendAudioStream(self, a_stream):
        self.a_streams.append(a_stream)

    def getSubtitleStreams(self):
        return self.s_streams

    def appendSubtitleStream(self, s_stream):
        self.s_streams.append(s_stream)

    def getSubtitleFiles(self):
        return self.s_files

    def appendSubtitleFile(self, s_file):
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
        # self.log.warning(data)
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

    def get_media_info(self):
        m_type = self.__get_type(self.name)
        if m_type == None:
            return None
        m_title = self.__get_title(self.name, m_type)
        if m_title == None:
            return None
        m_type.title = m_title
        if isinstance(m_type, Series):
            m_episode = self.__get_episode(self.name, m_title)
            if m_episode == None:
                return None
            m_season = self.__get_season(self.name)
            if m_season == None:
                return None
            m_season.addEpisode(m_episode)
            m_type.addSeason(m_season)
        elif isinstance(m_type, MiniSeries):
            m_episode = self.__get_episode(self.name, m_title)
            if m_episode == None:
                return None
            m_type.addEpisode(m_episode)
        return m_type

    def __get_episode(full_name, m_title):
        # Get file name
        _, f_name = os.path.split(full_name)
        # Get Episode info
        info = guessit(f_name)
        # Check type
        if "type" in info and info["type"] != "episode":
            return None
        # Episode number
        if "episode" not in info:
            return None
        ep_number = info["episode"]
        # Episode title
        ep_title = ""
        if "episode_title" in info:
            ratio = SequenceMatcher(None, m_title.lower(), info["episode_title"].lower()).ratio()
            if ratio <= 0.6:
                ep_title = info["episode_title"]
        elif "title" in info:
            ratio = SequenceMatcher(None, m_title.lower(), info["title"].lower()).ratio()
            if ratio <= 0.6:
                ep_title = info["title"]
        # Create episode
        m_episode = Episode(ep_title, ep_number, 0.0)
        return m_episode

    def __get_season(f_name):
        # Get season (if possible)
        info = guessit(f_name)
        s_number = 1
        if "season" in info:
            s_number = info["season"]
        m_season = Season(s_number)
        return m_season

    def __get_type(f_name):
        f_path, f_name = os.path.split(f_name)
        # Get file type
        type_rx = re.compile(r"(s([0-9]{1,}))", re.I)
        type_rxe = re.compile(r"(e([0-9]{1,}))", re.I)
        type_res = type_rx.search(f_path)
        type_res2 = type_rx.search(f_name)
        type_res3 = type_rxe.search(f_name)
        if type_res != None or type_res2 != None:
            # Series
            m_type = Series("")
        elif type_res3 != None:
            # Mini Series
            m_type = MiniSeries("")
        else:
            # Movive
            m_type = Movie("", 0.0)
        return m_type

    def __get_title(f_name, m_type):
        m_title = None
        f_path, f_name = os.path.split(f_name)
        parts = f_path.split("\\")
        if isinstance(m_type, (Movie, MiniSeries)):
            m_title = parts[-1:][0]
        elif isinstance(m_type, Series):
            m_title = parts[-2:-1][0]
        info = guessit(f_name)
        if "title" in info: # and info["title"].lower() in m_title.lower():
            m_title = info["title"]
        return m_title