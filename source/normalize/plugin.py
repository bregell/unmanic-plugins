#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    opus_reencode

    UNMANIC PLUGINS OVERVIEW:

        Plugins are stand-alone Python modules that are executed at defined stages during
        the optimisation process.

        The Plugin class is made up of defined "runner" functions. For each of these functions,
        whatever parameters are provided must also be returned in the form of a tuple.

        A Plugin class may contain any number of plugin "runner" functions, however they may
        only have one of each type.

        A Plugin class may be configured by providing a dictionary "Settings" class in it's header.
        This will be accessible to users from within the Unmanic Plugin Manager WebUI.
        Plugin settings will be callable from any of the Plugin class' "runner" functions.

        A Plugin has limited access to the Unmanic process' data. However, there is no limit
        on what a plugin may carryout when it's "runner" processes are called. The only requirement
        is that the data provided to the "runner" function is returned once the execution of that
        function is complete.

        A System class has been provided to feed data to the Plugin class at the discretion of the
        Plugin's developer.
        System information can be obtained using the following syntax:
            ```
            system = System()
            system_info = system.info()
            ```
        In this above example, the system_info variable will be filled with a dictionary of a range
        of system information.

    THIS EXAMPLE:

        > The Worker Process Plugin runner
            :param data     - Dictionary object of data that will configure how the FFMPEG process is executed.

"""
import logging
import os
import re

from unmanic.libs.unplugins.settings import PluginSettings
from unmanic.libs.system import System

from normalize.lib.pyff import MediaFile

# Configure plugin logger
logger = logging.getLogger("Unmanic.Plugin.normalize")


class Settings(PluginSettings):
    """
    An object to hold a dictionary of settings accessible to the Plugin
    class and able to be configured by users from within the Unmanic WebUI.

    This class has a number of methods available to it for accessing these settings:

        > get_setting(<key>)            - Fetch a single setting value. Or leave the
                                        key argument empty and return the full dictionary.
        > set_setting(<key>, <value>)   - Set a singe setting value.
                                        Used by the Unmanic WebUI to save user settings.
                                        Settings are stored on disk in order to be persistent.

    """
    settings = {
    }


def check_run(m_file: MediaFile) -> bool:
    normalize = True
    for a_stream in m_file.getAudioStreams():
        logger.debug("Stream codec   : {}".format(a_stream.codec))
        logger.debug("Stream channels: {}".format(a_stream.channels))
        logger.debug("Stream layout  : {}".format(a_stream.channel_layout))
        if a_stream.codec == "opus" or a_stream.codec == "pcm_s16le":
            normalize = False

    return normalize

def on_worker_process(data):
    """
    Runner function - enables additional configured processing jobs during the worker stages of a task.

    The 'data' object argument includes:
        exec_command            - A command that Unmanic should execute. Can be empty.
        command_progress_parser - A function that Unmanic can use to parse the STDOUT of the command to collect progress stats. Can be empty.
        file_in                 - The source file to be processed by the command.
        file_out                - The destination that the command should output (may be the same as the file_in if necessary).
        original_file_path      - The absolute path to the original file.
        repeat                  - Boolean, should this runner be executed again once completed with the same variables.

    :param data:
    :return:
    """
    settings = Settings()
    system = System()
    system_info = system.info()

    in_abs = os.path.abspath(data.get('file_in'))
    out_abs = os.path.abspath(data.get('file_out'))

    m_file = MediaFile(name = in_abs, log = logger)
    m_file.getInfo()
    run_norm = check_run(m_file)

    if run_norm:
        cmd = [
            'ffmpeg-normalize',
            in_abs,
            '-o', out_abs,
            '-v',
            '-pr',
        ]

        # Set exec cmd
        data['exec_command'] = cmd

        # Create parser
        parser = Parser(logger)

        # Set the parser
        data['command_progress_parser'] = parser.parse

    return data


class Parser(object):
    data = {
        'percent': 0
    }
    percent = 0
    pass_nr = 0
    streams = None
    stream = None
    steps = 0
    step = 0

    def __init__(self, logger):
        self.logger = logger

    def parse(self, line_text):
        # Count streams
        if self.streams == None:
            streams_re = re.compile(r"Stream [0-9]{1,}\/([0-9]{1,})", re.I)
            streams_res = streams_re.search(line_text)
            if streams_res != None:
                self.streams = int(streams_res.group(1))
                self.steps = self.streams + 1
                self.logger.debug("Streams: {}".format(streams_res.group(1)))

        if self.pass_nr == 0:
            # Search for first pass
            pass_re = re.compile(r"first pass", re.I)
            pass_res = pass_re.search(line_text)
            if pass_res != None:
                self.logger.debug("First pass")
                self.pass_nr = 1
                self.step = 1

        if self.pass_nr == 1:
            # Search for start of second pass
            pass_re = re.compile(r"Second Pass", re.I)
            pass_res = pass_re.search(line_text)
            if pass_res != None:
                self.logger.debug("Second pass")
                self.pass_nr = 2
                self.step = self.steps - 1

            # Set current stream
            stream_re = re.compile(r"Stream ([0-9]{1,})\/[0-9]{1,}", re.I)
            stream_res = stream_re.search(line_text)
            if stream_res != None:
                self.stream = int(stream_res.group(1))
                self.step = self.stream
                self.logger.debug(f"Stream: {self.step}")

        # Search for percent in the progress bar line output
        percent_re = re.compile(r"[0-9]{1,3}%")
        re_result = percent_re.search(line_text)
        percent_new = None
        if re_result != None:
            percent_new = int(re_result[0][:-1])

        if percent_new != None and self.steps != None and self.steps > 0:
            offset = 100 / self.steps
            percent_calc = (percent_new / self.steps) + (offset * self.step) - offset
            self.percent = round(percent_calc)

        self.data = {
            'percent': self.percent
        }

        return self.data
