const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // Recipe management
    loadRecipes: async () => {
      try {
        return await ipcRenderer.invoke('load-recipes');
      } catch (error) {
        console.error('Error loading recipes:', error);
        return { success: false, error: error.message };
      }
    },

    saveRecipe: async (recipe) => {
      try {
        return await ipcRenderer.invoke('save-recipe', recipe);
      } catch (error) {
        console.error('Error saving recipe:', error);
        return { success: false, error: error.message };
      }
    },

    deleteRecipe: async (recipeName) => {
      try {
        return await ipcRenderer.invoke('delete-recipe', recipeName);
      } catch (error) {
        console.error('Error deleting recipe:', error);
        return { success: false, error: error.message };
      }
    },

    searchRecipes: async (searchTerm) => {
      try {
        return await ipcRenderer.invoke('search-recipes', searchTerm);
      } catch (error) {
        console.error('Error searching recipes:', error);
        return { success: false, error: error.message };
      }
    },

    exportRecipes: async (exportPath) => {
      try {
        return await ipcRenderer.invoke('export-recipes', exportPath);
      } catch (error) {
        console.error('Error exporting recipes:', error);
        return { success: false, error: error.message };
      }
    },

    fetchAddons: async () => {
      try {
        return await ipcRenderer.invoke('fetch-addons');
      } catch (error) {
        console.error('Error fetching addons:', error);
        return { success: false, error: error.message };
      }
    },

    // Event listeners
    onPythonMessage: (callback) => {
      const listener = (event, message) => callback(message);
      ipcRenderer.on('python-message', listener);
      return () => {
        ipcRenderer.removeListener('python-message', listener);
      };
    },

    onMenuExportRecipes: (callback) => {
      const listener = () => callback();
      ipcRenderer.on('menu-export-recipes', listener);
      return () => {
        ipcRenderer.removeListener('menu-export-recipes', listener);
      };
    },

    // Recipe type definitions
    getRecipeTypes: () => {
      return [
        { id: 'shaped', name: 'Shaped Crafting' },
        { id: 'shapeless', name: 'Shapeless Crafting' },
        { id: 'smithing', name: 'Smithing' },
        { id: 'smelting', name: 'Smelting' },
        { id: 'blasting', name: 'Blasting' },
        { id: 'smoking', name: 'Smoking' },
        { id: 'campfire_cooking', name: 'Campfire Cooking' },
        { id: 'stonecutting', name: 'Stonecutting' },
        { id: 'brewing', name: 'Brewing' },
        { id: 'custom', name: 'Custom' }
      ];
    }
  }
);

// Log when the preload script has loaded
console.log('Preload script loaded successfully');
