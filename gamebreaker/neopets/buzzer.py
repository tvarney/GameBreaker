
from gamebreaker import image
import pyautogui
import gamebreaker.neopets.common as np
from PIL import Image

target_color = (204, 0, 0)
start_color = (0, 204, 0)
wire_color = (0, 0, 0)
used_color = (255, 0, 255)


def add_pos(vec, add):
    return vec[0] + add[0], vec[1] + add[1]


def is_on_start() -> bool:
    position = pyautogui.position()
    return pyautogui.pixelMatchesColor(position[0], position[1], start_color)


def move_off_start():
    return


def _get_pixel(pos, offset, width, data):
    return data[(pos[0] + offset[0]) + (pos[1] + offset[1]) * width]


def solid_black(pos, data, width):
    for i in range(-2, 2, 1):
        for j in range(-2, 2, 1):
            if _get_pixel(pos, (i, j), width, data) != (0, 0, 0):
                return False
    return True


def create_mask(area):
    start = None
    end = None
    mask = Image.new('RGB', (area.width, area.height), (255,255,255))
    data = area.getdata()
    # print("Area: {}x{}".format(area.width, area.height))
    for y in range(area.height - 1):
        for x in range(area.width - 1):
            pixel = area.getpixel((x, y))
            if pixel == (0, 0, 0):
                if solid_black((x, y), data, area.width):
                    mask.putpixel((x, y), (0, 0, 0))
            elif pixel == (204, 0, 0):
                if end is None:
                    end = x, y
                mask.putpixel((x, y), (0, 0, 0))
            elif pixel == (0, 204, 0):
                if start is None:
                    start = x, y
                mask.putpixel((x, y), (0, 0, 0))
    return start, end, mask


def run():
    im = image.ImageGrabber()
    bbox = np.GetGameArea()
    if bbox is None:
        print("Could not locate neopets game area")
        return

    area = im.grab_area(bbox, False)
    start, end, mask = create_mask(area)
    
    print(start)
    mask.show("Game Mask")


if __name__=="__main__":
    run()