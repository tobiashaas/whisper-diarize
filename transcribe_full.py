"""
Whisper TTS - Full Transcription with Speaker Diarization
==========================================================
Outputs:
  - *_transcript.txt   : Lesbares Transkript mit Sprecher + Timestamps
  - *_speakers.srt     : SRT-Datei fuer Adobe Premiere (Captions Import)
  - *_markers.csv      : Adobe Premiere Sequence Markers (Import via Markers Panel)

Voraussetzungen:
  - HuggingFace Token mit Zugriff auf pyannote-Modelle
  - Token als Umgebungsvariable HF_TOKEN setzen ODER --hf-token Argument nutzen
  - Modell-Zugriff beantragen auf:
      https://huggingface.co/pyannote/speaker-diarization-3.1
      https://huggingface.co/pyannote/segmentation-3.0

Verwendung:
  python transcribe_full.py <datei> [optionen]

  python transcribe_full.py interview.mp4
  python transcribe_full.py interview.mp4 --language de --speakers 2
  python transcribe_full.py interview.mp4 --hf-token hf_xxxx --model large-v2
"""

import sys
import os
import argparse
import datetime
import warnings
import logging

# Drittbibliothek-Warnungen unterdrücken
warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")
warnings.filterwarnings("ignore", message=".*torchcodec.*")
warnings.filterwarnings("ignore", message=".*TensorFloat-32.*")
warnings.filterwarnings("ignore", message=".*Lightning automatically upgraded.*")
warnings.filterwarnings("ignore", message=".*upgrade_checkpoint.*")

# Logging von whisperx/pyannote auf WARNING reduzieren
logging.getLogger("whisperx").setLevel(logging.WARNING)
logging.getLogger("pyannote").setLevel(logging.WARNING)
logging.getLogger("lightning").setLevel(logging.WARNING)
logging.getLogger("pytorch_lightning").setLevel(logging.WARNING)

def format_srt_time(seconds: float) -> str:
    """Formatiert Sekunden als SRT-Timestamp HH:MM:SS,mmm"""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    millis = int((seconds % 1) * 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def format_readable_time(seconds: float) -> str:
    """Formatiert Sekunden als MM:SS.s"""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"

def seconds_to_premiere_frames(seconds: float, fps: float = 25.0) -> str:
    """Konvertiert Sekunden zu Premiere-kompatibler Timecode HH:MM:SS:FF"""
    total_frames = int(seconds * fps)
    ff = total_frames % int(fps)
    total_secs = total_frames // int(fps)
    hh = total_secs // 3600
    mm = (total_secs % 3600) // 60
    ss = total_secs % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

def save_txt(segments, output_path: str):
    """Speichert lesbares Transkript mit Sprecher + Timestamps"""
    with open(output_path, "w", encoding="utf-8") as f:
        current_speaker = None
        for seg in segments:
            speaker = seg.get("speaker", "UNKNOWN")
            start = seg["start"]
            end = seg["end"]
            text = seg["text"].strip()

            if speaker != current_speaker:
                if current_speaker is not None:
                    f.write("\n")
                f.write(f"\n[{speaker}]\n")
                current_speaker = speaker

            f.write(f"  [{format_readable_time(start)} - {format_readable_time(end)}] {text}\n")

def save_srt(segments, output_path: str):
    """Speichert SRT-Datei mit Speaker-Labels fuer Adobe Premiere"""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            speaker = seg.get("speaker", "UNKNOWN")
            start = format_srt_time(seg["start"])
            end = format_srt_time(seg["end"])
            text = seg["text"].strip()

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"[{speaker}] {text}\n\n")

