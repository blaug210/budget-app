# Budget App - Desktop Application

Native desktop application wrapper for the Budget App using Electron.

## Features

- Native desktop application for Windows, macOS, and Linux
- Automatically starts Django backend server
- Native menu integration
- Keyboard shortcuts
- Offline-capable (once data is loaded)
- System tray integration (future)
- Auto-updates (future)

## Prerequisites

- Node.js 16+ and npm
- Python 3.13+
- Django project dependencies installed

## Installation

1. Install Node.js dependencies:
   ```bash
   cd desktop
   npm install
   ```

2. Ensure Django backend is set up:
   ```bash
   cd ..
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

## Development

Run the desktop app in development mode:

```bash
cd desktop
npm start
```

This will:
1. Start the Django development server automatically
2. Launch the Electron app
3. Load the Django app in the Electron window

## Building

Build the desktop app for distribution:

### macOS
```bash
npm run build:mac
```
Produces: `dist/Budget App.dmg` and `dist/Budget App.app`

### Windows
```bash
npm run build:win
```
Produces: `dist/Budget App Setup.exe` and `dist/Budget App.exe` (portable)

### Linux
```bash
npm run build:linux
```
Produces: `dist/Budget App.AppImage` and `dist/budget-app_1.0.0_amd64.deb`

### All platforms
```bash
npm run build
```

## Keyboard Shortcuts

- `Cmd/Ctrl + N` - New Budget
- `Cmd/Ctrl + B` - View All Budgets
- `Cmd/Ctrl + T` - Add Transaction
- `Cmd/Ctrl + I` - Import Data
- `Cmd/Ctrl + E` - Export Data
- `Cmd/Ctrl + Q` - Quit Application
- `Cmd/Ctrl + R` - Reload
- `Cmd/Ctrl + Shift + I` - Toggle Developer Tools

## Project Structure

```
desktop/
├── main.js           # Main Electron process
├── preload.js        # Preload script for security
├── package.json      # Node.js dependencies
├── assets/           # Icons and assets
│   ├── icon.png
│   ├── icon.icns    # macOS icon
│   └── icon.ico     # Windows icon
└── dist/            # Built applications
```

## How It Works

1. **Main Process** (`main.js`):
   - Starts Django development server on port 8000
   - Creates Electron window
   - Loads Django URL in window
   - Handles application lifecycle
   - Manages native menus and shortcuts

2. **Preload Script** (`preload.js`):
   - Provides secure bridge between renderer and main process
   - Exposes limited API to web pages
   - Adds desktop-specific styling

3. **Django Backend**:
   - Runs in background as subprocess
   - Serves web interface on localhost:8000
   - Automatically starts/stops with desktop app

## Configuration

Settings are stored in:
- macOS: `~/Library/Application Support/budget-app-desktop/config.json`
- Windows: `%APPDATA%\budget-app-desktop\config.json`
- Linux: `~/.config/budget-app-desktop/config.json`

## Troubleshooting

### Django server won't start
- Ensure Python virtual environment is activated
- Check that port 8000 is not in use
- Verify Django dependencies are installed

### App won't build
- Ensure Node.js 16+ is installed
- Delete `node_modules` and run `npm install` again
- Check that all assets exist in `assets/` folder

### Blank window on startup
- Check Django server logs in console
- Verify Django is running on http://127.0.0.1:8000
- Try manually starting Django: `python manage.py runserver`

## Future Enhancements

- [ ] System tray integration
- [ ] Auto-updates
- [ ] Offline mode with local database
- [ ] Native file system integration
- [ ] Backup/restore from desktop
- [ ] Multiple database profiles
- [ ] Dark mode support
- [ ] Custom themes

## License

Same as parent project.
