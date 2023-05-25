#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    hevc_nvenc_opus_reencode

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

from ffmpeg import StreamMapper, Probe, Parser

from pyff.objects import MediaFile
from pyff.fops import get_file_info, get_media_info
from pyff.tcode import transcode_file, TranscodeJob, TranscodeResult

# Configure plugin logger
logger = logging.getLogger("Unmanic.Plugin.hevc_nvenc_opus_reencode")


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

def on_library_management_file_test(data):
    """
    Runner function - enables additional actions during the library management file tests.

    The 'data' object argument includes:
        path                            - String containing the full path to the file being tested.
        issues                          - List of currently found issues for not processing the file.
        add_file_to_pending_tasks       - Boolean, is the file currently marked to be added to the queue for processing.

    :param data:
    :return:

    """
    m_file = MediaFile(data.get('path'))
    t_job = TranscodeJob(m_file, logger)
    check_file(t_job)

    data['add_file_to_pending_tasks'] = t_job.result.status
    
    return data



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

    m_file = MediaFile(data.get('file_in'))
    m_file_new = MediaFile(data.get('file_out'))
    t_job = TranscodeJob(m_file, logger, new_file = m_file_new)
    create_cmd(t_job)

    if t_job.result.status:
        data['exec_command'] = t_job.args
        
        # Set the parser
        probe = Probe(logger, allowed_mimetypes=['video'])
        parser = Parser(logger)
        parser.set_probe(probe)
        data['command_progress_parser'] = parser.parse_progress
    

    return data

################
## Check file ##
################
def check_file(t_job):
    # Check for _HEVC in filename
    if "HEVC" in t_job.mediafile.name:
        t_job.result = TranscodeResult(False, "File is HEVC")
        return

    # Get media info
    mediainfo = get_media_info(t_job.mediafile)
    if mediainfo == None:
         t_job.result = TranscodeResult(False, "Could not parse media info")
         return

     # Check that files are not already transcoded (HEVC)
    if os.path.isfile(t_job.new_file.name) == True:
        t_job.result = TranscodeResult(False, "File already has HEVC version")
        return
    
    t_job.result = TranscodeResult(True, "Add to pending tasks")
    return 

####################
## Process a file ##
####################
def create_cmd(t_job):
    # Get file info
    result, txt = get_file_info(t_job.mediafile)
    if result == False:
        t_job.result = TranscodeResult(False, txt)
        t_job.log.print(txt)
        return
    for v_stream in t_job.mediafile.getVideoStreams():
        if v_stream.codec == "hevc":
            txt = "File is HEVC"
            t_job.result = TranscodeResult(False, txt)
            t_job.log.print(txt)
            return

    # Start transcoding job
    transcode_file(t_job)

    txt = "Executing: {}".format(" ".join(t_job.args))
    t_job.log.print(txt)

    return
