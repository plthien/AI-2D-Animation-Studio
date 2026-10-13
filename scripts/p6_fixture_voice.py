"""CI ONLY: non-speech reference tones used to test WAV alignment.

Not Kokoro TTS, not a human narration; do not distribute this audio as voice.
"""
import math
import struct
import wave
from pathlib import Path

def main(destination: Path) -> None:
    destination.mkdir(parents=True,exist_ok=True)
    for i in range(5):
        filename=destination/f"shot_{i+1:02d}.wav"
        samples=24000*2
        with wave.open(str(filename),"wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(24000)
            frequency=200+70*i
            pcm=b"".join(struct.pack("<h",int(5000*math.sin(2*math.pi*frequency*n/24000)))
                         for n in range(samples))
            f.writeframes(pcm)
        print(filename,"2 seconds synthetic signal, not spoken voice")

if __name__=="__main__":
    main(Path("outputs/p6_demo/voices"))
