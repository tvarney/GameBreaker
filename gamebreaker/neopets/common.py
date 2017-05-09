
import gamebreaker.image as image


def GetGameArea():
    im = image.ImageGrabber()

    img_ul = image.load_from_file("./data/neopets_top_left.png", True)
    img_br = image.load_from_file("./data/neopets_bottom_right.png", True)
    screen = im.grab_screen(im.AllMonitors, True)
    match_ul = image.find_match(screen, img_ul, image.TM_CCOEFF_NORMED)
    match_br = image.find_match(screen, img_br, image.TM_CCOEFF_NORMED)

    if match_ul[0] < 0.95 or match_br[0] < 0.95:
        return None

    top_left = match_ul[1]
    bottom_right = match_br[1]
    ul_w, ul_h, br_w, br_h = img_ul.shape[0], img_ul.shape[1], img_br.shape[0], img_br.shape[1]
    top_left = top_left[0] + ul_h, top_left[1] +  ul_w

    bbox = im.make_bbox(top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])
    return bbox
