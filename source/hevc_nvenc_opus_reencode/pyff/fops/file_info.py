import subprocess
import json
import re

import chardet
import send2trash

from ..objects import VideoStream, AudioStream, SubtitleStream

def remove_file(mediafile, log):
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
def get_file_info(mediafile, print_debug = False):
    # Command
    args = ["ffprobe", "-v", "quiet", "-hide_banner", "-show_format", "-show_streams", "-print_format", "json"]

    if ".vob" in mediafile.name:
        args.extend(["-analyzeduration", "500M", "-probesize", "500M"])
    else:
        args.extend(["-analyzeduration", "250M", "-probesize", "250M"])

    args.extend(["-i",  mediafile.name])

    # Get file info from ffprobe
    info_json = None
    try :
        info_json = subprocess.check_output(args)
    except:
        txt = "File: {} was unreadable, skipping.".format(mediafile.name)
        mediafile.log.print(txt)
        return False, txt

    data = info_json.decode('utf8')
    json_data = json.loads(data)

    # Get file size
    mediafile.size = int(json_data["format"]["size"])

    # Get media length
    mediafile.length = 0.0
    if "duration" in json_data["format"]:
        mediafile.length = float(json_data["format"]["duration"])

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
            mediafile.appendVideoStream(v_stream)
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
            mediafile.appendAudioStream(a_stream)
            continue
        # Subtitle
        if item["codec_type"] == "subtitle":
            language = "unk"
            if "tags" in item and "language" in item["tags"]:
                language = item["tags"]["language"]
            s_stream = SubtitleStream(item["index"], item["codec_name"], language)
            mediafile.appendSubtitleStream(s_stream)
            continue

    if mediafile.getVideoStreams() == [] or mediafile.getAudioStreams() == []:
        txt = "File: {} No audio and/or video codec could be found.".format(mediafile.name)
        mediafile.log.print(txt)
        return False, txt

    # Special calculation for vido bitrate if missing from stream
    f_bitrate = int(json_data["format"]["bit_rate"])
    a_bitrate_total = 0
    v_bitrate_total = 0
    v_bitrate_missing = 0
    for a_stream in mediafile.getAudioStreams():
        a_bitrate_total += a_stream.bitrate
    for v_stream in mediafile.getVideoStreams():
        if v_stream.bitrate != 0:
            v_bitrate_total += v_stream.bitrate
        else:
            v_bitrate_missing += 1
    for v_stream in mediafile.getVideoStreams():
        if v_stream.bitrate == 0:
            v_stream.bitrate = int((f_bitrate - v_bitrate_total - a_bitrate_total) / v_bitrate_missing)

    # Audio sanity (transparency level)
    for a_stream in mediafile.getAudioStreams():
        a_bitrate = a_stream.bitrate
        if a_bitrate > 320000:
            a_stream.bitrate = 320000
        elif a_bitrate < 96000:
            a_stream.bitrate = 96000

    # Video sanity (transparency level)
    for v_stream in mediafile.getVideoStreams():
        if v_stream.width == None:
            txt = "Unknown video width for: {}".format(mediafile.name)
            mediafile.log.print(txt)
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

    return True, "Success"

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