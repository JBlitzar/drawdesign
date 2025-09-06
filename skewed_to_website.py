from drawing_to_website import generate_landing_page_from_image
from unskew import unskew, save
from PIL import Image
import numpy as np


def get_website_from_camera_feed_image(image_path):
    img = np.array(Image.open(image_path))
    out = unskew(img)
    save(save, "unskewed.png")
    result = generate_landing_page_from_image("unskewed.png")
    return result


if __name__ == "__main__":
    print(generate_landing_page_from_image("photo.jpg"))
