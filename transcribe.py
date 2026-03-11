import whisper
import sys
import os

def transcribe_video(video_path, model_name="turbo", language=None):
    if not os.path.exists(video_path):
        print(f"Error: File '{video_path}' not found")
        sys.exit(1)

    print(f"Loading model: {model_name}...")
    model = whisper.load_model(model_name)

    print(f"Transcribing: {video_path}")
    result = model.transcribe(video_path, language=language)

    output_path = os.path.splitext(video_path)[0] + "_transcript.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"Transcript saved to: {output_path}")
    print(f"\nTranscript:\n{result['text']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <video_file> [model] [language]")
        print("Models: tiny, base, small, medium, large, turbo (default)")
        print("Languages: en, de, es, fr, etc. (auto-detect if not specified)")
        sys.exit(1)

    video_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "turbo"
    language = sys.argv[3] if len(sys.argv) > 3 else None

    transcribe_video(video_path, model_name, language)
