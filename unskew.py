import cv2
import numpy as np
from PIL import Image


def save(img, name="out.png"):
    im = Image.fromarray(img)  # (img * 255).astype(np.uint8)
    im.save(name)


def capture_unskewed_photo(out="unskewed.png"):
    cam = cv2.VideoCapture(0)
    ret = False
    frame = None
    for _ in range(5):
        ret, frame = cam.read()
    while not ret:
        ret, frame = cam.read()

    cam.release()
    dst = unskew(frame)
    save(dst, out)
    save(frame, "img.jpg")


def unskew_video():
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        dst = unskew(frame)
        cv2.imshow("Unskewed", dst)
        cv2.imshow("Original", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


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
    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    def order_points(pts_: np.ndarray) -> np.ndarray:
        ys = pts_[:, 1]
        top_idxs = ys.argsort()[:2]
        bot_idxs = ys.argsort()[-2:]
        top = pts_[top_idxs]
        bot = pts_[bot_idxs]
        top = top[np.argsort(top[:, 0])]
        bot = bot[np.argsort(bot[:, 0])]
        tl, tr = top[0], top[1]
        bl, br = bot[0], bot[1]
        return np.array([tl, tr, br, bl], dtype=np.float32)

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

        corners = order_points(corners)

        size = (int(11 * 100), int(8.5 * 100))
        pts2 = np.float32([[0, 0], [size[0], 0], [size[0], size[1]], [0, size[1]]])
        # https://math.stackexchange.com/questions/2789094/deskew-and-rotate-a-photographed-rectangular-image-aka-perspective-correction
        M, mask = cv2.findHomography(np.float32(corners), pts2)

        dst = cv2.warpPerspective(img, M, size)

        dst = cv2.flip(dst, 0)

        return dst

    return img


def main(inp="photo.jpg", out="unskewed.png"):
    img = np.array(Image.open(inp))
    print(img.shape)
    dst = unskew(img)
    save(dst, out)


if __name__ == "__main__":
    unskew_video()
