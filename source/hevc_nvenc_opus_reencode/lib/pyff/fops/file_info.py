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

import subprocess
import json
import re

import chardet
import send2trash

from hevc_nvenc_opus_reencode.lib.pyff.objects.videostream import VideoStream
from hevc_nvenc_opus_reencode.lib.pyff.objects.audiostream import AudioStream
from hevc_nvenc_opus_reencode.lib.pyff.objects.subtitlestream import SubtitleStream
from hevc_nvenc_opus_reencode.lib.pyff.objects.mediafile import MediaFile

def remove_file(mediafile: MediaFile, log):
    try:
        send2trash.send2trash(mediafile.name)
        #os.remove(file_name)
    except Exception as e:
        txt = "Failed to remove: {}, result: {}".format(mediafile.name, e)
        print(txt)
        log.print(txt)
        return
    txt = "Succefully removed: {}".format(mediafile.name)
    print(txt)
    log.print(txt)
    return

################################################
def detect_encoding(s_file):
    with open(s_file.name, "rb") as f:
        detector = chardet.UniversalDetector()
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    if "encoding" not in detector.result:
        False
    s_file.encoding = detector.result["encoding"]
    return True

################################################
def convert_encoding(s_file, enc_out = "utf-8"):
    content = None
    try:
        with open(s_file.name, "r", encoding=s_file.encoding) as f:
            content = f.read()
    except Exception as e:
        print(e)
        return False

    if content == None:
        return False

    try:
        with open(s_file.name, "w", encoding=enc_out) as f:
            f.write(content)
    except Exception as e:
        print(e)
        return False

    return True