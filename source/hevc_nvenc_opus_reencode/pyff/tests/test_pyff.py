from unittest import TestCase

from ..fops import get_file_info

class Pyff(TestCase):
    def test_get_file_info(self, mediafile, log):
        file_info = {}
        file_info["f_name"] = "test.txt"
        s, _ = get_file_info(mediafile, log)
        self.assertTrue(s)