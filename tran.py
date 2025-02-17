import os
import subprocess
import whisper

def transcribe_to_vtt(file_path):
    """
    Transcribes an MP3 or M4A audio file to a WebVTT file.
    """
    base, ext = os.path.splitext(file_path)
    # Convert m4a to wav if needed (mp3 is supported directly)
    if ext.lower() == ".m4a":
        temp_wav = base + ".wav"
        subprocess.run(
            ["ffmpeg", "-y", "-i", file_path, "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", temp_wav],
            check=True
        )
        file_path = temp_wav

    model = whisper.load_model("large-v3")
    result = model.transcribe(file_path, fp16=False)
    text = result.get("text", "").strip()

    # Create simple VTT output. Here we create one cue spanning 10 seconds.
    # For production, cue timings should be generated per sentence or word.
    vtt_content = "WEBVTT\n\n00:00:00.000 --> 00:00:10.000\n" + text

    out_file = base + ".vtt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(vtt_content)
    
    return out_file

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tran.py <audio_file_path>")
        sys.exit(1)
    input_path = sys.argv[1]
    vtt_file = transcribe_to_vtt(input_path)
    print(f"VTT file created: {vtt_file}")
