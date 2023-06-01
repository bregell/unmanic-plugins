#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    plugins.transcode.py

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

import re

from .mediafile import MediaFile

class TranscodeResult(object):
    def __init__(self, status = True, string = None):
        self.status = status
        self.string = ("" if string == None else string)

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        if type(status) is not bool:
            raise TypeError("result must be bool")
        self.__status = status

    @property
    def string(self):
        return self.__string

    @string.setter
    def string(self, string):
        if type(string) is not str:
            raise TypeError("string must be str")
        self.__string = string


class TranscodeJob(object):
    def __init__(self, mediafile, log, args = None, result = None, new_file = None):
        self.log = log
        self.mediafile = mediafile
        self.args = ([] if args == None else args)
        self.result = (TranscodeResult() if result == None else result)
        self.new_file = (MediaFile("", None) if new_file == None else new_file)

    @property
    def mediafile(self):
        return self.__mediafile

    @mediafile.setter
    def mediafile(self, mediafile):
        self.__mediafile = mediafile

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, result):
        self.__result = result

    @property
    def new_file(self):
        return self.__new_file

    @new_file.setter
    def new_file(self, new_file):
        self.__new_file = new_file

    def create_cmd(self, print_debug = False):
        txt = self.mediafile.getInfo()
        if print_debug == True:
            self.log.debug(txt)
        if txt == "":
            self.log.error("Info could not be generated")
            raise Exception(txt)

        # Use ffmpeg
        self.args = ["ffmpeg", "-hide_banner", "-loglevel", "info", "-vsync", "0"]

        # Extend stream scan for VOB
        if ".vob" in self.mediafile.name:
            self.args.extend(["-analyzeduration", "500M", "-probesize", "500M"])
        else :
            self.args.extend(["-analyzeduration", "250M", "-probesize", "250M"])

        #v_index = 0
        #for v_stream in self.mediafile.getVideoStreams():
            # self.args.extend(["-hwaccel", "cuda", "-hwaccel_output_format", "cuda", "-c:v:{}".format(v_index)])
            # Use hwaccel for x264, mpeg4, mpeg2 decoding
            # if v_stream.codec in ["h264", "mpeg2", "mpeg2video"]: # "mpeg4"
                #self.args.extend(["-hwaccel", "cuvid", "-c:v:{}".format(v_index)])
                #if v_stream.codec == "h264":
                #    self.args.extend(["h264_cuvid"])
                #elif v_stream.codec == "mpeg4": # Disabled
                #    self.args.extend(["mpeg4_cuvid"])
                #elif v_stream.codec in ["mpeg2", "mpeg2video"]:
                #    self.args.extend(["mpeg2_cuvid"])

        # Set decode hwaccel
        self.args.extend(["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"])
        # Add main input file
        self.args.extend(["-i", self.mediafile.name])

        # Add srt input files
        m_index = 1
        for s_file in self.mediafile.getSubtitleFiles():
            self.args.extend(["-sub_charenc", s_file.encoding, "-i", s_file.name])
            m_index += 1

        # Loop over video steams
        for v_stream in self.mediafile.getVideoStreams():
            self.args.extend(["-map", "0:{}".format(v_stream.index)])

        # Loop over audio streams
        for a_stream in self.mediafile.getAudioStreams():
            self.args.extend(["-map", "0:{}".format(a_stream.index)])

        # Loop over subtitle streams
        for s_stream in self.mediafile.getSubtitleStreams():
            if s_stream.codec in ["subrip", "ass", "dvd_subtitle", "dvb_subtitle", "pgssub", "hdmv_pgs_subtitle"]:
                self.args.extend(["-map", "0:{}".format(s_stream.index)])

        # Loop over subtitle files
        for i in range(1, m_index):
            self.args.extend(["-map", "{}".format(i)])

        # Video encoder settings
        v_index = 0
        for v_stream in self.mediafile.getVideoStreams():
            # Encode to HEVC with nvenc
            self.args.extend(["-c:v:{}".format(v_index), "hevc_nvenc"])
            # Use preset slow, vbr_hq, 2pass
            self.args.extend(["-preset", "slow", "-rc", "vbr", "-rc-lookahead", "32"])
            # Requested Quality
            self.args.extend(["-cq", "28"])
            # Intra Frames
            self.args.extend(["-g", "250"])
            # Quality Min - Max
            self.args.extend(["-qmin", "0", "-qmax", "34"])
            # Set bitrate targets, bitrate=0 maxrate=input_bitrate
            self.args.extend(["-b:v:{}".format(v_index), "0", "-maxrate", str(v_stream.bitrate)])
            # Set buffer to 2 * maxrate
            self.args.extend(["-bufsize", str(v_stream.bitrate * 2)])
            # Use spatial aq
            self.args.extend(["-spatial_aq", "1", "-aq-strength", "15"])
            v_index += 1

        # Config audio streams
        a_index = 0
        for a_stream in self.mediafile.getAudioStreams():
            # Audio encoder settings
            a_encoder = "copy"
            self.args.extend(["-c:a:{}".format(a_index), a_encoder])
            a_index += 1

        # Config subtitle streams
        s_index = 0
        for s_stream in self.mediafile.getSubtitleStreams():
            if s_stream.codec in ["subrip", "ass", "dvd_subtitle", "dvb_subtitle", "pgssub", "hdmv_pgs_subtitle"]:
                self.args.extend(["-c:s:{}".format(s_index), "copy"])
            s_index += 1

        # Set output filename
        self.args.extend(["-f", "matroska", self.new_file.name])
        return
