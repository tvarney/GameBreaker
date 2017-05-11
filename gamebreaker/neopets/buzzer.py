
from gamebreaker import image
import pyautogui
import gamebreaker.neopets.common as np
from PIL import Image
import win32api, win32con
from time import sleep
import random
import os.path

target_color = (204, 0, 0)

wire_color = (0, 0, 0)
used_color = (255, 0, 255)

start_colors = [(0, g, 0) for g in range(142, 206)]
_offsets = [(0, 1), (0, -1), (-1,  0), (1, 0), (-1, 1), (1, 1), (-1, -1), (1, -1)]


def add_pos(vec, add):
    return vec[0] + add[0], vec[1] + add[1]


def _get_pixel(pos, offset, width, data):
    return data[(pos[0] + offset[0]) + (pos[1] + offset[1]) * width]


def _set_pixel(pos, offset, image, color):
    image.putpixel((pos[0] + offset[0], pos[1] + offset[1]), color)


def check_rect(pos, data, width, colors, radius: int = 2):
    for i in range(-radius, radius, 1):
        for j in range(-radius, radius, 1):
            if not _get_pixel(pos, (i, j), width, data) in colors:
                return False
    return True


def draw_centered_rect(img, pos, radius: int, color = (0, 0, 0)):
    for i in range(-radius, radius, 1):
        for j in range(-radius, radius, 1):
            _set_pixel(pos, (i, j), img, color)


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
                if check_rect((x, y), data, area.width, [(0,0,0)]):
                    mask.putpixel((x, y), (0, 0, 0))
            elif pixel == (204, 0, 0):
                if end is None and check_rect((x, y), data, area.width, [(204, 0, 0)]):
                    end = x, y
                mask.putpixel((x, y), (0, 0, 0))
            elif pixel in start_colors:
                if start is None and check_rect((x, y), data, area.width, start_colors):
                    start = x, y
                mask.putpixel((x, y), (0, 0, 0))
    # Reduce the mask
    data = mask.getdata()
    newmask = Image.new('RGB', (area.width, area.height), (255, 255, 255))
    for y in range(area.height - 1):
        for x in range(area.width - 1):
            pixel = mask.getpixel((x, y))
            if pixel == (0, 0, 0):
                if y < 10 or check_rect((x, y), data, area.width, [(0, 0, 0), 0]):
                    newmask.putpixel((x, y), (0,0,0))

    return start, end, newmask


def _sssp_put(array, pos, width, value):
    array[pos[0]+pos[1]*width] = value


def _sssp_get(array, pos, width):
    return array[pos[0]+pos[1]*width]


def dijkstra_sssp(mask, start, stop):
    if start is None:
        print("SSSP: Invalid start value of None")
        return []

    if stop is None:
        print("SSSP: Invalid stop value of None")
        return []

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


def follow_path(path, ul, start, end, random_timing : bool = False):
    win32api.SetCursorPos((start[0] + ul[0], start[1] + ul[1]))
    pyautogui.click()
    if random_timing:
        sleep(random.random()*2.0)
    for pos in path:
        win32api.SetCursorPos((pos[0] + ul[0], pos[1] + ul[1]))
        sleep(0.0022)

    win32api.SetCursorPos((end[0] + ul[0], end[1] + ul[1]))


def draw_path(screen, path, start, end):
    screen.putpixel(start, (255, 0, 255))
    for pos in path:
        screen.putpixel(pos, (255, 0, 255))
    screen.putpixel(end, (255, 0, 255))


def find_game(im: image.ImageGrabber, data_path: str = "./data/"):
    # Load the image id we use to find the game
    img_id = image.load_from_file(os.path.join(data_path, "buzzer_id.png"), True, False)
    screen = im.grab_screen(image.ImageGrabber.AllMonitors, True, False)
    match_value, ul = image.find_match(screen, img_id, image.TM_CCOEFF_NORMED)
    if match_value < 0.85:
        return None

    return im.make_bbox(ul[0]-10, ul[1]-10, 800, 600)


def play(is_main: bool = False, move_cursor: bool = True, random_timing: bool = False):
    print(is_main)
    im = image.ImageGrabber()
    bbox = None
    if is_main:
        bbox = find_game(im, "../../data")
    else:
        bbox = find_game(im)
    if bbox is None:
        print("Could not locate neopets game area")
        return

    area = im.grab_area(bbox, False)
    start, end, mask = create_mask(area)
    start_mask = mask.copy()
    print("Start: {}\nEnd: {}".format(start, end))
    if start is not None:
        draw_centered_rect(mask, start, 5, (0, 0, 0))
    else:
        print("Invalid Start Value!")
        pos = pyautogui.position()
        print("Color under cursor: {}".format(pyautogui.pixel(pos[0], pos[1])))
        return
    if end is not None:
        draw_centered_rect(mask, end, 5, (0, 0, 0))
    else:
        print("Invalid end Value!")
        return

    #print(start)
    #mask.show("Game Mask")

    path = dijkstra_sssp(mask, start, end)
    ul = bbox['left'], bbox['top']
    size = 6
    while len(path) == 0:
        draw_centered_rect(mask, start, size, (0, 0, 0))
        draw_centered_rect(mask, end, size, (0, 0, 0))
        size += 1
        print("Adjusting start area: {}".format(size))
        path = dijkstra_sssp(mask, start, end)
        if size >= 20:
            start_mask.show()
            image.apply_mask(area, start_mask, (255, 0, 255)).show()
            return

    if move_cursor:
        follow_path(path, ul, start, end, random_timing)
    else:
        draw_path(area, path, start, end)
        area.show("Solution Path")

if __name__ == "__main__":
    play(True, True, True)
