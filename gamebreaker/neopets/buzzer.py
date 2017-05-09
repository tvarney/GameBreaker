
from gamebreaker import image
import pyautogui
import gamebreaker.neopets.common as np
from PIL import Image
import win32api, win32con
from time import sleep

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


def _set_pixel(pos, offset, image, color):
    image.putpixel((pos[0] + offset[0], pos[1] + offset[1]), color)


def solid_black(pos, data, width):
    for i in range(-2, 2, 1):
        for j in range(-2, 2, 1):
            if _get_pixel(pos, (i, j), width, data) != (0, 0, 0):
                return False
    return True


def draw_centered_rect(image, pos, radius: int, color = (0, 0, 0)):
    for i in range(-radius, radius, 1):
        for j in range(-radius, radius, 1):
            _set_pixel(pos, (i, j), image, color)


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
            elif pixel == (0, 204, 0) or pixel == (0, 156, 0):
                if start is None:
                    start = x, y
                mask.putpixel((x, y), (0, 0, 0))
    return start, end, mask


def _sssp_put(array, pos, width, value):
    array[pos[0]+pos[1]*width] = value


def _sssp_get(array, pos, width):
    return array[pos[0]+pos[1]*width]


_offsets = [
    (0, 1), (0, -1), (-1,  0), (1, 0), (-1, 1), (1, 1), (-1, -1), (1, -1)
]
def dijkstra_sssp(mask, start, stop):
    width = mask.width
    height = mask.height

    mask_data = mask.getdata()
    edge = [stop]
    visited = [(2**32-1) for i in range(width*height)]
    _sssp_put(visited, stop, width, 0)
    while len(edge) > 0:
        position = edge.pop(0)
        value = _sssp_get(visited, position, width) + 1
        for offset in _offsets:
            npos = (position[0] + offset[0], position[1] + offset[1])
            old_value = _sssp_get(visited, npos, width)
            if old_value > value:
                if _get_pixel(position, offset, width, mask_data) == (0, 0, 0):
                    _sssp_put(visited, npos, width, value)
                    # Should probably use a set instead of an array (meh)
                    edge.append(npos)

    # Follow the path
    path = []
    pos = start
    while pos != stop:
        minval = 2**32-1
        move = None
        for offset in _offsets:
            npos = (pos[0] + offset[0], pos[1] + offset[1])
            value = _sssp_get(visited, npos, width)
            if value < minval:
                move = npos
                minval = value
        if move is None:
            print("SSSP: Failed; could not find valid path")
            break
        path.append(move)
        pos = move

    return path


def run():
    im = image.ImageGrabber()
    bbox = np.GetGameArea()
    if bbox is None:
        print("Could not locate neopets game area")
        return

    area = im.grab_area(bbox, False)
    start, end, mask = create_mask(area)
    if start is not None:
        draw_centered_rect(mask, start, 3, (0, 0, 0))
    if end is not None:
        draw_centered_rect(mask, end, 3, (0, 0, 0))

    #print(start)
    #mask.show("Game Mask")

    path = dijkstra_sssp(mask, start, end)
    ul = bbox['left'], bbox['top']
    #win32api.SetCursorPos((start[0] + ul[0], start[1] + ul[1]))

    if len(path) == 0:
        print("No points in path")
        return

    pyautogui.click()
    print("Path Length: {}".format(len(path)))
    print("Time: {} seconds".format(0.05 * len(path)))
    for pos in path:
        win32api.SetCursorPos((pos[0] + ul[0], pos[1] + ul[1]))
        sleep(0.003)

    win32api.SetCursorPos((end[0] + ul[0], end[1] + ul[1]))
    # mask.show("Path")

if __name__=="__main__":
    run()