# PrivacyHub

PrivacyHub — Desktop application for creating, editing, versioning and exporting privacy / confidentiality rules. Inspired by GitHub (repository structure) and Telegram (clean minimal design).

## Features

- Create, edit, delete rules with versioning
- Attach screenshots/images to rules
- Export to .txt, .md and .pdf (with Cyrillic font support)
- Preview window before publishing
- Publish rules with a shareable base64 code
- Browse public PrivacyHub templates (EN/RU/KK)
- Settings: Dark/Light theme + Language (English, Русский, Қазақша)
- Auto-translate rule content via MyMemory API when switching languages
- Downloads history with Windows Explorer integration
- **Search by title AND content**
- **Comments on rules**
- **Keyboard shortcuts** (see below)
- **Admin-only Community publishing**
- **Non-destructive publishing** (old versions preserved)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + N` | New Rule |
| `Ctrl + F` | Focus search box |
| `Ctrl + S` | Save current rule |
| `Ctrl + A` | Open Admin Panel (admin only) |
| `Ctrl + Alt + S` | Open Settings |
| `Ctrl + D` | Open Downloads history |

## Requirements

- Windows 10/11
- Python 3.10+
- `ttkbootstrap`, `Pillow`, `fpdf2`

## Install dependencies

```bash
pip install ttkbootstrap Pillow fpdf2
```

## Run

```bash
python main.py
```

## Build EXE

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name PrivacyHub --collect-all ttkbootstrap main.py
```

Or using the spec file:

```bash
python -m PyInstaller PrivacyHub.spec
```

## Publish to GitHub

See [PUBLISH_GITHUB.md](PUBLISH_GITHUB.md) for step-by-step instructions.

## License

MIT
