import whisper
import sys
import os

def transcribe_vtt(video_path, model_name="turbo", language="de"):
    if not os.path.exists(video_path):
        print(f"Error: File '{video_path}' not found")
        sys.exit(1)

    print(f"Loading model: {model_name}...")
    model = whisper.load_model(model_name)

    print(f"Transcribing: {video_path}")
    result = model.transcribe(video_path, language=language)

    output_path = os.path.splitext(video_path)[0] + ".vtt"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for segment in result["segments"]:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            f.write(f"{format_time(start)} --> {format_time(end)}\n{text}\n\n")

    print(f"VTT with timestamps saved to: {output_path}")

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_vtt.py <video_file> [model] [language]")
        sys.exit(1)

    video_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "turbo"
    language = sys.argv[3] if len(sys.argv) > 3 else "de"

    transcribe_vtt(video_path, model_name, language)
