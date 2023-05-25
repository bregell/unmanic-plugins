import humanize

from .stream import Stream

class MediaStream(Stream):
    def __init__(self, index, codec, bitrate):
        Stream.__init__(self, index, codec)
        self.__bitrate = bitrate

    @property
    def bitrate(self):
        return self.__bitrate

    @bitrate.setter
    def bitrate(self, bitrate):
        if type(bitrate) is not int:
            raise TypeError("Bitrate is not integer")
        self.__bitrate = bitrate

    def getInfo(self):
        txt = ""
        txt += Stream.getInfo(self) + ", "
        txt += "Bitrate: {}/s".format(humanize.naturalsize(self.bitrate))
        return txt