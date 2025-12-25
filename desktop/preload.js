const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Settings
  getSetting: (key) => ipcRenderer.invoke('get-setting', key),
  setSetting: (key, value) => ipcRenderer.invoke('set-setting', key, value),

  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  // Navigation listeners
  onNavigate: (callback) => ipcRenderer.on('navigate', (event, url) => callback(url)),
  onAddTransaction: (callback) => ipcRenderer.on('add-transaction', callback),
  onTriggerImport: (callback) => ipcRenderer.on('trigger-import', callback),
  onTriggerExport: (callback) => ipcRenderer.on('trigger-export', callback),

  // Platform info
  platform: process.platform
});

// Add desktop-specific styling when page loads
window.addEventListener('DOMContentLoaded', () => {
  // Add desktop class to body for desktop-specific CSS
  document.body.classList.add('desktop-app');

  // Set platform-specific class
  document.body.classList.add(`platform-${process.platform}`);
});
