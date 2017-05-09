
from gamebreaker import image
import pyautogui
import gamebreaker.neopets.common as np


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


def run():
    im = image.ImageGrabber()
    bbox = np.GetGameArea()
    if bbox is None:
        print("Could not locate neopets game area")
        return

    area = im.grab_area(bbox, False)
    for y in range(1):
        for x in range(1):
            pixel = area.getpixel((x,y))
            print(pixel)


    area.show("Game Area")



if __name__=="__main__":
    run()