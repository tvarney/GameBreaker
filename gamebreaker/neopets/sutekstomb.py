
import pyautogui
from PIL import Image, ImageDraw
import gamebreaker.color as Color
import gamebreaker.image as img
import os.path
import time
import win32gui, win32con


class Tile(object):
    AllTiles = []

    @staticmethod
    def GetTileId(pixel):
        for id, tile in enumerate(Tile.AllTiles):
            if tile.matches(pixel):
                return id
            if pixel in _backgrounds:
                return -2
        return -1

    def __init__(self, name, color):
        self._name = name
        self._color = color
        self._id = len(Tile.AllTiles)
        Tile.AllTiles.append(self)

    def matches(self, pixel):
        return self._color == pixel

    def id(self):
        return self._id

    def color(self):
        return self._color

    def __str__(self):
        return self._name


Tile.Head = Tile("Head", (106, 130, 240))
Tile.Scarab = Tile("Scarab", (0, 51, 0))
Tile.Tree = Tile("Tree", (102, 153, 0))
Tile.Gem = Tile("Gem", (245, 10, 81))
Tile.Obelisk = Tile("Obelisk", (241, 241, 82))
Tile.Sun = Tile("Sun", (255, 102, 0))
Tile.Pyramid = Tile("Pyramid", (255, 153, 0))
Tile.Bomb = Tile("Bomb", (255, 0, 0))
Tile.Amulet = Tile("Amulet", (105, 1, 1))
Tile.Special = Tile("Special", (0, 0, 0))
Tile.Ankh = Tile("Ankh", (102, 102, 102))

_backgrounds = [(202, 150, 98), (220, 183, 146)]
_time_up_text = (255, 255, 49)
_no_moves_bg = (41, 30, 19)


class Move(object):
    def __init__(self, old_pos, new_pos):
        self.old_pos = old_pos
        self.new_pos = new_pos

    def commit(self, ul, grid_space, click_delay = 0.03):
        if self.old_pos == self.new_pos:
            return True

        pos = ul[0] + 20 + self.old_pos[0] * grid_space, ul[1] + 20 + self.old_pos[1] * grid_space
        #win32gui.SetCursor(pos)
        pyautogui.moveTo(pos[0], pos[1])
        pyautogui.click()
        time.sleep(click_delay)

        pos = ul[0] + 20 + self.new_pos[0] * grid_space, ul[1] + 20 + self.new_pos[1] * grid_space
        pyautogui.moveTo(pos[0], pos[1])
        #win32gui.SetCursor(pos)
        pyautogui.click()


class Suteks(object):
    def __init__(self):
        self.sshot = img.ImageGrabber()
        self.data_path = "./data/"
        self.running = False
        self._last_screen = None
        self._final_screen = None

    def _find_area(self):
        img_id = img.load_from_file(os.path.join(self.data_path, "suteks_id.png"), True, False)
        screen = self.sshot.grab_screen(0, True)
        mval, ul = img.find_match(screen, img_id, img.TM_CCOEFF_NORMED)
        if mval <= 0.85:
            return None
        return ul[0] + img_id.shape[0], ul[1] + img_id.shape[1]

    def fill_grid(self, bbox, grid, ul):
        breakout = True
        while breakout:
            area = self.sshot.grab_area(bbox)
            self._last_screen = area

            if area.getpixel((139, 145)) == _time_up_text:
                print("Game Over!")
                self.running = False
                return False
            if area.getpixel((10,10)) == (226, 199, 171):
                #area.show()
                pos = pyautogui.position()
                time.sleep(1.0)
                if pos != pyautogui.position():
                    exit(1) # TODO: Change this so we don't kill the process!
                pyautogui.moveTo(ul[0] + 140, ul[1] + 260)
                pyautogui.click()
                continue

            breakout = False
            for y in range(10):
                for x in range(10):
                    pixel = area.getpixel((20 + x * 40, 20 + y * 40))
                    t_id = Tile.GetTileId(pixel)
                    if t_id == -1:
                        print("Found unknown tile at {}x{}: Color = {}".format(x, y, pixel))
                    if t_id == -2:
                        breakout = True
                        break
                    grid[y][x] = t_id
                if breakout:
                    break
        return True

    def play(self, stime=0.3):
        ul = self._find_area()
        bbox = img.ImageGrabber.make_bbox(ul[0], ul[1], 400, 400)
        print("Found Game at {}x{}".format(bbox['left'], bbox['top']))
        grid = [[-1 for i in range(10)] for j in range(10)]

        pyautogui.moveTo(10,10)
        pos = pyautogui.position()

        self.running = True
        while self.running:
            if pyautogui.position() != pos:
                print("Mouse moved! Quitting...")
                return

            if not self.fill_grid(bbox, grid, ul):
                self.running = False
                break

            move = find_move(grid)

            pos = pyautogui.position()
            time.sleep(stime)
            if pos != pyautogui.position():
                exit(1) #TODO: Change this so we aren't killing the process!

            if move is not None:
                move.commit(ul, 40)
                pos = pyautogui.position()
            else:
                #print("Could not find move!")
                #generate_grid_image(grid).show("Current Grid")
                self._final_screen = self._last_screen

            time.sleep(0.4)


