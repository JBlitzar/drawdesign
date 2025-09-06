import base64
import mimetypes
import os
from dotenv import load_dotenv
from openai import OpenAI


def encode_image_b64(image_path: str):
    mime, _ = mimetypes.guess_type(image_path)
    if mime is None:
        mime = "image/jpeg"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return mime, b64


def generate_landing_page_from_image(image_path: str):
    mime, b64 = encode_image_b64(image_path)
    prompt = (
        "You are a senior web developer. Given the following image of a hand-drawn landing page, "
        "generate a complete single-file HTML for a modern, responsive landing page. "
        "Use Tailwind CSS via CDN for all styling. Only output the code, no explanations. "
        "Keep the exact layout of the original drawing in the landing page (i.e. if the designer wants an image at the bottom, keep it on the bottom) "
        "Use eye-catching, beautiful UI/UX colors throughout. If there are empty spaces or placeholders "
        "that have not been sketched in by the designer, fill them in with visually appealing, cool, and modern colors "
        "and layouts so the page looks polished and attractive overall. DO NOT ADD IN IMAGES!, just use placeholders"
    )
    client = OpenAI()
    result = client.responses.create(
        model="chatgpt-4o-latest",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": f"data:{mime};base64,{b64}"},
                ],
            }
        ],
        max_output_tokens=2000,
        temperature=0.2,
    )
    return result.output_text


if __name__ == "__main__":
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    if not key:
        raise ValueError("Missing OPENAI_API_KEY (or OPENAI_KEY) in environment.")
    os.environ["OPENAI_API_KEY"] = key
    image_path = "test.jpeg"
    html = generate_landing_page_from_image(image_path)
    out_path = "generated_landing_page.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Landing page code generated and saved to {out_path}")
