import os
from dotenv import load_dotenv
from openai import OpenAI
import whisper
from datetime import datetime
import re
from pathlib import Path


html_file_path = "generated_landing_page.html"

def transcribe_audio(audio_path: str) -> str:
    model = whisper.load_model("turbo")
    result = model.transcribe(audio_path)
    return result["text"]

def _strip_code_fence(text: str) -> str:
    """
    If the model wraps HTML in ```html ... ``` or ``` ... ```, strip the fences.
    """
    fenced = re.match(r"^```(?:html)?\s*(.*)```$", text.strip(), flags=re.DOTALL | re.IGNORECASE)
    return fenced.group(1).strip() if fenced else text

def make_edits_html(feedback_text: str, html_file_path: str, client: OpenAI, model: str = "gpt-4o") -> str:
 
    p = Path(html_file_path)
    if not p.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file_path}")

    original_html = p.read_text(encoding="utf-8")

    system_prompt = (
        "You are a senior frontend engineer. You will receive:\n"
        "1) FEEDBACK: textual feedback transcribed from audio\n"
        "2) HTML: the current full HTML file\n\n"
        "Apply ONLY the concrete, relevant edits requested in the FEEDBACK.\n"
        "Constraints:\n"
        "- Preserve head/meta, existing assets, classes, and IDs unless changes are explicitly required to satisfy FEEDBACK.\n"
        "- Do not invent external assets or libraries unless FEEDBACK asks for them.\n"
        "- Return ONLY a complete, valid HTML document (no explanations, no markdown fences).\n"
        "- Keep scripts/styles intact unless FEEDBACK requires modifications.\n"
        "- If FEEDBACK is ambiguous, prefer minimal, safe improvements that obviously satisfy it."
    )

    user_payload = (
        "<FEEDBACK>\n"
        f"{feedback_text.strip()}\n"
        "</FEEDBACK>\n\n"
        "<HTML>\n"
        f"{original_html}\n"
        "</HTML>"
    )

    # Call the Responses API with system + user content
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": user_payload}]},
        ],
        max_output_tokens=8192,
        temperature=0.2,
    )

    edited_html = resp.output_text
    edited_html = _strip_code_fence(edited_html).strip()

    if not edited_html.lower().startswith("<!doctype") and "<html" not in edited_html.lower():
        raise ValueError("Model response does not look like a full HTML document.")

    # Backup original, then write the new file
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = f"{html_file_path}.bak.{ts}"
    p.rename(backup_path)
    Path(html_file_path).write_text(edited_html, encoding="utf-8")

    return edited_html

if __name__ == "__main__":
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    if not key:
        raise ValueError("Missing OPENAI_API_KEY (or OPENAI_KEY) in environment.")
    client = OpenAI(api_key=key)

    # 1) transcribe your audio to feedback text
    audio_path = "audio.mp3"
    feedback = transcribe_audio(audio_path)

    # 2) apply edits to your HTML file
    updated_html = make_edits_html(feedback, html_file_path, client, model="gpt-4o")
    print("HTML updated successfully.")
