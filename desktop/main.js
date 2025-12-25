const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');

const store = new Store();

let mainWindow;
let djangoProcess;

// Django server configuration
const DJANGO_HOST = '127.0.0.1';
const DJANGO_PORT = 8000;
const DJANGO_URL = `http://${DJANGO_HOST}:${DJANGO_PORT}`;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    icon: path.join(__dirname, 'assets', 'icon.png'),
    show: false
  });

  // Create application menu
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Budget',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('navigate', '/budgets/create/');
          }
        },
        { type: 'separator' },
        {
          label: 'Import',
          accelerator: 'CmdOrCtrl+I',
          click: () => {
            mainWindow.webContents.send('trigger-import');
          }
        },
        {
          label: 'Export',
          accelerator: 'CmdOrCtrl+E',
          click: () => {
            mainWindow.webContents.send('trigger-export');
          }
        },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Budget',
      submenu: [
        {
          label: 'All Budgets',
          accelerator: 'CmdOrCtrl+B',
          click: () => {
            mainWindow.webContents.send('navigate', '/budgets/');
          }
        },
        { type: 'separator' },
        {
          label: 'Add Transaction',
          accelerator: 'CmdOrCtrl+T',
          click: () => {
            mainWindow.webContents.send('add-transaction');
          }
        }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        { type: 'separator' },
        { role: 'front' }
      ]
    },
    {
      role: 'help',
      submenu: [
        {
          label: 'About Budget App',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Budget App',
              message: 'Budget Application',
              detail: 'Version 1.0.0\n\nA comprehensive budget tracking and cost accounting application.',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Load Django URL
  mainWindow.loadURL(DJANGO_URL);

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startDjangoServer() {
  return new Promise((resolve, reject) => {
    const projectRoot = path.join(__dirname, '..');

    // Determine Python command (python3 on Mac/Linux, python on Windows)
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

    // Start Django server
    djangoProcess = spawn(
      pythonCmd,
      ['manage.py', 'runserver', `${DJANGO_HOST}:${DJANGO_PORT}`, '--noreload'],
      {
        cwd: projectRoot,
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      }
    );

    let serverStarted = false;

    djangoProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`Django: ${output}`);

      // Check if server started successfully
      if (output.includes('Starting development server') && !serverStarted) {
        serverStarted = true;
        // Give server a moment to fully start
        setTimeout(() => resolve(), 1000);
      }
    });

    djangoProcess.stderr.on('data', (data) => {
      const error = data.toString();
      console.error(`Django Error: ${error}`);

      // Don't reject on warnings, only on critical errors
      if (error.toLowerCase().includes('error') && error.includes('port') && !serverStarted) {
        reject(new Error(`Django server failed to start: ${error}`));
      }
    });

    djangoProcess.on('close', (code) => {
      console.log(`Django process exited with code ${code}`);
      if (!serverStarted) {
        reject(new Error(`Django server exited with code ${code}`));
      }
    });

    // Timeout if server doesn't start within 10 seconds
    setTimeout(() => {
      if (!serverStarted) {
        reject(new Error('Django server startup timeout'));
      }
    }, 10000);
  });
}

function stopDjangoServer() {
  if (djangoProcess) {
    djangoProcess.kill();
    djangoProcess = null;
  }
}

// App lifecycle
app.whenReady().then(async () => {
  try {
    console.log('Starting Django server...');
    await startDjangoServer();
    console.log('Django server started successfully');
    createWindow();
  } catch (error) {
    console.error('Failed to start Django server:', error);
    const { dialog } = require('electron');
    dialog.showErrorBox(
      'Startup Error',
      `Failed to start the application server:\n\n${error.message}\n\nPlease ensure Python and Django are installed.`
    );
    app.quit();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopDjangoServer();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopDjangoServer();
});

// IPC handlers
ipcMain.handle('get-setting', (event, key) => {
  return store.get(key);
});

ipcMain.handle('set-setting', (event, key, value) => {
  store.set(key, value);
  return true;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});
