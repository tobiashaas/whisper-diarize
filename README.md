# whisper-diarize

Lokale, GPU-beschleunigte Videotranskription mit **Sprechererkennung** und Export in Standardformate.

Basiert auf [WhisperX](https://github.com/m-bain/whisperX) + [pyannote-audio](https://github.com/pyannote/pyannote-audio).

## Features

- Transkription via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (erheblich schneller als OpenAI Whisper)
- Automatische Sprechererkennung (Diarization) — unterscheidet SPEAKER_01, SPEAKER_02, ...
- Wort-genaues Timestamp-Alignment
- GPU-Unterstützung (CUDA) für schnelle Verarbeitung
- Drei Ausgabeformate (offene Standards, überall nutzbar):
  - `.srt` — Standard-Untertitelformat (Premiere, DaVinci Resolve, Final Cut, YouTube, VLC, ...)
  - `.csv` — Tabelle mit Timestamps & Sprecher (Excel, Premiere Markers, ...)
  - `.txt` — Lesbares Transkript nach Sprecher gruppiert

---

## Voraussetzungen

### Hardware
- Empfohlen: NVIDIA GPU mit CUDA-Unterstützung (ab ~4 GB VRAM)
- Funktioniert auch auf CPU (deutlich langsamer)

### Software
- Python 3.10 oder neuer → https://www.python.org/downloads/
- Git → https://git-scm.com/downloads
- FFmpeg (für Audio-Extraktion aus Videos) → https://ffmpeg.org/download.html
  - Windows: [gpl-shared Build herunterladen](https://github.com/BtbN/FFmpeg-Builds/releases), entpacken und den `bin`-Ordner zum PATH hinzufügen
- NVIDIA GPU: CUDA-Treiber 12.x → https://developer.nvidia.com/cuda-downloads

### HuggingFace Token (für Sprechererkennung)

Die Sprechererkennung nutzt pyannote-Modelle, die hinter einer kostenlosen Zugangsbeschränkung liegen.
Einmalige Einrichtung (ca. 5 Minuten):

**Schritt 1 — Account & Token:**
1. Kostenlosen Account erstellen: https://huggingface.co/join
2. Token erstellen (Read-Zugriff reicht): https://huggingface.co/settings/tokens
3. Token kopieren — er beginnt mit `hf_...`

**Schritt 2 — Modell-Zugriff beantragen:**
Beide Seiten aufrufen, einloggen und auf **"Agree and access repository"** klicken:
- https://huggingface.co/pyannote/speaker-diarization-3.1
- https://huggingface.co/pyannote/segmentation-3.0

**Schritt 3 — Token verfügbar machen:**

Option A — dauerhaft (empfohlen):
- Windows: Systemsteuerung → System → Erweiterte Systemeinstellungen → Umgebungsvariablen
- Neue Benutzervariable: Name `HF_TOKEN`, Wert `hf_xxxx`
- Terminal neu starten

Option B — nur für aktuelle PowerShell-Sitzung:
```powershell
$env:HF_TOKEN = "hf_xxxx"
```

Option C — direkt als Argument beim Aufruf:
```powershell
python transcribe_full.py video.mp4 --hf-token hf_xxxx
```

> Die Modelle werden beim ersten Start heruntergeladen (~35 MB) und danach lokal gecacht.
> Ab dem zweiten Start ist kein Internet mehr nötig.

---

## Installation

### 1. Repository klonen

```powershell
git clone https://github.com/tobiashaas/whisper-diarize.git
cd whisper-diarize
```

### 2. Virtuelle Umgebung erstellen

```powershell
python -m venv venv
venv\Scripts\activate
```

> Die virtuelle Umgebung isoliert alle Pakete vom System-Python.
> Nach dem Aktivieren erscheint `(venv)` am Anfang der Eingabezeile.

### 3. Pakete installieren

**Option A — Mit NVIDIA GPU (empfohlen):**

Zuerst PyTorch mit CUDA-Support installieren (Größe: ~2,9 GB):
```powershell
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
```

Dann die restlichen Pakete:
```powershell
pip install whisperx pyannote-audio hf_xet
```

**Option B — Nur CPU:**
```powershell
pip install whisperx pyannote-audio
```

> `hf_xet` ist optional, beschleunigt aber den einmaligen Modell-Download erheblich.

### 4. Installation prüfen

```powershell
python -c "import torch; print('CUDA verfuegbar:', torch.cuda.is_available())"
```

Erwartete Ausgabe bei GPU: `CUDA verfuegbar: True`

---

## Verwendung

```powershell
cd whisper-diarize
venv\Scripts\activate

# Einfach starten (nutzt HF_TOKEN aus Umgebungsvariable)
python transcribe_full.py interview.mp4

# Mit explizitem Token
python transcribe_full.py interview.mp4 --hf-token hf_xxxx

# Mit bekannter Sprecheranzahl (verbessert Genauigkeit)
python transcribe_full.py interview.mp4 --speakers 2

# Englisches Video, besseres Modell
python transcribe_full.py interview.mp4 --language en --model large-v2

# Alle Optionen anzeigen
python transcribe_full.py --help
```

### Alle Optionen

| Option | Standard | Beschreibung |
|--------|----------|--------------|
| `--model` | `turbo` | Whisper-Modell: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`, `turbo` |
| `--language` | `de` | Sprache: `de`, `en`, `fr`, `es`, ... oder `auto` für automatische Erkennung |
| `--hf-token` | `$HF_TOKEN` | HuggingFace Token für Sprechererkennung |
| `--speakers` | auto | Exakte Anzahl Sprecher — verbessert die Genauigkeit wenn bekannt |
| `--min-speakers` | — | Minimale Sprecheranzahl |
| `--max-speakers` | — | Maximale Sprecheranzahl |
| `--fps` | `25.0` | Framerate des Videos für Premiere Markers (24, 25, 30, 60, ...) |
| `--device` | `cuda` | `cuda` für GPU, `cpu` für Prozessor |
| `--diarize-model` | `pyannote/speaker-diarization-3.1` | Alternatives pyannote-Modell |

**Modell-Empfehlungen:**

| Modell | Geschwindigkeit | Genauigkeit | VRAM |
|--------|----------------|-------------|------|
| `turbo` | sehr schnell | gut | ~2 GB |
| `large-v2` | langsamer | sehr gut | ~5 GB |
| `large-v3` | langsamer | am besten | ~5 GB |

---

## Ausgabe

Für jede Eingabedatei `video.mp4` werden drei Dateien im selben Ordner erzeugt:

### `video_transcript.txt`
Lesbares Transkript, nach Sprecher gruppiert:
```
[SPEAKER_01]
  [00:00.00 - 00:12.40] Lorem ipsum dolor sit amet, consectetur adipiscing elit...
  [00:18.20 - 00:31.50] Sed do eiusmod tempor incididunt ut labore et dolore magna...

[SPEAKER_02]
  [00:31.80 - 00:45.10] Ut enim ad minim veniam, quis nostrud exercitation ullamco...
  [00:48.30 - 01:02.70] Duis aute irure dolor in reprehenderit in voluptate velit...
```

### `video_speakers.srt`
Standard-Untertitelformat mit Sprecher-Labels:
```
1
00:00:00,000 --> 00:00:12,400
[SPEAKER_01] Lorem ipsum dolor sit amet, consectetur adipiscing elit...

2
00:00:31,800 --> 00:00:45,100
[SPEAKER_02] Ut enim ad minim veniam, quis nostrud exercitation ullamco...
```

### `video_markers.csv`
Zeitstempel-Tabelle mit Sprecherzuordnung:
```
Name        Description                    In             Out            Duration       Marker Type
SPEAKER_01  Lorem ipsum dolor sit amet...  00:00:00:00    00:00:31:10    00:00:31:10    Comment
SPEAKER_02  Ut enim ad minim veniam...     00:00:31:20    00:01:05:08    00:00:33:13    Comment
```

---

## Import-Anleitungen

### Adobe Premiere Pro

#### SRT als Captions (Untertitelspur)
1. **Datei → Importieren** → `video_speakers.srt` auswählen
2. Die SRT-Datei erscheint im Projektfenster
3. Auf die Timeline ziehen — Premiere erstellt automatisch einen **Caption-Track**
4. Im Caption-Track sind alle Segmente mit `[SPEAKER_01]` / `[SPEAKER_02]` beschriftet
5. Optional: Im **Captions-Panel** Schriftart und Stil anpassen

Offizielle Dokumentation: [Captions in Premiere Pro](https://helpx.adobe.com/premiere-pro/using/working-with-captions.html)

#### CSV als Sequence Markers
1. **Markers Panel** öffnen: Fenster → Marker
2. Hamburger-Menü (☰) oben rechts → **Marker importieren**
3. `video_markers.csv` auswählen
4. Marker erscheinen auf der Timeline — nützlich zur Navigation zwischen Sprechern

> **Wichtig:** Die FPS der CSV muss zur Premiere-Sequenz passen.
> Standard ist 25 fps — bei anderen Framerates `--fps 24` / `--fps 30` / `--fps 60` angeben.

Offizielle Dokumentation: [Marker in Premiere Pro](https://helpx.adobe.com/premiere-pro/using/markers.html)

---

### DaVinci Resolve

#### SRT als Untertitel
1. Im **Cut** oder **Edit**-Tab: **Timeline → Import Subtitles** → `video_speakers.srt`
2. Alternativ: Im Media Pool Rechtsklick → **Import Media** → SRT-Datei wählen, dann auf die Timeline ziehen
3. Ein **Subtitle Track** wird automatisch erstellt
4. Im **Inspector** lassen sich Schrift, Farbe und Position anpassen

> DaVinci Resolve Free unterstützt SRT-Import vollständig.
> Der Premiere-Markers-CSV ist nicht mit Resolve kompatibel — die SRT-Spur ist hier die richtige Wahl.

Offizielle Dokumentation: [DaVinci Resolve Manual](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-Manual.pdf) (Kapitel "Subtitles and Captions")

---

### Final Cut Pro

#### SRT als Captions
1. Projekt öffnen, Video in der Timeline
2. **Datei → Importieren → Captions** → `video_speakers.srt` auswählen
3. Im Dialog **"Zu vorhandenem Clip hinzufügen"** wählen
4. Captions erscheinen als eigene Spur über dem Video-Clip
5. Im **Caption Editor** (Darstellung → Captions anzeigen) lassen sich Texte und Timing nachbearbeiten

> SRT wird nativ unterstützt ab Final Cut Pro 10.6.5.
> Bei älteren Versionen: SRT zuerst mit [Subtitle Edit](https://www.nikse.dk/subtitleedit) in CEA-608 konvertieren.

Offizielle Dokumentation: [Captions in Final Cut Pro](https://support.apple.com/guide/final-cut-pro/captions-overview-ver346df5f4/mac)

---

### Weitere Nutzungsmöglichkeiten

| Anwendung | Format | Verwendung |
|-----------|--------|-----------|
| YouTube Studio | `.srt` | Video hochladen → Untertitel → Datei hochladen |
| Vimeo | `.srt` | Video-Einstellungen → Distribution → Untertitel |
| VLC / jeder Player | `.srt` | Gleicher Ordner + gleicher Dateiname wie Video → automatisch erkannt |
| Word / Google Docs | `.txt` | Öffnen oder einfügen als Protokoll / Transkript-Dokument |
| Notion / Obsidian | `.txt` | Direkt als Notiz einfügen |
| Excel / Numbers | `.csv` | Öffnen für Auswertung, Zeiterfassung, Dokumentation |

### Sprecher umbenennen

In allen Ausgabedateien heißen Sprecher `SPEAKER_01`, `SPEAKER_02` etc.
Einfach mit **Suchen & Ersetzen** in jedem Texteditor umbenennen:

- `SPEAKER_01` → `Max Mustermann`
- `SPEAKER_02` → `Jana Schmidt`

---

## Genutzte Bibliotheken & Projekte

| Projekt | Beschreibung | Link |
|---------|-------------|------|
| **WhisperX** | Erweitertes Whisper mit Word-Alignment & Diarization-Integration | https://github.com/m-bain/whisperX |
| **faster-whisper** | CTranslate2-basierte Whisper-Implementierung (4x schneller) | https://github.com/SYSTRAN/faster-whisper |
| **pyannote-audio** | Speaker Diarization & Segmentation | https://github.com/pyannote/pyannote-audio |
| **OpenAI Whisper** | Original Whisper ASR Modell | https://github.com/openai/whisper |
| **PyTorch** | Deep Learning Framework | https://pytorch.org |

---

## Lizenz

MIT License — siehe [LICENSE](LICENSE)
