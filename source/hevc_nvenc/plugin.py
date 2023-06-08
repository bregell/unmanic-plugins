#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    hevc_nvenc

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

from unmanic.libs.unplugins.settings import PluginSettings
from unmanic.libs.system import System

from hevc_nvenc.lib.ffmpeg import Probe, Parser
from hevc_nvenc.lib.pyff import MediaFile, TranscodeJob, TranscodeResult

# Configure plugin logger
logger = logging.getLogger("Unmanic.Plugin.hevc_nvenc")


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
    """
    Runner function - enables additional actions during the library management file tests.

    The 'data' object argument includes:
        path                            - String containing the full path to the file being tested.
        issues                          - List of currently found issues for not processing the file.
        add_file_to_pending_tasks       - Boolean, is the file currently marked to be added to the queue for processing.

    :param data:
    :return:

    """


    # Check for HEVC in filename
    if "hevc" in m_file.name.lower():
        txt = "{}: File is HEVC".format(m_file.name)
        m_file.log.debug(txt)
        return False

    if "x265" in m_file.name.lower():
        txt = "{}: File is x265".format(m_file.name)
        m_file.log.debug(txt)
        return False

    if "h265" in m_file.name.lower():
        txt = "{}: File is h265".format(m_file.name)
        m_file.log.debug(txt)
        return False

    # Get file info
    txt = m_file.getInfo()
    if len(m_file.getVideoStreams()) == 0:
        m_file.log.debug(txt)
        return False

    txt = "{}: Add to pending tasks".format(m_file.name)
    m_file.log.debug(txt)

    return True

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

    m_file = MediaFile(in_abs, log = logger)
    m_file.getInfo()

    run_hevc = check_run(m_file)

    if run_hevc:
        m_file_new = MediaFile(out_abs, log = logger)
        t_job = TranscodeJob(m_file, logger, new_file = m_file_new)

        # Start transcoding job
        t_job.create_cmd()

        txt = "Executing: {}".format(" ".join(t_job.args))
        t_job.log.debug(txt)

        if t_job.result.status:
            data['exec_command'] = t_job.args

            # Set the parser
            # Get the path to the file
            probe = Probe(logger, allowed_mimetypes=['video'])
            probe.file(in_abs)
            parser = Parser(logger)
            parser.set_probe(probe)
            data['command_progress_parser'] = parser.parse_progress

    return data
