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


def generate_landing_page_from_image(image_path: str, audio_path: str | None = None):
    transcription = ""
    if audio_path:
        try:
            transcription = stt(audio_path)
        except Exception:
            transcription = ""
    mime, b64 = encode_image_b64(image_path)
    prompt = """
    You are a senior website designer and developer. Given the following image of a hand-drawn landing page, generate a complete single-file HTML for a modern, minimal, responsive landing page.

    Keep the exact layout of the original drawing in the landing page (e.g., if the designer wants an image at the bottom, keep it on the bottom). just use placeholders.
    Make sure it follows best practices for the max width of a website.

    Place the components in the website at an appropriate distance, position, and size, since hand drawn sketch might not perfectly illustrate the ideal dimensions. Use your best judgement.

    Follow the best practices for a landing page when it comes to font sizing. For example, the hero text should be large and the subheading should be smaller. But do try to retain the relative sizing and spacing, positioning as drawn.
    
    Correctly identify the buttons if they are drawn in the image.

    Images are marked as a rectangle with an large X in it. Show related images as emojis if possible.

    Let's use Inter as a default font family using this CDN definition:
    <link rel="preconnect" href="https://rsms.me/">
    <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
    All text on the website should use Inter font. Don't use bold. Use medium font weight at most.

    Use Tailwind CSS via CDN for all styling.

    You should only respond with the output code, no explanations.
    """

    prompt = str(prompt)
    prompt += f"Here is a transcription of the user's narration while describing this: {transcription}"
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
