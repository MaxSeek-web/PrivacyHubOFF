# How to Publish PrivacyHub to GitHub

## Option 1: Using Git CLI (recommended)

### Step 1 — Install Git
Download Git for Windows: https://git-scm.com/download/win

### Step 2 — Open terminal in project folder
```powershell
cd C:\Claude\PrivacyHubApp
```

### Step 3 — Initialize repository
```bash
git init
```

### Step 4 — Add files and commit
```bash
git add main.py README.md requirements.txt .gitignore PUBLISH_GITHUB.md
git commit -m "feat: comments, search content, hotkeys, admin-only community publish, non-destructive pub versions"
```

### Step 5 — Create GitHub repository
1. Go to https://github.com/new
2. Name it `PrivacyHub`
3. Leave it public or choose private
4. **Do NOT** initialize with README (we already have one)

### Step 6 — Link and push
```bash
git remote add origin https://github.com/YOUR_USERNAME/PrivacyHub.git
git branch -M main
git push -u origin main
```

## Option 2: GitHub Desktop (easiest)

1. Download GitHub Desktop: https://desktop.github.com/
2. Sign in to your GitHub account
3. File → Add local repository → Choose `C:\Claude\PrivacyHubApp`
4. Type a summary like "Initial release v2.1.1"
5. Click "Publish repository"

## Option 3: Manual Upload (no Git needed)

1. Go to https://github.com/new
2. Name it `PrivacyHub`, click Create
3. In the repo page, click "uploading an existing file"
4. Drag and drop these files from `C:\Claude\PrivacyHubApp`:
   - `main.py`
   - `README.md`
   - `requirements.txt`
   - `.gitignore`
   - `PUBLISH_GITHUB.md`
5. Click "Commit changes"

## Adding Releases

After pushing code, go to your GitHub repo → **Releases** → **Create a new release**
- Tag version: `v2.1.1`
- Title: `PrivacyHub v2.1.1`
- Drag and drop `PrivacyHub.exe` as a release asset

Done!
