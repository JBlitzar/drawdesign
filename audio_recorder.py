import threading
import wave
from typing import Optional

import pyaudio


class AudioRecorder:
    def __init__(self, filename: str = "temp_audio.wav", rate: int = 44100, channels: int = 1):
        self.audio_filename = filename
        self.rate = rate
        self.channels = channels
        self.frames_per_buffer = 1024
        self.format = pyaudio.paInt16

        self._pa: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._frames: list[bytes] = []

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        try:
            self._pa = pyaudio.PyAudio()
            self._stream = self._pa.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.frames_per_buffer,
            )
            self._stop.clear()
            self._frames = []
            self._thread = threading.Thread(target=self._record, daemon=True)
            self._thread.start()
        except Exception:
            # Fail silently; caller can proceed without audio
            self._cleanup_streams()

    def _record(self):
        if not self._stream:
            return
        try:
            self._stream.start_stream()
        except Exception:
            return
        while not self._stop.is_set():
            try:
                data = self._stream.read(self.frames_per_buffer, exception_on_overflow=False)
                self._frames.append(data)
            except Exception:
                # Drop frame on read errors (overflows, device hiccups)
                continue

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
        self._write_wav()
        self._cleanup_streams()

    def _write_wav(self):
        try:
            with wave.open(self.audio_filename, "wb") as wf:
                wf.setnchannels(self.channels)
                sampwidth = self._pa.get_sample_size(self.format) if self._pa else 2
                wf.setsampwidth(sampwidth)
                wf.setframerate(self.rate)
                if self._frames:
                    wf.writeframes(b"".join(self._frames))
                else:
                    # Write an empty file with correct header
                    wf.writeframes(b"")
        except Exception:
            pass

    def _cleanup_streams(self):
        try:
            if self._stream:
                if self._stream.is_active():
                    try:
                        self._stream.stop_stream()
                    except Exception:
                        pass
                try:
                    self._stream.close()
                except Exception:
                    pass
        finally:
            self._stream = None
            if self._pa:
                try:
                    self._pa.terminate()
                except Exception:
                    pass
                self._pa = None
