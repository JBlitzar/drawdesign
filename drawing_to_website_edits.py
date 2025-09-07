def encode_file_b64(file_path: str):
    mime = "text/html"
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return mime, b64


import base64
import mimetypes
import os
from dotenv import load_dotenv
from openai import OpenAI
from stt import stt


def encode_image_b64(image_path: str):
    mime, _ = mimetypes.guess_type(image_path)
    if mime is None:
        mime = "image/jpeg"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return mime, b64


def update_landing_page_with_edits(
    new_image_path: str, old_image_path: str, html_path: str, audio_path: str
):
    new_mime, b64_new = encode_image_b64(new_image_path)
    old_mime, b64_old = encode_image_b64(old_image_path)
    print("encoded")

    transcription = stt(audio_path)
    print("transcribed")

    html_content = ""
    with open(html_path, "r") as f:
        html_content = f.read()

    prompt = (
        "You are a senior web developer. Given the following two images: the first is a hand-drawn landing page with edits (edits are in a different color), "
        "and the second is the original version without edits (just in black). You are also given the current HTML code for the landing page. "
        "Your task is to notice the changes/edits between the new and old images, and update the HTML so that the landing page reflects the new edits. "
        "Do NOT showcase the edits in a different color or format. Naturally interweave it into the landing page."
        "Use Tailwind CSS via CDN for all styling. Only output the updated HTML code, no explanations. Don't say that you're unable to directly compare images. You will be given images, and you are an AI model with vision capabilities"
    )
    prompt = str(prompt)
    prompt += f"The previous HTML content follows: {html_content}. "

    prompt = str(prompt)
    prompt += f"Here is a transcription of the user's narration while describing this: {transcription}"
    print("edit prompt,", prompt)

    client = OpenAI()
    result = client.responses.create(
        model="chatgpt-4o-latest",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{new_mime};base64,{b64_new}",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{old_mime};base64,{b64_old}",
                    },
                ],
            }
        ],
        max_output_tokens=3000,
        temperature=0.2,
    )
    print("result:", result.output_text)
    return result.output_text


if __name__ == "__main__":
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    if not key:
        raise ValueError("Missing OPENAI_API_KEY (or OPENAI_KEY) in environment.")
    os.environ["OPENAI_API_KEY"] = key
    new_image_path = "image.jpg"  # new image with edits
    old_image_path = "prev_image.jpg"  # old image without edits
    html_path = "out.html"  # existing html file
    html = update_landing_page_with_edits(new_image_path, old_image_path, html_path)
    print(html)
