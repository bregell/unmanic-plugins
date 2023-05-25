from .mediastream import MediaStream

class VideoStream(MediaStream):
    def __init__(self, index, codec, bitrate, width, height):
        MediaStream.__init__(self, index, codec, bitrate)
        self.__height = height
        self.__width = width

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, height):
        if type(height) is not int:
            raise TypeError("Height is not integer")
        if height < 0:
            raise ValueError("Height should be a positive number over zero")
        self.__height = height

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, width):
        if type(width) is not int:
            raise TypeError("Width is not integer")
        if width < 0:
            raise ValueError("Width should be a positive number over zero")
        self.__width = width

    def getInfo(self):
        txt = ""
        txt += MediaStream.getInfo(self) + ", "
        txt += "Width: {}, Heigth {}".format(self.width, self.height)
        return txt