def generate_grid_image(grid):
    img = Image.new('RGB', (400,400), Color.White)
    context = ImageDraw.Draw(img)
    for y in range(10):
        for x in range(10):
            tile_id = grid[y][x]
            t_color = Color.White
            if tile_id >= 0:
                t_color = Tile.AllTiles[tile_id].color()
            elif tile_id == -1:
                t_color = Color.Gray50
            context.rectangle((x*40, y*40, x*40+40, y*40+40), t_color, t_color)
    return img


def find_move(grid):
    move = None
    value = 0
    for y in range(10):
        for x in range(10):
            if grid[y][x] < 0:
                continue
            if x >= 1:
                nvalue = _test_move_left(x, y, grid)
                if nvalue > value:
                    move = Move((x, y), (x - 1, y))
                    value = nvalue
            if x <= 8:
                nvalue = _test_move_right(x, y, grid)
                if nvalue > value:
                    move = Move((x, y), (x + 1, y))
                    value = nvalue
            if y >= 1:
                nvalue = _test_move_up(x, y, grid)
                if nvalue > value:
                    move = Move((x, y), (x, y - 1))
                    value = nvalue
            if y <= 8:
                nvalue = _test_move_down(x, y, grid)
                if nvalue > value:
                    move = Move((x, y), (x, y + 1))
                    value = nvalue
            # Stop as soon as we find the best move possible rating 4
            if value == 4:
                return move
    return move


def _test_move_up(x, y, grid) -> int:
    matches = [grid[y][x], Tile.Amulet.id()]
    xm2 = False if x < 2 else grid[y-1][x-2] in matches
    xm1 = False if x < 1 else grid[y-1][x-1] in matches
    xp1 = False if x > 8 else grid[y-1][x+1] in matches
    xp2 = False if x > 7 else grid[y-1][x+2] in matches

    ym3 = False if y < 3 else grid[y-3][x] in matches
    ym2 = False if y < 2 else grid[y-2][x] in matches

    r = 0
    if xm2 and xm1:
        r += 1
    if xp1 and xp2:
        r += 1
    if xp1 and xm1:
        r += 1
    if ym3 and ym2:
        r += 1
    return r


def _test_move_down(x, y, grid) -> int:
    matches = [grid[y][x], Tile.Amulet.id()]
    xm2 = False if x < 2 else grid[y + 1][x - 2] in matches
    xm1 = False if x < 1 else grid[y + 1][x - 1] in matches
    xp1 = False if x > 8 else grid[y + 1][x + 1] in matches
    xp2 = False if x > 7 else grid[y + 1][x + 2] in matches

    yp3 = False if y > 6 else grid[y + 3][x] in matches
    yp2 = False if y > 7 else grid[y + 2][x] in matches

    r = 0
    if xm2 and xm1:
        r += 1
    if xp1 and xp2:
        r += 1
    if xp1 and xm1:
        r += 1
    if yp3 and yp2:
        r += 1
    return r


def _test_move_left(x, y, grid) -> int:
    matches = [grid[y][x], Tile.Amulet.id()]
    ym2 = False if y < 2 else grid[y - 2][x - 1] in matches
    ym1 = False if y < 1 else grid[y - 1][x - 1] in matches
    yp1 = False if y > 8 else grid[y + 1][x - 1] in matches
    yp2 = False if y > 7 else grid[y + 2][x - 1] in matches

    xm3 = False if x < 3 else grid[y][x - 3] in matches
    xm2 = False if x < 2 else grid[y][x - 2] in matches

    r = 0
    if ym2 and ym1:
        r += 1
    if yp2 and yp1:
        r += 1
    if yp1 and ym1:
        r += 1
    if xm3 and xm2:
        r += 1
    return r


def _test_move_right(x, y, grid) -> int:
    matches = [grid[y][x], Tile.Amulet.id()]

    ym2 = False if y < 2 else grid[y - 2][x + 1] in matches
    ym1 = False if y < 1 else grid[y - 1][x + 1] in matches
    yp1 = False if y > 8 else grid[y + 1][x + 1] in matches
    yp2 = False if y > 7 else grid[y + 2][x + 1] in matches

    xp3 = False if x > 6 else grid[y][x + 3] in matches
    xp2 = False if x > 7 else grid[y][x + 2] in matches

    r = 0
    if ym2 and ym1:
        r += 1
    if yp1 and yp2:
        r += 2
    if yp1 and ym1:
        r += 1
    if xp3 and xp2:
        r += 1

    return r

if __name__ == "__main__":
    s = Suteks()
    s.data_path = "../../data/"
    s.play()