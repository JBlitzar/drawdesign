import os
import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv

from audio_recorder import AudioRecorder
from unskew import unskew, save
from drawing_to_website import generate_landing_page_from_image
from drawing_to_website_edits import update_landing_page_with_edits


def ensure_api_key():
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    if not key:
        raise ValueError("Missing OPENAI_API_KEY (or OPENAI_KEY) in environment.")
    os.environ["OPENAI_API_KEY"] = key


def preview_and_capture(audio: bool = True) -> str:
    rec = AudioRecorder() if audio else None
    if rec:
        rec.start()

    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Unskewed")
    cv2.namedWindow("Camera")
    dst = None

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                continue
            dst = unskew(frame)
            try:
                cv2.imshow("Unskewed", dst)
                cv2.imshow("Camera", frame)
            except cv2.error:
                pass
            if cv2.waitKey(1) == ord("q"):
                break
    finally:
        if rec:
            rec.stop()
        cam.release()
        cv2.destroyAllWindows()

    if dst is None:
        raise RuntimeError("No frame captured from camera")

    save(np.asarray(dst), "image.jpg")
    return "temp_audio.wav" if audio else None


def generate_or_update(audio_path: str | None):
    # if out.html exists and prev image exists, update; else generate
    if os.path.exists("out.html") and os.path.exists("image.jpg") and os.path.exists("prev_image.jpg"):
        html = update_landing_page_with_edits("image.jpg", "prev_image.jpg", "out.html", audio_path)
    else:
        html = generate_landing_page_from_image("image.jpg", audio_path)
    html = html.replace("```html", "").replace("```", "")
    with open("out.html", "w", encoding="utf-8") as f:
        f.write(html)
    try:
        os.system("open out.html")
    except Exception:
        pass


def main():
    ensure_api_key()
    # Initial capture and generation
    audio_path = preview_and_capture(audio=True)
    if os.path.exists("image.jpg"):
        # keep previous copy for subsequent edits
        save(np.asarray(Image.open("image.jpg")), "prev_image.jpg")
    generate_or_update(audio_path)

    # Loop for iterative edits
    while True:
        audio_path = preview_and_capture(audio=True)
        if os.path.exists("image.jpg"):
            last = np.asarray(Image.open("image.jpg"))
            save(last, "prev_image.jpg")
        generate_or_update(audio_path)


if __name__ == "__main__":
    main()
