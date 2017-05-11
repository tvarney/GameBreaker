
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
            print("Converting to Grayscale")
            img.convert('L').convert(Format)
        return numpy.array(img) if convert else img

    def grab_area(self, bbox, convert: bool = False, grayscale: bool = False):
        img = Image.frombytes(Format, (bbox['width'], bbox['height']), self.sct.get_pixels(bbox))
        if grayscale:
            print("Converting to Grayscale")
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
    print("Loaded {} as {}".format(filename, img.mode))
    if grayscale:
        print("Converting to Grayscale")
        img = img.convert('L').convert(Format)
    if img.mode == "RGBA":
        img = img.convert("RGB")
    return numpy.array(img) if convert else img


def apply_mask(source, mask, mask_color = (0, 0, 0)):
    dim = min(source.width, mask.width), min(source.height, mask.height)
    result = Image.new('RGB', dim)
    for y in range(dim[1]):
        for x in range(dim[0]):
            pixel = mask.getpixel((x, y))
            if pixel != (0, 0, 0):
                pixel = source.getpixel((x, y))
            else:
                pixel = mask_color

            result.putpixel((x, y), pixel)
    return result


def _get_pixel(pos, offset, width, data):
    return data[(pos[0] + offset[0]) + (pos[1] + offset[1]) * width]


def _set_pixel(pos, offset, image, color):
    image.putpixel((pos[0] + offset[0], pos[1] + offset[1]), color)


def check_rect(pos, data, width, colors, radius: int = 2):
    for i in range(-radius, radius, 1):
        for j in range(-radius, radius, 1):
            npos = pos[0] + i, pos[1] + j
            print("Pixel at {} = {}".format(npos, _get_pixel(pos, (i, j), width, data)))
            if not _get_pixel(pos, (i, j), width, data) in colors:
                return False
    return True


if __name__ == "__main__":
    im = ImageGrabber()
    area_pil = im.grab_area(ImageGrabber.make_bbox(10, 10, 800, 600), False, False)
    area_cv2 = im.grab_area(ImageGrabber.make_bbox(10, 10, 800, 600), True, False)

    cv2.imshow("CV2 Area", area_cv2)
    cv2.waitKey()
    cv2.destroyAllWindows()

    area_pil.show("PIL Area")
