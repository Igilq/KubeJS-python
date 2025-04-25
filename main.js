const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const { PythonShell } = require('python-shell');
const Store = require('electron-store');

// Initialize configuration store
const store = new Store();

// Keep a global reference of the window object to prevent garbage collection
let mainWindow;
let pythonProcess = null;

// Default paths for config and recipes
const DEFAULT_CONFIG_PATH = path.join(__dirname, 'config.json');
const DEFAULT_RECIPES_PATH = path.join(__dirname, 'recipes.json');

// Load configuration
function loadConfig() {
  try {
    const configPath = store.get('configPath', DEFAULT_CONFIG_PATH);
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (error) {
    console.error('Error loading config:', error);
    // Create default config if not exists
    const defaultConfig = {
      paths: {
        recipes_file: DEFAULT_RECIPES_PATH,
        addons_db_file: path.join(__dirname, 'addons_db.json'),
        export_default: path.join(__dirname, 'export.js')
      },
      settings: {
        db_max_age_days: 7,
        kubejs_addons_url: 'https://kubejs.com/wiki/addons'
      },
      logging: {
        level: 'INFO',
        format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        file: path.join(__dirname, 'kubejs_manager.log')
      }
    };
    
    try {
      fs.writeFileSync(DEFAULT_CONFIG_PATH, JSON.stringify(defaultConfig, null, 2));
      console.log('Created default config file');
      return defaultConfig;
    } catch (writeError) {
      console.error('Error creating default config:', writeError);
      return defaultConfig;
    }
  }
}

// Create the main window
function createWindow() {
  const config = loadConfig();
  
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    icon: path.join(__dirname, 'assets', 'icon.png')
  });

  // Load the main HTML file
  mainWindow.loadFile('index.html');

  // Open DevTools in development mode
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  // Create application menu
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Export Recipes',
          click: () => mainWindow.webContents.send('menu-export-recipes')
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
        { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'toggleDevTools' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About KubeJS Recipe Manager',
              message: 'KubeJS Recipe Manager',
              detail: 'A tool for managing KubeJS recipes for Minecraft modding.\n\nVersion: 1.0.0\nElectron: ' + process.versions.electron + '\nNode: ' + process.versions.node
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // Start the Python backend process
  startPythonProcess(config);

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
    if (pythonProcess) {
      pythonProcess.end();
      pythonProcess = null;
    }
  });
}

// Debug flag - set to true to enable debug messages
const DEBUG = true;

// Helper function for debug logging
function debugLog(...args) {
  if (DEBUG) {
    console.log('[DEBUG]', ...args);
  }
}

// Start Python process for the backend
function startPythonProcess(config) {
  // Use python3 explicitly on macOS/Linux, fallback to python on Windows
  const defaultPython = process.platform === 'win32' ? 'python' : 'python3';
  const pythonPath = store.get('pythonPath', defaultPython);
  const scriptPath = path.join(__dirname, 'kubejs.py');
  
  debugLog(`Starting Python process with executable: ${pythonPath}`);
  debugLog(`Script path: ${scriptPath}`);
  
  // Create options for Python process with improved stdio configuration
  const options = {
    mode: 'json',
    pythonPath: pythonPath,
    pythonOptions: ['-u'], // unbuffered output is critical for IPC
    scriptPath: __dirname,
    args: ['--ipc'], // Special mode for IPC communication
    stderrParser: line => line, // Capture stderr lines as-is
    stdoutParser: line => {
      debugLog('Python stdout:', line);
      return line;
    }
  };

  try {
    debugLog('Creating PythonShell instance...');
    pythonProcess = new PythonShell('kubejs.py', options);
    
    // Set up message handler for JSON communication
    pythonProcess.on('message', function (message) {
      debugLog('Received message from Python:', message);
      if (mainWindow) {
        mainWindow.webContents.send('python-message', message);
      }
    });

    // Handle standard output that's not JSON
    pythonProcess.stdout.on('data', function (data) {
      debugLog('Python stdout data:', data.toString());
    });

    // Handle standard error output
    pythonProcess.stderr.on('data', function (data) {
      const errorText = data.toString();
      console.error('Python stderr:', errorText);
      
      // Only show error dialog for serious errors, not for normal logging
      if (errorText.includes('Error') || errorText.includes('Exception')) {
        if (mainWindow) {
          dialog.showErrorBox('Python Error', errorText);
        }
      }
    });

    // Handle process errors
    pythonProcess.on('error', function (err) {
      console.error('Python process error:', err);
      
      if (mainWindow) {
        dialog.showErrorBox('Python Error', 
          `Error with Python backend: ${err.message}\n\n` + 
          `Please ensure Python ${pythonPath} is installed correctly and the script has execute permissions.`
        );
      }
    });

    // Handle process exit
    pythonProcess.on('close', function (exitCode, signal) {
      console.log(`Python process exited with code: ${exitCode}, signal: ${signal}`);
      
      // If process terminated with non-zero exit code and it wasn't manually terminated
      if (exitCode !== 0 && exitCode !== null && signal !== 'SIGTERM') {
        if (mainWindow) {
          dialog.showErrorBox('Python Process Terminated', 
            `The Python backend terminated unexpectedly with exit code ${exitCode}.\n\n` +
            `This may indicate an error in the Python script.`
          );
        }
      }
      
      pythonProcess = null;
    });
    
    // Test communication by sending a ping
    setTimeout(() => {
      if (pythonProcess) {
        debugLog('Sending test message to Python process...');
        try {
          pythonProcess.send({ action: 'load_recipes' });
          debugLog('Test message sent successfully');
        } catch (error) {
          debugLog('Failed to send test message:', error);
        }
      }
    }, 1000);
    
    debugLog('Python process started successfully');
  } catch (error) {
    console.error('Error starting Python process:', error);
    
    if (mainWindow) {
      dialog.showErrorBox('Python Error', 
        `Failed to start Python backend: ${error.message}\n\n` +
        `Command: ${pythonPath} ${scriptPath} --ipc\n\n` +
        `Please ensure Python is installed correctly and the script path is valid.`
      );
    }
  }
}

