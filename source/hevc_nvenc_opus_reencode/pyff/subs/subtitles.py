import os
import re
import glob

import pycountry
import langdetect
from langdetect import DetectorFactory

from ..objects import SubtitleFile, Movie, Series
from ..fops import detect_encoding, convert_encoding

DetectorFactory.seed = 0

def detect_subtitles(mediafile, mediainfo):
    files = []
    res = glob.glob(mediafile.path + "/*.srt", recursive=True)
    files.extend(res)
    res = glob.glob(mediafile.path + "/subs/*.srt", recursive=True)
    files.extend(res)
    res = glob.glob(mediafile.path + "/Subs/*.srt", recursive=True)
    files.extend(res)

    title = ""
    ptrn_e = None
    ptrn_s = None
    ptrn_t = None

    if isinstance(mediainfo, Movie):
        title = mediainfo.title
    elif isinstance(mediainfo, Series):
        # Make regex for Episode, Season
        ep = str(mediainfo.seasons[0].episodes[0].episode)
        ptrn_e = re.compile("e{ep}|x{ep}".format(ep = ep.zfill(2)), re.I)
        se = str(mediainfo.seasons[0].season)
        ptrn_s = re.compile("s{se}|{se}x".format(se = se.zfill(2)), re.I)
        title = mediainfo.seasons[0].episodes[0].title

    # Make regex for Title
    i = True
    rs = ""
    for t in title.split(" "):
        if i == True:
            rs += "{}".format(t)
            i = False
        else:
            rs += "|{}".format(t)
    if rs != "":
        ptrn_t = re.compile(rs, re.I)

    # Make regex for lang
    swe = re.compile(r"sv|swe", re.I)
    eng = re.compile(r"en|eng", re.I)

    # Loop trough subtitle files
    for s_name in files:
        f = os.path.basename(s_name)

        # Chech if title matches
        tt = None
        if ptrn_t != None:
            tt = ptrn_t.search(f)

        # Check if file matches Episode (EXX)
        ep = None
        if ptrn_e != None:
            ep = ptrn_e.search(f)

        # Check if file matches Season (SXX)
        se = None
        if ptrn_s != None:
            se = ptrn_s.search(f)

        if isinstance(mediainfo, Movie):
            if tt == None:
                continue
        elif isinstance(mediainfo, Series):
            if ep == None:
                continue

        # Detect file encoding
        s_file = SubtitleFile(s_name, "srt")
        res = detect_encoding(s_file)
        if res == False:
            continue

        # Convert to utf-8
        if convert_encoding(s_file, "utf-8") == False:
            continue

        # Find language
        if swe.search(f) != None:
            s_file.language = "swe"
        elif eng.search(f) != None:
            s_file.language = "eng"
        else:
            res = detect_language(s_file)

        # Put info into file info
        mediafile.appendSubtitleFile(s_file)

def detect_language(s_file):
    try:
        with open(s_file.name, "r", encoding=s_file.encoding) as f:
            content = f.readlines()
    except Exception as e:
        print(e)
        return False

    # Sanitize file text for better detection
    regx = re.compile(r"[0-9]{1,}\n", re.I)
    text = ""
    for line in content:
        if "-->" in line:
            continue
        if line == "\n":
            continue
        if regx.search(line) != None:
            continue
        text += line[:-1] + " "
    # Do detection
    res = langdetect.detect(text)
    lang = pycountry.languages.get(alpha_2=res)
    s_file.language = lang.alpha_3
    return True