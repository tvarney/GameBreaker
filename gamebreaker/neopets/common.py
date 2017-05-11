
import gamebreaker.image as image
import os.path
import cv2


def GetGameArea(data_path : str = "./data", match_value: float = 0.70):
    im = image.ImageGrabber()

    img_ul = image.load_from_file(os.path.join(data_path, "neopets_top_left.png"), True, False)
    img_br = image.load_from_file(os.path.join(data_path, "neopets_bottom_right.png"), True, False)
    screen = im.grab_screen(im.FirstMonitor, True, False)
    match_ul = image.find_match(screen, img_ul, image.TM_CCOEFF_NORMED)
    if match_ul[0] < match_value:
        img_ul = image.load_from_file(os.path.join(data_path, "neopets_top_left_alt.png"), True, False)
        match_ul = image.find_match(screen, img_ul, image.TM_CCOEFF_NORMED)
    match_br = image.find_match(screen, img_br, image.TM_CCOEFF_NORMED)
    if match_br[0] < match_value:
        img_br = image.load_from_file(os.path.join(data_path, "neopets_bottom_right_alt.png"), True, False)
        match_br = image.find_match(screen, img_br, image.TM_CCOEFF_NORMED)

    if match_ul[0] < match_value or match_br[0] < match_value:
        print("UL_Value: {}\nBR_Value: {}".format(match_ul[0], match_br[0]))
        return None

    if match_ul[0] < 0.85:
        print("Upper left corner match is of low quality: {}".format(match_ul))
    if match_br[0] < 0.85:
        print("Bottom right corner match is of low quality: {}".format(match_br))

    top_left = match_ul[1]
    bottom_right = match_br[1]
    ul_w, ul_h, br_w, br_h = img_ul.shape[0], img_ul.shape[1], img_br.shape[0], img_br.shape[1]
    top_left = top_left[0] + ul_h, top_left[1] + ul_w
    if top_left[0] >= bottom_right[0] or top_left[1] >= bottom_right[1]:
        print("Bad coordinates: ul{} < br{}".format(top_left, bottom_right))
        w, h = img_ul.shape[1], img_ul.shape[0]
        cv2.rectangle(screen, top_left, (top_left[0] + w, top_left[1] + h), (0,0,255), 2)
        w, h = img_br.shape[1], img_br.shape[0]
        cv2.rectangle(screen, bottom_right, (bottom_right[0] + w, bottom_right[1] + h), (255, 0, 0), 2)
        cv2.imshow("Screen", screen)
        cv2.imshow("img_br", img_br)
        cv2.imshow("img_ul", img_ul)
        cv2.waitKey()
        cv2.destroyAllWindows()
        return None
    return im.make_bbox(top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])


if __name__ == "__main__":
    bbox = GetGameArea("../../data/")
    if bbox is None:
        print("Could not find game area")
    else:
        im = image.ImageGrabber()
        area = im.grab_area(bbox)
        area.show()