// IPC handlers for communication with the renderer process
ipcMain.handle('load-recipes', async () => {
  if (!pythonProcess) {
    return { success: false, error: 'Python process not running' };
  }
  
  return new Promise((resolve) => {
    try {
      pythonProcess.send({ action: 'load_recipes' });
      
      const messageHandler = (message) => {
        if (message.action === 'recipes_loaded') {
          pythonProcess.removeListener('message', messageHandler);
          resolve(message);
        }
      };
      
      pythonProcess.on('message', messageHandler);
      
      // Set timeout to prevent hanging
      setTimeout(() => {
        pythonProcess.removeListener('message', messageHandler);
        resolve({ success: false, error: 'Timeout waiting for response' });
      }, 5000);
    } catch (error) {
      resolve({ success: false, error: error.message });
    }
  });
});

ipcMain.handle('save-recipe', async (event, recipe) => {
  if (!pythonProcess) {
    return { success: false, error: 'Python process not running' };
  }
  
  return new Promise((resolve) => {
    try {
      pythonProcess.send({ action: 'save_recipe', recipe });
      
      const messageHandler = (message) => {
        if (message.action === 'recipe_saved') {
          pythonProcess.removeListener('message', messageHandler);
          resolve(message);
        }
      };
      
      pythonProcess.on('message', messageHandler);
      
      // Set timeout to prevent hanging
      setTimeout(() => {
        pythonProcess.removeListener('message', messageHandler);
        resolve({ success: false, error: 'Timeout waiting for response' });
      }, 5000);
    } catch (error) {
      resolve({ success: false, error: error.message });
    }
  });
});

ipcMain.handle('delete-recipe', async (event, recipeName) => {
  if (!pythonProcess) {
    return { success: false, error: 'Python process not running' };
  }
  
  return new Promise((resolve) => {
    try {
      pythonProcess.send({ action: 'delete_recipe', recipeName });
      
      const messageHandler = (message) => {
        if (message.action === 'recipe_deleted') {
          pythonProcess.removeListener('message', messageHandler);
          resolve(message);
        }
      };
      
      pythonProcess.on('message', messageHandler);
      
      // Set timeout to prevent hanging
      setTimeout(() => {
        pythonProcess.removeListener('message', messageHandler);
        resolve({ success: false, error: 'Timeout waiting for response' });
      }, 5000);
    } catch (error) {
      resolve({ success: false, error: error.message });
    }
  });
});

ipcMain.handle('search-recipes', async (event, searchTerm) => {
  if (!pythonProcess) {
    return { success: false, error: 'Python process not running' };
  }
  
  return new Promise((resolve) => {
    try {
      pythonProcess.send({ action: 'search_recipes', searchTerm });
      
      const messageHandler = (message) => {
        if (message.action === 'search_results') {
          pythonProcess.removeListener('message', messageHandler);
          resolve(message);
        }
      };
      
      pythonProcess.on('message', messageHandler);
      
      // Set timeout to prevent hanging
      setTimeout(() => {
        pythonProcess.removeListener('message', messageHandler);
        resolve({ success: false, error: 'Timeout waiting for response' });
      }, 5000);
    } catch (error) {
      resolve({ success: false, error: error.message });
    }
  });
});

ipcMain.handle('export-recipes', async (event, exportPath) => {
  if (!pythonProcess) {
    return { success: false, error: 'Python process not running' };
  }
  
  const { filePath } = await dialog.showSaveDialog(mainWindow, {
    title: 'Export Recipes',
    defaultPath: exportPath || 'export.js',
    filters: [
      { name: 'JavaScript Files', extensions: ['js'] },
      { name: 'JSON Files', extensions: ['json'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  
  if (!filePath) {
    return { success: false, error: 'Export cancelled' };
  }
  
  return new Promise((resolve) => {
    try {
      pythonProcess.send({ action: 'export_recipes', filePath });
      
      const messageHandler = (message) => {
        if (message.action === 'recipes_exported') {
          pythonProcess.removeListener('message', messageHandler);
          resolve(message);
        }
      };
      
      pythonProcess.on('message', messageHandler);
      
      // Set timeout to prevent hanging
      setTimeout(() => {
        pythonProcess.removeListener('message', messageHandler);
        resolve({ success: false, error: 'Timeout waiting for response' });
      }, 5000);
    } catch (error) {
      resolve({ success: false, error: error.message });
    }
  });
});

ipcMain.handle('fetch-addons', async () => {
  if (!pythonProcess) {
    return { success: false, error: 'Python process not running' };
  }
  
  return new Promise((resolve) => {
    try {
      pythonProcess.send({ action: 'fetch_addons' });
      
      const messageHandler = (message) => {
        if (message.action === 'addons_fetched') {
          pythonProcess.removeListener('message', messageHandler);
          resolve(message);
        }
      };
      
      pythonProcess.on('message', messageHandler);
      
      // Set timeout to prevent hanging
      setTimeout(() => {
        pythonProcess.removeListener('message', messageHandler);
        resolve({ success: false, error: 'Timeout waiting for response' });
      }, 10000); // Longer timeout for web fetch
    } catch (error) {
      resolve({ success: false, error: error.message });
    }
  });
});

// Application lifecycle events
app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Handle app exit
app.on('before-quit', () => {
  if (pythonProcess) {
    pythonProcess.send({ action: 'exit' });
    pythonProcess.end();
    pythonProcess = null;
  }
});
