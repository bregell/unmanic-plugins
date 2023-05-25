from .basefile import BaseFile
from .videostream import VideoStream
from .audiostream import AudioStream
from .subtitlestream import SubtitleStream
from .subtitlefile import SubtitleFile

class MediaFile(BaseFile):
    def __init__(self, name, size = 0, length = 0.0, v_streams = None, a_streams = None, s_streams = None, s_files = None):
        BaseFile.__init__(self, name, size)
        self.length = length
        self.v_streams  = ([] if v_streams  == None else v_streams)
        self.a_streams  = ([] if a_streams  == None else a_streams)
        self.s_streams  = ([] if s_streams  == None else s_streams)
        self.s_files    = ([] if s_files    == None else s_files)

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
        if type(v_stream) is not VideoStream:
            raise TypeError("Must be of type VideoStream")
        self.v_streams.append(v_stream)

    def getAudioStreams(self):
        return self.a_streams

    def appendAudioStream(self, a_stream):
        if type(a_stream) is not AudioStream:
            raise TypeError("Must be of type AudioStream")
        self.a_streams.append(a_stream)

    def getSubtitleStreams(self):
        return self.s_streams

    def appendSubtitleStream(self, s_stream):
        if type(s_stream) is not SubtitleStream:
            raise TypeError("Must be of type SubtitleStream")
        self.s_streams.append(s_stream)

    def getSubtitleFiles(self):
        return self.s_files

    def appendSubtitleFile(self, s_file):
        if type(s_file) is not SubtitleFile:
            raise TypeError("Must be of type SubtitleFile")
        self.s_files.append(s_file)

    def getInfo(self):
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