def save_premiere_markers_csv(segments, output_path: str, fps: float = 25.0):
    """
    Speichert Adobe Premiere Sequence Markers als CSV.
    Import: Premiere > Markers Panel > Import Markers (Hamburger-Menu)
    """
    with open(output_path, "w", encoding="utf-8") as f:
        # Premiere Markers CSV Header
        f.write("Name\tDescription\tIn\tOut\tDuration\tMarker Type\n")

        current_speaker = None
        block_start = None
        block_texts = []

        for seg in segments:
            speaker = seg.get("speaker", "UNKNOWN")
            text = seg["text"].strip()

            if speaker != current_speaker:
                # Vorherigen Block schreiben
                if current_speaker is not None and block_texts:
                    in_tc = seconds_to_premiere_frames(block_start, fps)
                    out_tc = seconds_to_premiere_frames(seg["start"], fps)
                    dur_tc = seconds_to_premiere_frames(seg["start"] - block_start, fps)
                    desc = " ".join(block_texts)[:200]  # Premiere-Limit
                    f.write(f"{current_speaker}\t{desc}\t{in_tc}\t{out_tc}\t{dur_tc}\tComment\n")

                current_speaker = speaker
                block_start = seg["start"]
                block_texts = [text]
            else:
                block_texts.append(text)

        # Letzten Block schreiben
        if current_speaker and block_texts:
            last_end = segments[-1]["end"]
            in_tc = seconds_to_premiere_frames(block_start, fps)
            out_tc = seconds_to_premiere_frames(last_end, fps)
            dur_tc = seconds_to_premiere_frames(last_end - block_start, fps)
            desc = " ".join(block_texts)[:200]
            f.write(f"{current_speaker}\t{desc}\t{in_tc}\t{out_tc}\t{dur_tc}\tComment\n")

