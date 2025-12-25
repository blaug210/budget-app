# Desktop App Installation Guide

## Quick Start

### 1. Install Dependencies

```bash
cd desktop
npm install
```

### 2. Run the App

```bash
npm start
```

That's it! The app will automatically start the Django backend and open in a native window.

## Detailed Setup

### Prerequisites

#### macOS
- Node.js 16+ (install via: `brew install node`)
- Python 3.13+ (already installed if Django works)
- Xcode Command Line Tools (for building): `xcode-select --install`

#### Windows
- Node.js 16+ (download from: https://nodejs.org/)
- Python 3.13+ (already installed if Django works)
- Windows Build Tools (for building): `npm install --global windows-build-tools`

#### Linux (Ubuntu/Debian)
- Node.js 16+: `sudo apt install nodejs npm`
- Python 3.13+ (already installed if Django works)
- Build tools: `sudo apt install build-essential`

### Installation Steps

1. **Navigate to desktop folder:**
   ```bash
   cd /Users/williamkohl/workspace/budget-app/desktop
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Verify Django setup:**
   ```bash
   cd ..
   source .venv/bin/activate
   python manage.py check
   ```

4. **Run the desktop app:**
   ```bash
   cd desktop
   npm start
   ```

## Building Distributable Packages

### macOS Application (.app / .dmg)

```bash
npm run build:mac
```

Output files in `dist/`:
- `Budget App.app` - macOS application bundle
- `Budget App.dmg` - Disk image for distribution

### Windows Installer (.exe)

```bash
npm run build:win
```

Output files in `dist/`:
- `Budget App Setup.exe` - Windows installer
- `Budget App.exe` - Portable executable (no installation needed)

### Linux Package (.AppImage / .deb)

```bash
npm run build:linux
```

Output files in `dist/`:
- `Budget App.AppImage` - Universal Linux application
- `budget-app_1.0.0_amd64.deb` - Debian package

## Distribution

### macOS
1. Build the .dmg file: `npm run build:mac`
2. Distribute `dist/Budget App.dmg`
3. Users drag to Applications folder to install

### Windows
1. Build the installer: `npm run build:win`
2. Distribute `dist/Budget App Setup.exe`
3. Users run the installer

### Linux
1. Build AppImage: `npm run build:linux`
2. Distribute `dist/Budget App.AppImage`
3. Users make it executable: `chmod +x "Budget App.AppImage"`

## Packaging with Django

The built applications need to include the Django backend. Current setup assumes Django is installed separately.

For fully standalone apps, you'll need to:

1. **Bundle Python** with the app
2. **Include Django dependencies**
3. **Package the database** (SQLite) or configure PostgreSQL

This can be done with:
- PyInstaller (bundle Django as executable)
- Docker (distribute as Docker container)
- Custom installer (include Python installer)

## Troubleshooting

### "npm install" fails
- Try: `npm cache clean --force` then `npm install` again
- Update npm: `npm install -g npm@latest`

### "npm start" doesn't start Django
- Verify Python path in main.js (line 96)
- Manually start Django to test: `cd .. && python manage.py runserver`
- Check that port 8000 is not in use: `lsof -i :8000`

### Building fails
- macOS: Ensure Xcode Command Line Tools are installed
- Windows: Install windows-build-tools
- Linux: Install build-essential

### App starts but shows error page
- Django may have failed to start
- Check console logs for Django errors
- Verify all migrations are run: `python manage.py migrate`

## Configuration

### Change Django Port

Edit `main.js` line 10:
```javascript
const DJANGO_PORT = 8000;  // Change to desired port
```

### Change Python Command

Edit `main.js` line 96:
```javascript
const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
```

### Add Custom Icons

Place icons in `desktop/assets/`:
- `icon.png` (512x512)
- `icon.icns` (macOS)
- `icon.ico` (Windows)

Then rebuild: `npm run build`

## Next Steps

After installation:
1. Launch the app: `npm start`
2. Create your first budget
3. Import transactions
4. Explore keyboard shortcuts (Cmd+K for help)

Enjoy your native Budget App! 🎉
