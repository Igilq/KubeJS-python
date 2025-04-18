const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
    saveRecipe: (data) => ipcRenderer.invoke('save-recipe', data),
    loadRecipe: () => ipcRenderer.invoke('load-recipe'),
    loadBlocks: (modpackPath) => ipcRenderer.invoke('load-blocks', modpackPath),
});