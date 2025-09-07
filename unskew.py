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


def unskew(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img

    cnt = max(contours, key=cv2.contourArea)

    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    if len(approx) < 4:
        hull = cv2.convexHull(cnt)
        approx = cv2.approxPolyDP(hull, 0.02 * cv2.arcLength(hull, True), True)
    if len(approx) != 4:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        approx = np.int0(box)

    pts = approx.reshape(-1, 2).astype(np.float32)

    # Order corners: tl, tr, br, bl
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).reshape(-1)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]
    ordered = np.array([tl, tr, br, bl], dtype=np.float32)

    # Compute target size preserving orientation (portrait or landscape)
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxWidth = int(max(widthA, widthB))
    maxHeight = int(max(heightA, heightB))
    maxWidth = max(100, maxWidth)
    maxHeight = max(100, maxHeight)

    dst_pts = np.array(
        [[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]],
        dtype=np.float32,
    )
    M = cv2.getPerspectiveTransform(ordered, dst_pts)
    dst = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    # Ensure upright orientation: if upside down (more dark pixels in top vs bottom), flip
    # Simple heuristic to avoid upside-down or mirror effects
    top = dst[: maxHeight // 3, :, :]
    bottom = dst[-maxHeight // 3 :, :, :]
    if top.mean() < bottom.mean():
        dst = cv2.rotate(dst, cv2.ROTATE_180)

    return dst


def main(inp="photo.jpg", out="unskewed.png"):
    img = np.array(Image.open(inp))
    print(img.shape)
    dst = unskew(img)
    save(dst, out)
    
