import cv2
import numpy as np
from PIL import Image
import itertools


def save(img, name="out.png"):
    im = Image.fromarray(img)  # (img * 255).astype(np.uint8)
    im.save(name)


def capture_unskewed_photo(out="unskewed.png"):
    cam = cv2.VideoCapture(0)
    ret = False
    frame = None
    while not ret:
        ret, frame = cam.read()

    cam.release()
    dst = unskew(frame)
    save(dst, out)


def unskew(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    gray = gray / np.max(gray) * 255

    gray = (gray > 180) * 255

    gray = gray.astype(np.uint8)

    # save(gray, "gray-init.png")

    kernel = np.ones((5, 5), np.uint8)

    gray = cv2.erode(gray, kernel, iterations=5)
    gray = cv2.dilate(gray, kernel, iterations=5)

    kernel = np.ones((11, 11), np.uint8)

    gray = cv2.dilate(gray, kernel, iterations=5)
    gray = cv2.erode(gray, kernel, iterations=5)

    # gray = cv2.dilate(gray, kernel, iterations=2)
    # gray = cv2.erode(gray, kernel, iterations=2)

    # save(gray, "gray.png")

    # from https://stackoverflow.com/questions/9043805/test-if-two-lines-intersect-javascript-function
    def intersects(a, b, c, d, p, q, r, s):
        det = (c - a) * (s - q) - (r - p) * (d - b)
        if det == 0:
            return False
        else:
            lambda_ = ((s - q) * (r - a) + (p - r) * (s - b)) / det
            gamma = ((b - d) * (r - a) + (c - a) * (s - b)) / det
            return (0 < lambda_ < 1) and (0 < gamma < 1)

    # lenght of line, implemented by me
    def length(a, b, c, d):
        dy = d - b
        dx = c - a
        return np.sqrt(dy**2 + dx**2)

    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        cnt = max(contours, key=cv2.contourArea)

        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyN(cnt, 4, epsilon_percentage=epsilon, ensure_convex=True)
        corners = approx.reshape(-1, 2)

        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        for c in corners:
            cv2.circle(mask, tuple(c), 50, 120, -1)

        gray = mask

        assert len(corners) == 4

        for ordering in itertools.permutations(corners):
            # if AB intersects CD
            o = ordering
            a = o[0]
            b = o[1]
            c = o[2]
            d = o[3]
            if intersects(a[0], a[1], b[0], b[1], c[0], c[1], d[0], d[1]) and length(
                a[0], a[1], c[0], c[1]
            ) < length(b[0], b[1], c[0], c[1]):
                # probably good! corners intersect.
                corners = [a, c, b, d]
                break

        size = (int(11 * 100), int(8.5 * 100))
        pts2 = np.float32([[0, 0], [size[0], 0], [size[0], size[1]], [0, size[1]]])
        # https://math.stackexchange.com/questions/2789094/deskew-and-rotate-a-photographed-rectangular-image-aka-perspective-correction
        M, mask = cv2.findHomography(np.float32(corners), pts2)

        dst = cv2.warpPerspective(img, M, size)
        return dst


def main(inp="photo.jpg", out="unskewed.png"):
    img = np.array(Image.open(inp))
    print(img.shape)
    dst = unskew(img)
    save(dst, out)


if __name__ == "__main__":
    capture_unskewed_photo()
    # main()
