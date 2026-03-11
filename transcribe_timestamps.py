import whisper
import sys
import os

def transcribe_with_timestamps(video_path, model_name="turbo", language="de"):
    if not os.path.exists(video_path):
        print(f"Error: File '{video_path}' not found")
        sys.exit(1)

    print(f"Loading model: {model_name}...")
    model = whisper.load_model(model_name)

    print(f"Transcribing: {video_path}")
    result = model.transcribe(video_path, language=language)

    output_path = os.path.splitext(video_path)[0] + "_transcript_timestamps.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            f.write(f"[{start:.1f}s - {end:.1f}s] {text}\n")

    print(f"Transcript with timestamps saved to: {output_path}")
    print("\nPreview:")
    for segment in result["segments"][:15]:
        start = segment["start"]
        text = segment["text"]
        print(f"[{start:.1f}s] {text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_timestamps.py <video_file> [model] [language]")
        sys.exit(1)

    video_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "turbo"
    language = sys.argv[3] if len(sys.argv) > 3 else "de"

    transcribe_with_timestamps(video_path, model_name, language)
