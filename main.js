const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;

app.on('ready', () => {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            enableRemoteModule: false,
        },
    });

    mainWindow.loadFile('index.html');
});

ipcMain.handle('save-recipe', async (event, data) => {
    fs.writeFileSync('recipes.json', JSON.stringify(data, null, 4));
    return { success: true };
});

ipcMain.handle('load-recipe', async () => {
    if (fs.existsSync('recipes.json')) {
        const data = fs.readFileSync('recipes.json', 'utf-8');
        return JSON.parse(data);
    }
    return {};
});

ipcMain.handle('load-blocks', async (event, modpackPath) => {
    const blocksFile = path.join(modpackPath, 'blocks.json');
    if (!fs.existsSync(blocksFile)) {
        throw new Error('Plik blocks.json nie istnieje w podanej lokalizacji.');
    }
    const data = fs.readFileSync(blocksFile, 'utf-8');
    return JSON.parse(data);
});