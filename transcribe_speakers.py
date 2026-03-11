import whisperx
import sys
import os

def transcribe_with_speakers(video_path, model_name="turbo", language="de"):
    if not os.path.exists(video_path):
        print(f"Error: File '{video_path}' not found")
        sys.exit(1)

    print(f"Loading WhisperX model: {model_name}...")
    model = whisperx.load_model(model_name, device="cpu")

    print(f"Transcribing: {video_path}")
    audio = whisperx.load_audio(video_path)
    result = model.transcribe(audio, language=language)

    print("Performing speaker diarization...")
    try:
        diarize_model = whisperx.DiarizationPipeline(use_auth_token=None)
        diarize_result = diarize_model(audio)
        
        result = whisperx.assign_word_speakers(diarize_result, result)
    except Exception as e:
        print(f"Diarization failed: {e}")
        print("Saving transcript without speaker labels...")
        output_path = os.path.splitext(video_path)[0] + "_transcript.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            for segment in result["segments"]:
                f.write(segment["text"] + "\n")
        print(f"Transcript saved to: {output_path}")
        return

    output_path = os.path.splitext(video_path)[0] + "_transcript_speakers.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            start = segment["start"]
            end = segment["end"]
            speaker = segment.get("speaker", "UNKNOWN")
            text = segment["text"]
            f.write(f"[{start:.1f}s - {end:.1f}s] {speaker}: {text}\n")

    print(f"Transcript with speakers saved to: {output_path}")
    print("\nPreview:")
    for segment in result["segments"][:10]:
        start = segment["start"]
        speaker = segment.get("speaker", "UNKNOWN")
        text = segment["text"]
        print(f"[{start:.1f}s] {speaker}: {text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_speakers.py <video_file> [model] [language]")
        sys.exit(1)

    video_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "turbo"
    language = sys.argv[3] if len(sys.argv) > 3 else "de"

    transcribe_with_speakers(video_path, model_name, language)
