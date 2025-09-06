# convert speech to text

from openai import OpenAI


def stt(inp_file: str) -> str:
    client = OpenAI()

    audio_file = open(inp_file, "rb")

    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe", file=audio_file
    )

    audio_file.close()

    print(transcription.text)
    return transcription.text
