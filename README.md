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

## Web Version

PrivacyHub is also available as a **fully client-side web application** — no installation required, all data is stored in your browser's localStorage.

**Live:** [https://1000k.ru](https://1000k.ru)

**Features (Web):**
- Same rule CRUD, versioning, images, comments
- Login/Register system (seeded admin: `testers@example.ru` / `testers`)
- Three public feeds: **Community** (all rules), **Authors** (author-published), **My Rules**
- Admin-only Community publishing
- Dark/Light themes + EN/RU/KK languages
- Keyboard shortcuts: `Ctrl+N` New, `Ctrl+S` Save, `Ctrl+F` Search, `Ctrl+A` Admin Panel, `Ctrl+D` Downloads, `Ctrl+Alt+S` Settings
- Export to .txt and .md
- Base64 shareable publish links

**Files:**
- `index.html` — GitHub Pages build
- `PrivacyHub-Web.html` — Standalone local file

## Requirements (Desktop)

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
