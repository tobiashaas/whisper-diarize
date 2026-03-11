# whisper-diarize

Lokale, GPU-beschleunigte Videotranskription mit **Sprechererkennung** und Export in Standardformate.

Basiert auf [WhisperX](https://github.com/m-bain/whisperX) + [pyannote-audio](https://github.com/pyannote/pyannote-audio).

> **Hinweis:** Es gibt keine direkte Software-Integration. Die Ausgabe sind offene Standardformate (SRT, CSV, TXT) die von nahezu jedem Video- und Textprogramm geöffnet werden können.

## Features

- Transkription via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (erheblich schneller als OpenAI Whisper)
- Automatische Sprechererkennung (Diarization) — unterscheidet SPEAKER_01, SPEAKER_02, ...
- Wort-genaues Timestamp-Alignment
- GPU-Unterstützung (CUDA) für schnelle Verarbeitung
- Drei Ausgabeformate (offene Standards, überall nutzbar):
  - `.srt` — Standard-Untertitelformat (Premiere, DaVinci Resolve, Final Cut, YouTube, VLC, ...)
  - `.csv` — Tabelle mit Timestamps & Sprecher (Excel, Premiere Markers, ...)
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
git clone https://github.com/USERNAME/whisper-diarize.git
cd whisper-diarize

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
cd whisper-diarize
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

## Import-Anleitungen

### Adobe Premiere Pro

#### SRT als Captions (Untertitelspur)
1. **Datei → Importieren** → `video_speakers.srt` auswählen
2. Die SRT-Datei erscheint im Projektfenster
3. Auf die Timeline ziehen — Premiere erstellt automatisch einen **Caption-Track**
4. Im Caption-Track sind alle Segmente mit `[SPEAKER_01]` / `[SPEAKER_02]` beschriftet
5. Optional: Im **Captions-Panel** Schriftart und Stil anpassen

#### CSV als Sequence Markers
1. **Markers Panel** öffnen (Fenster → Marker)
2. Hamburger-Menü (☰) oben rechts → **Marker importieren**
3. `video_markers.csv` auswählen
4. Marker erscheinen auf der Timeline, farblich nach Sprecher sortierbar
5. Nützlich für schnelle Navigation: Wo spricht welcher Sprecher?

> **Tipp:** Richtige FPS einstellen damit Marker exakt sitzen:
> `python transcribe_full.py video.mp4 --fps 24` (oder 25, 30, 60)

---

### DaVinci Resolve

#### SRT als Untertitel
1. **Media Pool** → Rechtsklick → **Import Media** → `video_speakers.srt`
2. In den **Edit**-Tab wechseln
3. SRT-Clip aus dem Media Pool auf die Timeline ziehen — wird als **Subtitle Track** eingefügt
4. Alternativ: Timeline → **Import Subtitles** → `video_speakers.srt`
5. Im **Inspector** lassen sich Schrift, Farbe und Position anpassen

#### TXT als Referenz im Schnitt
- `video_transcript.txt` in einem Texteditor nebenher öffnen
- Dient als Inhaltsverzeichnis: Sprecher + Timestamps auf einen Blick
- Hilfreich um schnell zu finden wo ein bestimmtes Thema besprochen wurde

> **Hinweis:** DaVinci Resolve Free unterstützt SRT-Import vollständig. Markers-CSV ist Resolve-spezifisch und nicht kompatibel — die SRT-Spur ist hier die bessere Option.

---

### Final Cut Pro

#### SRT als Captions
1. Projekt öffnen und das Video in der Timeline haben
2. **Datei → Importieren → Captions** → `video_speakers.srt` auswählen
3. Im Dialog **"Zu vorhandenem Clip hinzufügen"** wählen
4. Captions erscheinen als eigene Spur über dem Video-Clip
5. Im **Caption Editor** (Darstellung → Captions anzeigen) lassen sich Texte und Timing nachbearbeiten

> **Hinweis:** Final Cut Pro unterstützt SRT nativ seit Version 10.6.5. Bei älteren Versionen ggf. zuerst in CEA-608 konvertieren (z.B. mit [Subtitle Edit](https://www.nikse.dk/subtitleedit)).

---

### Weitere Nutzungsmöglichkeiten

| Anwendung | Format | Verwendung |
|-----------|--------|-----------|
| YouTube Studio | `.srt` | Video hochladen → Untertitel → Hochladen |
| Vimeo | `.srt` | Video-Einstellungen → Untertitel |
| VLC / jeder Player | `.srt` | Gleicher Ordner wie Video, automatisch erkannt |
| Word / Google Docs | `.txt` | Protokoll, Transkript-Dokument |
| Notion / Obsidian | `.txt` | Notizen, Wissensdatenbank |
| Excel / Numbers | `.csv` | Auswertung, Zeiterfassung, Protokoll |

### Sprecher umbenennen

In allen Ausgabedateien heißen Sprecher `SPEAKER_01`, `SPEAKER_02` etc.
Um echte Namen zu vergeben einfach **Suchen & Ersetzen** nutzen:

- `SPEAKER_01` → `Max Mustermann`
- `SPEAKER_02` → `Jana Schmidt`

Funktioniert in jedem Texteditor, Word, VS Code etc.

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
