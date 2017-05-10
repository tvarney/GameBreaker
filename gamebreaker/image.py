
import cv2
import mss
import numpy
from PIL import Image

TM_CCOEFF = cv2.TM_CCOEFF
TM_CCOEFF_NORMED = cv2.TM_CCOEFF_NORMED
TM_CCORR = cv2.TM_CCORR
TM_CCORR_NORMED = cv2.TM_CCORR_NORMED
TM_SQDIFF = cv2.TM_SQDIFF
TM_SQDIFF_NORMED = cv2.TM_SQDIFF_NORMED

Format = 'RGB'


class ImageGrabber(object):
    AllMonitors = 0
    FirstMonitor = 1

    def __init__(self):
        self.sct = mss.mss()
        self.displays = self.sct.enum_display_monitors()

    @staticmethod
    def make_bbox(x, y, width, height):
        return {'left': x, 'top': y, 'width': width, 'height': height}

    def monitor_dimensions(self, monitor: int):
        return self.displays[monitor]['width'], self.displays[monitor]['height']

    # Timings:
    #     3840x1080: 200 ms
    #     1920x1080: 90 ms
    #     800x600: 35 ms
    def grab_screen(self, monitor: int, convert: bool = False, grayscale: bool = False):
        pixels = self.sct.get_pixels(self.displays[monitor])
        img = Image.frombytes(Format, (self.monitor_dimensions(monitor)), pixels)
        if grayscale:
            img.convert('L').convert(Format)
        return numpy.array(img) if convert else img

    def grab_area(self, bbox, convert: bool = False, grayscale: bool = False):
        img = Image.frombytes(Format, (bbox['width'], bbox['height']), self.sct.get_pixels(bbox))
        if grayscale:
            img = img.convert('L').convert(Format)
        return numpy.array(img) if convert else img


def find_match(img_source, img_object, method: int):
    result_image = cv2.matchTemplate(img_source, img_object, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_image)

    if method in [TM_SQDIFF, TM_SQDIFF_NORMED]:
        return min_val, min_loc
    return max_val, max_loc


def load_from_file(filename, convert: bool = False, grayscale: bool = False):
    img = Image.open(filename, "r")
    if grayscale:
        img = img.convert('L').convert(Format)
    return numpy.array(img) if convert else img
