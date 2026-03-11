# whisper-diarize

Lokale, GPU-beschleunigte Videotranskription mit **Sprechererkennung** und Export in Standardformate.

Basiert auf [WhisperX](https://github.com/m-bain/whisperX) + [pyannote-audio](https://github.com/pyannote/pyannote-audio).

## Features

- Transkription via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (erheblich schneller als OpenAI Whisper)
- Automatische Sprechererkennung (Diarization) — unterscheidet SPEAKER_01, SPEAKER_02, ...
- Wort-genaues Timestamp-Alignment
- GPU-Unterstützung (CUDA) für schnelle Verarbeitung
- Zwei Ausgabeformate (offene Standards, überall nutzbar):
  - `.srt` — Standard-Untertitelformat (Premiere, DaVinci Resolve, Final Cut, YouTube, VLC, ...)
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
.\venv\Scripts\Activate.ps1
```

> Die virtuelle Umgebung isoliert alle Pakete vom System-Python.
> Nach dem Aktivieren erscheint `(venv)` am Anfang der Eingabezeile.
> In der klassischen Windows-Eingabeaufforderung (CMD) lautet der Befehl stattdessen `venv\Scripts\activate.bat`.

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
.\venv\Scripts\Activate.ps1

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

Alternativ ohne Aktivierung direkt mit dem Interpreter aus dem Projekt-venv:

```powershell
.\venv\Scripts\python.exe transcribe_full.py interview.mp4
```

**Windows PowerShell: robuster Direktaufruf**

```powershell
.\venv\Scripts\python.exe .\transcribe_full.py "C:\Pfad\mit Leerzeichen\video.mp4"
```

> Lange Windows-Pfade immer in **Anführungszeichen** und in **einer Zeile** übergeben.
> Das ist besonders wichtig bei Pfaden mit Leerzeichen oder Zeichen wie `&`.

### Alle Optionen

| Option | Standard | Beschreibung |
|--------|----------|--------------|
| `--model` | `turbo` | Whisper-Modell: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`, `turbo` |
| `--language` | `de` | Sprache: `de`, `en`, `fr`, `es`, ... oder `auto` für automatische Erkennung |
| `--hf-token` | `$HF_TOKEN` | HuggingFace Token für Sprechererkennung |
| `--speakers` | auto | Exakte Anzahl Sprecher — verbessert die Genauigkeit wenn bekannt |
| `--min-speakers` | — | Minimale Sprecheranzahl |
| `--max-speakers` | — | Maximale Sprecheranzahl |
| `--device` | `cuda` | `cuda` für GPU, `cpu` für Prozessor |
| `--diarize-model` | `pyannote/speaker-diarization-3.1` | Alternatives pyannote-Modell |

**Modell-Empfehlungen:**

| Modell | Geschwindigkeit | Genauigkeit | VRAM |
|--------|----------------|-------------|------|
| `turbo` | sehr schnell | gut | ~2 GB |
| `large-v2` | langsamer | sehr gut | ~5 GB |
| `large-v3` | langsamer | am besten | ~5 GB |

---

## Troubleshooting

### `WinError 127` / `libtorchaudio` / `Die angegebene Prozedur wurde nicht gefunden`

Wenn du so einen Fehler siehst, läuft das Skript fast immer im falschen Python-Interpreter oder mit einer kaputten `torch`/`torchaudio`-Kombination.

**PowerShell (empfohlen):**

```powershell
cd "C:\Github\Whisper TTS"
.\venv\Scripts\Activate.ps1
python transcribe_full.py "C:\Pfad\zur\datei.mp4"
```

**Ohne Aktivierung direkt:**

```powershell
.\venv\Scripts\python.exe transcribe_full.py "C:\Pfad\zur\datei.mp4"
```

Falls `Activate.ps1` blockiert wird:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Wenn du versehentlich das globale Python benutzt, kann Windows andere Paketversionen laden als im Projekt-venv. Genau das fuehrt haeufig zu `torchaudio`-Fehlern.

---

## Ausgabe

Für jede Eingabedatei `video.mp4` werden zwei Dateien im selben Ordner erzeugt:

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

## Import-Anleitungen

> **Wichtig:** Eine `.srt`-Datei wird in den folgenden Tools als **Untertitel / Captions** importiert, nicht als Timeline-Marker.
> Die Sprecherlabels wie `[SPEAKER_01]` bleiben dabei als Text im Untertitel erhalten.
> Wenn du echte Marker brauchst, musst du sie im jeweiligen Tool separat erzeugen oder aus einem anderen Format ableiten.

### Adobe Premiere Pro

#### SRT als Captions (Untertitelspur, nicht als Marker)
1. **Datei → Importieren** → `video_speakers.srt` auswählen
2. Die SRT-Datei erscheint im Projektfenster
3. Auf die Timeline ziehen — Premiere erstellt automatisch einen **Caption-Track**
4. Im Caption-Track sind alle Segmente mit `[SPEAKER_01]` / `[SPEAKER_02]` beschriftet
5. Optional: Im **Captions-Panel** Schriftart und Stil anpassen

Offizielle Dokumentation:
- [Import caption file from third-party service](https://helpx.adobe.com/ca/premiere/desktop/add-text-images/insert-captions/import-caption-file-from-third-party-service.html)
- [Supported file formats for captions](https://helpx.adobe.com/ca/premiere/desktop/add-text-images/insert-captions/supported-file-formats-for-captions.html)

---

### DaVinci Resolve

#### SRT als Untertitel
1. Projekt bzw. Timeline öffnen
2. **Datei → Import → Subtitle** wählen
3. `video_speakers.srt` auswählen
4. Die SRT-Datei landet im Media Pool / Bin
5. Die importierte Subtitle-Datei an den Anfang der Timeline ziehen
6. Resolve legt dafür eine **Subtitle Track** an
7. Im **Inspector** lassen sich Text, Stil, Position und Track-Einstellungen anpassen

> DaVinci Resolve Free unterstützt SRT-Import vollständig.
> Die SRT-Spur ist hier die richtige Wahl.

Offizielle Dokumentation:
- [DaVinci Resolve 20 Editors Guide](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-20-Editors-Guide.pdf?_v=1757574010000)
- [DaVinci Resolve 19 Beginner's Guide](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-19-Beginners-Guide.pdf?_v=1741161610000)

---

### Final Cut Pro

#### SRT als Captions
1. Projekt öffnen, Video in der Timeline
2. **Datei → Importieren → Captions** → `video_speakers.srt` auswählen
3. Im Import-Dialog eine **Caption Role** und die gewünschte Sprache wählen
4. Bei der Positionierung **Relative to Timeline** wählen, wenn die SRT ab dem Projektstart einsortiert werden soll
5. Import bestätigen
6. Captions erscheinen als eigene Spur oben in der Timeline
7. Im **Caption Editor** lassen sich Texte und Timing nachbearbeiten

> SRT wird nativ unterstützt ab Final Cut Pro 10.6.5.
> Bei älteren Versionen: SRT zuerst mit [Subtitle Edit](https://www.nikse.dk/subtitleedit) in CEA-608 konvertieren.

Offizielle Dokumentation:
- [Import captions into Final Cut Pro for Mac](https://support.apple.com/guide/final-cut-pro/import-captions-ver4185ef95a/mac)
- [Intro to captions in Final Cut Pro for Mac](https://support.apple.com/guide/final-cut-pro/intro-to-captions-ver00e40835d/mac)

---

### YouTube Studio

#### SRT als Untertitel hochladen
1. In **YouTube Studio** das gewünschte Video öffnen
2. Links **Subtitles** wählen
3. Falls nötig zuerst **ADD LANGUAGE** klicken und die Sprache auswählen
4. Unter **Subtitles** auf **ADD** klicken
5. **Upload file** wählen
6. Bei einer `.srt`-Datei **With timing** auswählen und hochladen

Offizielle Dokumentation:
- [Add subtitles & captions](https://support.google.com/youtube/answer/2734796?hl=en)
- [Supported subtitle and closed caption files](https://support.google.com/youtube/answer/2734698?hl=en)

---

### Vimeo

#### SRT als Untertitel oder Captions hochladen
1. Die Video-Seite in Vimeo öffnen
2. Links im Player-Bereich **Languages** wählen
3. Die `.srt`-Datei vom Rechner hochladen
4. Für die Datei **Language** und **Type** (`Subtitle` oder `Caption`) auswählen
5. Mit **Upload** bestätigen

Offizielle Dokumentation:
- [How to add captions or subtitles to my video](https://help.vimeo.com/hc/en-us/articles/21956884955537-How-to-add-captions-or-subtitles-to-my-video)

---

### Weitere Nutzungsmöglichkeiten

| Anwendung | Format | Verwendung |
|-----------|--------|-----------|
| YouTube Studio | `.srt` | Im Subtitles-Bereich als Datei mit Timing hochladen |
| Vimeo | `.srt` | Im Languages-Bereich hochladen und Sprache/Typ zuweisen |
| VLC / jeder Player | `.srt` | Gleicher Ordner + gleicher Dateiname wie Video; falls nicht automatisch geladen: Untertiteldatei manuell im Player wählen |
| Word / Google Docs | `.txt` | Öffnen oder einfügen als Protokoll / Transkript-Dokument |
| Notion / Obsidian | `.txt` | Direkt als Notiz einfügen |

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
