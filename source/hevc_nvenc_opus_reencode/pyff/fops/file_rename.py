import os
import re
from difflib import SequenceMatcher

from guessit import guessit as guessit


def similar(a, b):
    return

from ..objects import Episode, Season, Series, Movie, MiniSeries

def get_episode(full_name, m_title):
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

def get_season(f_name):
    # Get season (if possible)
    info = guessit(f_name)
    s_number = 1
    if "season" in info:
        s_number = info["season"]
    m_season = Season(s_number)
    return m_season

def get_type(f_name):
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

def get_title(f_name, m_type):
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

def get_media_info(mediafile):
    m_type = get_type(mediafile.name)
    if m_type == None:
        return None
    m_title = get_title(mediafile.name, m_type)
    if m_title == None:
        return None
    m_type.title = m_title
    if isinstance(m_type, Series):
        m_episode = get_episode(mediafile.name, m_title)
        if m_episode == None:
            return None
        m_season = get_season(mediafile.name)
        if m_season == None:
            return None
        m_season.addEpisode(m_episode)
        m_type.addSeason(m_season)
    elif isinstance(m_type, MiniSeries):
        m_episode = get_episode(mediafile.name, m_title)
        if m_episode == None:
            return None
        m_type.addEpisode(m_episode)
    return m_type

def get_new_name(mediafile, mediainfo):
    new_name = ""
    # Movie Title, Series Title
    first = True
    for t in mediainfo.title.split(" "):
        if first == True:
            new_name += "{}".format(t)
            first = False
        else:
            new_name += ".{}".format(t)
    if isinstance(mediainfo, Series):
        m_season = mediainfo.seasons[0]
        m_episode = m_season.episodes[0]
        # Season
        new_name += ".S{}".format(str(m_season.season).zfill(2))
        # Episode
        # Check for dual episodes
        if type(m_episode.episode) == int:
            ep = [m_episode.episode]
        else:
            ep = m_episode.episode
        for e in ep:
            new_name += "E{}".format(str(e).zfill(2))
        # Episode Title
        if m_episode.title != "":
            for es in  m_episode.title.split(" "):
                new_name += ".{}".format(es)
    elif isinstance(mediainfo, MiniSeries):
        m_episode = mediainfo.episodes[0]
        # Episode
        # Check for dual episodes
        if type(m_episode.episode) == int:
            ep = [m_episode.episode]
        else:
            ep = m_episode.episode
        for e in ep:
            new_name += ".E{}".format(str(e).zfill(2))
        # Episode Title
        if m_episode.title != "":
            for es in  m_episode.title.split(" "):
                new_name += ".{}".format(es)
    # Encoding and such
    new_name = new_name.replace(".HVEC", "")
    new_name = new_name.replace("_HVEC", "")
    new_name += ".{}".format("h265")
    new_name += ".{}".format("mkv")
    return os.path.join(mediafile.path, new_name)