def transcribe_full(
    file_path: str,
    model_name: str = "turbo",
    language: str = "de",
    hf_token: str = None,
    diarize_model_name: str = "pyannote/speaker-diarization-3.1",
    num_speakers: int = None,
    min_speakers: int = None,
    max_speakers: int = None,
    fps: float = 25.0,
    device: str = "cpu",
):
    import whisperx
    import torch
    # Lightning-Checkpoint-Upgrade-Meldung unterdrücken
    logging.getLogger("lightning.pytorch.utilities.upgrade_checkpoint").setLevel(logging.ERROR)
    logging.getLogger("lightning_fabric").setLevel(logging.WARNING)

    if not os.path.exists(file_path):
        print(f"FEHLER: Datei '{file_path}' nicht gefunden.")
        sys.exit(1)

    # Auto-fallback auf CPU falls CUDA nicht verfuegbar
    if device == "cuda" and not torch.cuda.is_available():
        print("WARNUNG: CUDA nicht verfuegbar, verwende CPU.")
        device = "cpu"

    if device == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 1)
        print(f"GPU: {gpu_name} ({vram_gb} GB VRAM)")
        compute_type = "float16"
        batch_size = 16
    else:
        compute_type = "int8"
        batch_size = 4

    base_path = os.path.splitext(file_path)[0]

    # --- 1. Transkription ---
    print(f"\n[1/3] Lade WhisperX-Modell: {model_name} (device={device}, compute={compute_type})...")
    model = whisperx.load_model(model_name, device=device, compute_type=compute_type)

    print(f"[1/3] Transkribiere: {file_path}")
    audio = whisperx.load_audio(file_path)
    result = model.transcribe(audio, language=language, batch_size=batch_size)
    print(f"      -> {len(result['segments'])} Segmente gefunden")

    # --- 2. Wort-Alignment ---
    print(f"[2/3] Wort-Alignment laeuft...")
    try:
        align_model, metadata = whisperx.load_align_model(
            language_code=result["language"], device=device
        )
        result = whisperx.align(
            result["segments"], align_model, metadata, audio, device,
            return_char_alignments=False
        )
        print(f"      -> Alignment abgeschlossen")
    except Exception as e:
        print(f"      -> Alignment uebersprungen: {e}")

    # --- 3. Speaker Diarization ---
    print(f"[3/3] Speaker Diarization laeuft...")

    if hf_token is None:
        hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        print("""
WARNUNG: Kein HuggingFace Token gefunden!
Speaker Diarization wird uebersprungen.

Um Speaker Diarization zu aktivieren:
  1. Account erstellen: https://huggingface.co
  2. Token erstellen:   https://huggingface.co/settings/tokens
  3. Modell-Zugriff beantragen:
       https://huggingface.co/pyannote/speaker-diarization-3.1
       https://huggingface.co/pyannote/segmentation-3.0
  4. Token setzen:
       set HF_TOKEN=hf_xxxx  (Windows CMD)
       $env:HF_TOKEN="hf_xxxx"  (PowerShell)
       oder: python transcribe_full.py ... --hf-token hf_xxxx

Speichere Transkript ohne Speaker-Labels...
""")
        for seg in result["segments"]:
            seg["speaker"] = "SPEAKER"
    else:
        try:
            from whisperx.diarize import DiarizationPipeline
            diarize_model = DiarizationPipeline(
                model_name=diarize_model_name,
                token=hf_token,
                device=device
            )

            diarize_kwargs = {}
            if num_speakers:
                diarize_kwargs["num_speakers"] = num_speakers
            if min_speakers:
                diarize_kwargs["min_speakers"] = min_speakers
            if max_speakers:
                diarize_kwargs["max_speakers"] = max_speakers

            diarize_segments = diarize_model(audio, **diarize_kwargs)
            result = whisperx.assign_word_speakers(diarize_segments, result)

            speakers = set(seg.get("speaker", "UNKNOWN") for seg in result["segments"])
            print(f"      -> {len(speakers)} Sprecher erkannt: {', '.join(sorted(speakers))}")
        except Exception as e:
            print(f"      -> Diarization fehlgeschlagen: {e}")
            for seg in result["segments"]:
                seg["speaker"] = "UNKNOWN"

    # --- Ausgabe ---
    segments = result["segments"]

    txt_path = base_path + "_transcript.txt"
    srt_path = base_path + "_speakers.srt"
    csv_path = base_path + "_markers.csv"

    save_txt(segments, txt_path)
    print(f"\nTranskript gespeichert:       {txt_path}")

    save_srt(segments, srt_path)
    print(f"SRT (Premiere Captions):      {srt_path}")

    save_premiere_markers_csv(segments, csv_path, fps=fps)
    print(f"CSV (Premiere Markers):       {csv_path}")

    print("\n--- Vorschau (erste 10 Segmente) ---")
    for seg in segments[:10]:
        speaker = seg.get("speaker", "UNKNOWN")
        print(f"  [{format_readable_time(seg['start'])}] {speaker}: {seg['text'].strip()}")

    if len(segments) > 10:
        print(f"  ... ({len(segments) - 10} weitere Segmente)")

    print("\nAdobe Premiere Nutzung:")
    print(f"  Captions:  Datei > Importieren > {os.path.basename(srt_path)}")
    print(f"  Markers:   Markers-Panel > Marker importieren > {os.path.basename(csv_path)}")
    print(f"  FPS:       {fps} fps (mit --fps anpassen falls noetig)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Whisper Transkription mit Speaker Diarization fuer Adobe Premiere",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("file", help="Video- oder Audiodatei (mp4, mp3, wav, m4a, mov, ...)")
    parser.add_argument("--model", default="turbo",
                        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3", "turbo"],
                        help="Whisper-Modell (default: turbo). large-v2/v3 = genauer, langsamer")
    parser.add_argument("--language", default="de",
                        help="Sprache (de, en, fr, es, ...) oder 'auto' fuer automatische Erkennung")
    parser.add_argument("--hf-token", default=None,
                        help="HuggingFace Token fuer Speaker Diarization")
    parser.add_argument("--diarize-model", default="pyannote/speaker-diarization-3.1",
                        help="Pyannote Diarization-Modell (default: pyannote/speaker-diarization-3.1)")
    parser.add_argument("--speakers", type=int, default=None,
                        help="Exakte Anzahl Sprecher (optional, verbessert Genauigkeit)")
    parser.add_argument("--min-speakers", type=int, default=None,
                        help="Minimale Anzahl Sprecher")
    parser.add_argument("--max-speakers", type=int, default=None,
                        help="Maximale Anzahl Sprecher")
    parser.add_argument("--fps", type=float, default=25.0,
                        help="Frames pro Sekunde fuer Premiere Markers (default: 25.0)")
    parser.add_argument("--device", default="cuda", choices=["cpu", "cuda"],
                        help="Rechengeraet (default: cuda, fallback: cpu)")

    args = parser.parse_args()

    lang = None if args.language == "auto" else args.language

    transcribe_full(
        file_path=args.file,
        model_name=args.model,
        language=lang,
        hf_token=args.hf_token,
        diarize_model_name=args.diarize_model,
        num_speakers=args.speakers,
        min_speakers=args.min_speakers,
        max_speakers=args.max_speakers,
        fps=args.fps,
        device=args.device,
    )
