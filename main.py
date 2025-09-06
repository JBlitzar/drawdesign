from flask import Flask, jsonify, request, send_from_directory
import base64
from skewed_to_website import get_website_from_camera_feed_image

app = Flask(__name__)


@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/snapshot", methods=["POST"])
def image_snapshot():
    img_b64 = request.json["image_data"].split(",")[1]
    imgdata = base64.b64decode(img_b64)
    with open("photo.jpg", "wb") as f:
        f.write(imgdata)

    print(get_website_from_camera_feed_image("photo.jpg"))


if __name__ == "__main__":
    app.run(debug=True)
