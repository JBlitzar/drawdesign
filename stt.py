from openai import OpenAI


def stt(inp_file: str) -> str:
    client = OpenAI()
    with open(inp_file, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe", file=audio_file
        )
    return getattr(transcription, "text", "")
