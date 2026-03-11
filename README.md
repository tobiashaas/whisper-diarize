# whisper-diarize-premiere

Lokale, GPU-beschleunigte Videotranskription mit **Sprechererkennung** und direktem Export für **Adobe Premiere Pro**.

Basiert auf [WhisperX](https://github.com/m-bain/whisperX) + [pyannote-audio](https://github.com/pyannote/pyannote-audio).

## Features

- Transkription via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (erheblich schneller als OpenAI Whisper)
- Automatische Sprechererkennung (Diarization) — unterscheidet SPEAKER_01, SPEAKER_02, ...
- Wort-genaues Timestamp-Alignment
- GPU-Unterstützung (CUDA) für schnelle Verarbeitung
- Drei Ausgabeformate direkt für Adobe Premiere:
  - `.srt` — Captions mit Sprecher-Labels (Datei > Importieren)
  - `.csv` — Sequence Markers (Markers Panel > Marker importieren)
  - `.txt` — Lesbares Transkript nach Sprecher gruppiert

## Voraussetzungen

### Hardware
- Empfohlen: NVIDIA GPU mit CUDA-Unterstützung
- Funktioniert auch auf CPU (langsamer)

### Software
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) (im PATH)
- NVIDIA CUDA 12.x Treiber (für GPU-Nutzung)

### HuggingFace Token (für Sprechererkennung)

Die Sprechererkennung nutzt pyannote-Modelle, die eine einmalige Registrierung erfordern:

1. **Account erstellen:** https://huggingface.co/join
2. **Token erstellen:** https://huggingface.co/settings/tokens (Read-Zugriff reicht)
3. **Modell-Zugriff beantragen** (einmalig, auf beiden Seiten "Agree" klicken):
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
4. **Token setzen** (Windows PowerShell):
   ```powershell
   $env:HF_TOKEN = "hf_xxxx"
   ```
   Oder dauerhaft über: Systemsteuerung → Umgebungsvariablen → `HF_TOKEN`

> Die Modelle werden beim ersten Start heruntergeladen (~35 MB) und danach lokal gecacht. Kein Internet mehr nötig.

## Installation

```powershell
# Repository klonen
git clone https://github.com/USERNAME/whisper-diarize-premiere.git
cd whisper-diarize-premiere

# Virtuelle Umgebung erstellen
python -m venv venv
venv\Scripts\activate

# Abhängigkeiten installieren (CPU)
pip install whisperx pyannote-audio

# Abhängigkeiten installieren (GPU, CUDA 12.8)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install whisperx pyannote-audio hf_xet
```

## Verwendung

```powershell
cd whisper-diarize-premiere
venv\Scripts\activate

# Einfach (nutzt HF_TOKEN aus Umgebungsvariable)
python transcribe_full.py interview.mp4

# Mit explizitem Token
python transcribe_full.py interview.mp4 --hf-token hf_xxxx

# Mit bekannter Sprecheranzahl (verbessert Genauigkeit)
python transcribe_full.py interview.mp4 --hf-token hf_xxxx --speakers 2

# Alle Optionen
python transcribe_full.py --help
```

### Optionen

| Option | Standard | Beschreibung |
|--------|----------|--------------|
| `--model` | `turbo` | Whisper-Modell: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`, `turbo` |
| `--language` | `de` | Sprache: `de`, `en`, `fr`, ... oder `auto` |
| `--hf-token` | `HF_TOKEN` | HuggingFace Token für Sprechererkennung |
| `--speakers` | auto | Exakte Anzahl Sprecher (optional, verbessert Genauigkeit) |
| `--min-speakers` | — | Minimale Sprecheranzahl |
| `--max-speakers` | — | Maximale Sprecheranzahl |
| `--fps` | `25.0` | Framerate für Premiere Markers (25, 24, 30, ...) |
| `--device` | `cuda` | `cuda` (GPU) oder `cpu` |
| `--diarize-model` | `pyannote/speaker-diarization-3.1` | Pyannote-Modell |

## Ausgabe

Für jede Eingabedatei `video.mp4` werden drei Dateien erzeugt:

### `video_transcript.txt`
Lesbares Transkript, nach Sprecher gruppiert:
```
[SPEAKER_01]
  [00:00.03 - 00:15.50] Wirklich so Kleeblätter, halt in Vorproduktion mal...
  [00:23.14 - 00:30.40] Die Option haben wir dann ja immer noch für...

[SPEAKER_02]
  [00:30.46 - 00:37.90] Ja, wir waren ja schon ein paar Mal hier bei euch...
```

### `video_speakers.srt`
SRT-Untertitel mit Sprecher-Labels für Adobe Premiere:
```
1
00:00:00,030 --> 00:00:15,590
[SPEAKER_01] Wirklich so Kleeblätter, halt in Vorproduktion mal...

2
00:00:30,460 --> 00:00:37,900
[SPEAKER_02] Ja, wir waren ja schon ein paar Mal hier bei euch...
```
**Import in Premiere:** Datei → Importieren → `video_speakers.srt`

### `video_markers.csv`
Sequence Markers für Adobe Premiere:
```
Name    Description    In             Out            Duration       Marker Type
SPEAKER_01    Wirklich so Kleeblätter...    00:00:00:01    00:00:30:11    00:00:30:10    Comment
SPEAKER_02    Ja, wir waren ja schon...     00:00:30:11    00:00:44:12    00:00:14:01    Comment
```
**Import in Premiere:** Markers Panel → (Hamburger-Menü) → Marker importieren → `video_markers.csv`

## Adobe Premiere Workflow

1. Video in Premiere importieren und in Sequenz ziehen
2. SRT importieren: **Datei → Importieren** → `_speakers.srt` → als Caption-Track auf die Timeline ziehen
3. Markers importieren: **Markers Panel öffnen** → Hamburger-Menü → **Marker importieren** → `_markers.csv`
4. Sprecher umbenennen: In `_transcript.txt` nach `SPEAKER_01` suchen & ersetzen mit echtem Namen

## Genutzte Bibliotheken & Projekte

| Projekt | Beschreibung | Link |
|---------|-------------|------|
| **WhisperX** | Erweitertes Whisper mit Word-Alignment & Diarization-Integration | https://github.com/m-bain/whisperX |
| **faster-whisper** | CTranslate2-basierte Whisper-Implementierung (4x schneller) | https://github.com/SYSTRAN/faster-whisper |
| **pyannote-audio** | Speaker Diarization & Segmentation | https://github.com/pyannote/pyannote-audio |
| **OpenAI Whisper** | Original Whisper ASR Modell | https://github.com/openai/whisper |
| **PyTorch** | Deep Learning Framework | https://pytorch.org |

## Lizenz

MIT License — siehe [LICENSE](LICENSE)

---

*Erstellt mit [Claude Code](https://claude.ai/claude-code)*
