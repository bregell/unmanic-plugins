from .mediastream import MediaStream

class AudioStream(MediaStream):
    def __init__(self, index, codec, bitrate, channels, channel_layout):
        MediaStream.__init__(self, index, codec, bitrate)
        self.__channels = channels
        self.__channel_layout = channel_layout

    @property
    def channels(self):
        return self.__channels

    @channels.setter
    def channels(self, channels):
        if type(channels) is not int:
            raise TypeError("Channels must be interger")
        self.__channels = channels

    @property
    def channel_layout(self):
        return self.__channel_layout

    @channel_layout.setter
    def channel_layout(self, channel_layout):
        self.__channel_layout = channel_layout

    def getInfo(self):
        txt = ""
        txt += MediaStream.getInfo(self) + ", "
        txt += "Channels: {}, Channel Layout: {}".format(self.channels, self.channel_layout)
        return txt
