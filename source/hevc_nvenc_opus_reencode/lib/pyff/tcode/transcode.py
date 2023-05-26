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
from logging import Logger

from hevc_nvenc_opus_reencode.lib.pyff.objects.mediafile import MediaFile

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
    def __init__(self, mediafile, log : Logger, args = None, result = None, new_file = None):
        self.mediafile = mediafile
        self.log = log
        self.args = ([] if args == None else args)
        self.result = (TranscodeResult() if result == None else result)
        self.new_file = (MediaFile("") if new_file == None else new_file)

    @property
    def mediafile(self):
        return self.__mediafile

    @mediafile.setter
    def mediafile(self, mediafile):
        if isinstance(mediafile, MediaFile) == False:
            raise TypeError("MediaFile is wrong type")
        self.__mediafile = mediafile

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, result):
        if isinstance(result, TranscodeResult) == False:
            raise TypeError("Result must be TranscodeResult")
        self.__result = result

    @property
    def new_file(self):
        return self.__new_file

    @new_file.setter
    def new_file(self, new_file):
        if isinstance(new_file, MediaFile) == False:
            raise TypeError("new_file must be of type MediaFile")
        self.__new_file = new_file

    def create_cmd(self, print_debug = False):

        txt = self.mediafile.getInfo()
        if print_debug == True:
            self.log.debug(txt)
        if txt == "":
            self.log.error("Info could not be generated")
            raise Exception(txt)

        # Use ffmpeg
        self.args = ["ffmpeg.exe", "-hide_banner", "-loglevel", "info", "-vsync", "0"]

        # Extend stream scan for VOB
        if ".vob" in self.mediafile.name:
            self.args.extend(["-analyzeduration", "500M", "-probesize", "500M"])
        else :
            self.args.extend(["-analyzeduration", "250M", "-probesize", "250M"])

        v_index = 0
        for v_stream in self.mediafile.getVideoStreams():
            # Use hwaccel for x264, mpeg4, mpeg2 decoding
            if v_stream.codec in ["h264", "mpeg2", "mpeg2video"]: # "mpeg4"
                #self.args.extend(["-hwaccel", "cuda", "-hwaccel_output_format", "cuda", "-c:v:{}".format(v_index)])
                self.args.extend(["-hwaccel", "cuvid", "-c:v:{}".format(v_index)])
                if v_stream.codec == "h264":
                    self.args.extend(["h264_cuvid"])
                elif v_stream.codec == "mpeg4": # Disabled
                    self.args.extend(["mpeg4_cuvid"])
                elif v_stream.codec in ["mpeg2", "mpeg2video"]:
                    self.args.extend(["mpeg2_cuvid"])

        # Add main input file
        self.args.extend(["-i", self.mediafile.name])

        # Add srt input files
        m_index = 1
        for s_file in self.mediafile.getSubtitleFiles():
            self.args.extend(["-sub_charenc", s_file.encoding, "-i", s_file.name])
            m_index += 1

        # Get main video steam
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
            self.args.extend(["-preset", "slow", "-rc", "vbr_hq", "-rc-lookahead", "32"])
            # Requested Quality
            self.args.extend(["-cq", "28"])
            # Intra Frames
            self.args.extend(["-g", "250"])
            # Quality Min - Max
            self.args.extend(["-qmin", "0", "-qmax", "34"])
            # Set bitrate targets, bitrate=0 maxrate=2*input_bitrate
            self.args.extend(["-b:v:{}".format(v_index), "0", "-maxrate", str(v_stream.bitrate)])
            # Set buffer to 2 * maxrate
            self.args.extend(["-bufsize", str(v_stream.bitrate * 2)])
            # Use spatial aq
            self.args.extend(["-spatial_aq", "1", "-aq-strength", "15"])
            v_index += 1

        # Config audio streams
        a_index = 0
        for a_stream in self.mediafile.getAudioStreams():
            # Set audio encoder
            if a_stream.codec == 'copy':
                a_encoder = "copy"
            elif a_stream.codec != 'opus':
                a_encoder = "libopus"
            else:
                a_encoder = "copy"

            # Audio encoder settings
            self.args.extend(["-c:a:{}".format(a_index), a_encoder])

            # If audio is not copy add channelmap and encoder settings
            if a_encoder != "copy":
                # Remove side and wide channels
                a_stream.channel_layout = re.search(r'^[^\(]+', a_stream.channel_layout).group(0)
                # Set channel_layout
                channel_config = "channelmap=channel_layout={}".format(a_stream.channel_layout)
                # Set compression level to "lossless"
                self.args.extend(["-filter:a:{}".format(a_index), channel_config, "-compression_level", "10"])
                # Set bitrate
                self.args.extend(["-b:a:{}".format(a_index), "{}".format(a_stream.bitrate)])
            a_index += 1

        # Config subtitle streams
        s_index = 0
        for s_stream in self.mediafile.getSubtitleStreams():
            if s_stream.codec in ["subrip", "ass", "dvd_subtitle", "dvb_subtitle", "pgssub", "hdmv_pgs_subtitle"]:
                self.args.extend(["-c:s:{}".format(s_index), "copy"])
            s_index += 1

        # Set output filename
        self.args.extend(["-f", "matroska", self.new_file.name])
        txt = "FFmpeg Command: {}".format(" ".join(self.args))
        self.log.info(txt)

        return
