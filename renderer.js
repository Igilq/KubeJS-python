/**
 * KubeJS Recipe Manager - Renderer Process
 * Handles all frontend UI interactions and communication with the Python backend
 */

// Store recipes globally
let recipes = {};
let activeRecipe = null;
let currentView = 'table'; // 'table' or 'card'
let addons = [];

// DOM Ready - Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize event listeners
    initEventListeners();
    
    // Load recipes on startup
    loadRecipes();
    
    // Register handler for menu export event from main process
    window.api.onMenuExportRecipes(() => {
        exportRecipes();
    });
});

// ==========================================
// UI Utility Functions
// ==========================================

/**
 * Show loading overlay with custom message
 * @param {string} message - Message to display
 */
function showLoading(message = 'Loading...') {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingText.textContent = message;
    loadingOverlay.classList.add('show');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.remove('show');
}

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Toast type (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showToast(message, type = 'success', duration = 3000) {
    const toastContainer = document.getElementById('toastContainer');
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastElement = document.createElement('div');
    toastElement.classList.add('toast', 'show');
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    toastElement.id = toastId;
    
    // Add color based on type
    let bgColor = 'bg-success';
    let icon = 'check-circle';
    
    if (type === 'error') {
        bgColor = 'bg-danger';
        icon = 'exclamation-circle';
    } else if (type === 'warning') {
        bgColor = 'bg-warning';
        icon = 'exclamation-triangle';
    } else if (type === 'info') {
        bgColor = 'bg-info';
        icon = 'info-circle';
    }
    
    // Create toast HTML
    toastElement.innerHTML = `
        <div class="toast-header ${bgColor} text-white">
            <i class="fas fa-${icon} me-2"></i>
            <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toastElement);
    
    // Auto remove after duration
    setTimeout(() => {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }, duration);
    
    // Add click handler to close button
    const closeButton = toastElement.querySelector('.btn-close');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            toastElement.classList.remove('show');
            setTimeout(() => {
                toastElement.remove();
            }, 300);
        });
    }
}

/**
 * Highlight search term in text
 * @param {string} text - Text to search in
 * @param {string} term - Term to highlight
 * @returns {string} HTML with highlighted term
 */
function highlightSearchTerm(text, term) {
    if (!term || !text) return text;
    
    // Escape the search term for regex
    const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedTerm})`, 'gi');
    
    return text.replace(regex, '<span class="highlight">$1</span>');
}

// ==========================================
// Recipe Management Functions
// ==========================================

/**
 * Load recipes from backend
 */
async function loadRecipes() {
    showLoading('Loading recipes...');
    
    try {
        const result = await window.api.loadRecipes();
        
        if (result.success) {
            recipes = result.recipes || {};
            updateRecipeUI();
            showToast('Recipes loaded successfully', 'success');
        } else {
            console.error('Error loading recipes:', result.error);
            showToast(`Failed to load recipes: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error loading recipes:', error);
        showToast(`Error loading recipes: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Save a recipe
 * @param {Object} recipe - Recipe object to save
 * @param {string} recipeName - Recipe name/identifier
 * @param {boolean} isNew - Whether this is a new recipe
 */
async function saveRecipe(recipe, recipeName, isNew = true) {
    showLoading(`${isNew ? 'Creating' : 'Updating'} recipe...`);
    
    try {
        const saveData = {
            recipe,
            recipeName,
            isNew
        };
        
        const result = await window.api.saveRecipe(saveData);
        
        if (result.success) {
            // Update local recipes
            if (isNew) {
                recipes[recipeName] = recipe;
            } else {
                recipes[recipeName] = recipe;
            }
            
            updateRecipeUI();
            showToast(`Recipe ${isNew ? 'created' : 'updated'} successfully`, 'success');
            return true;
        } else {
            console.error('Error saving recipe:', result.error);
            showToast(`Failed to save recipe: ${result.error}`, 'error');
            return false;
        }
    } catch (error) {
        console.error('Error saving recipe:', error);
        showToast(`Error saving recipe: ${error.message}`, 'error');
        return false;
    } finally {
        hideLoading();
    }
}

/**
 * Delete a recipe
 * @param {string} recipeName - Recipe name/identifier to delete
 */
async function deleteRecipe(recipeName) {
    showLoading('Deleting recipe...');
    
    try {
        const result = await window.api.deleteRecipe(recipeName);
        
        if (result.success) {
            // Remove from local recipes
            delete recipes[recipeName];
            updateRecipeUI();
            showToast('Recipe deleted successfully', 'success');
            return true;
        } else {
            console.error('Error deleting recipe:', result.error);
            showToast(`Failed to delete recipe: ${result.error}`, 'error');
            return false;
        }
    } catch (error) {
        console.error('Error deleting recipe:', error);
        showToast(`Error deleting recipe: ${error.message}`, 'error');
        return false;
    } finally {
        hideLoading();
    }
}

/**
 * Search recipes
 * @param {string} searchTerm - Term to search for
 */
async function searchRecipes(searchTerm) {
    if (!searchTerm) {
        showToast('Please enter a search term', 'warning');
        return;
    }
    
    showLoading('Searching recipes...');
    
    try {
        const result = await window.api.searchRecipes(searchTerm);
        
        if (result.success) {
            displaySearchResults(result.results, searchTerm);
        } else {
            console.error('Error searching recipes:', result.error);
            showToast(`Failed to search recipes: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error searching recipes:', error);
        showToast(`Error searching recipes: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Export recipes to a file
 */
async function exportRecipes() {
    showLoading('Exporting recipes...');
    
    try {
        const result = await window.api.exportRecipes();
        
        if (result.success) {
            showToast(`Recipes exported successfully to ${result.filePath}`, 'success');
        } else {
            if (result.error === 'Export cancelled') {
                showToast('Export cancelled', 'info');
            } else {
                console.error('Error exporting recipes:', result.error);
                showToast(`Failed to export recipes: ${result.error}`, 'error');
            }
        }
    } catch (error) {
        console.error('Error exporting recipes:', error);
        showToast(`Error exporting recipes: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Fetch KubeJS addons
 */
async function fetchAddons() {
    showLoading('Fetching KubeJS addons...');
    
    try {
        const result = await window.api.fetchAddons();
        
        if (result.success) {
            addons = result.addons || [];
            updateAddonUI();
            showToast('Addons fetched successfully', 'success');
            return true;
        } else {
            console.error('Error fetching addons:', result.error);
            showToast(`Failed to fetch addons: ${result.error}`, 'error');
            return false;
        }
    } catch (error) {
        console.error('Error fetching addons:', error);
        showToast(`Error fetching addons: ${error.message}`, 'error');
        return false;
    } finally {
        hideLoading();
    }
}

// ==========================================
// UI Update Functions
// ==========================================

/**
 * Update the recipe UI based on current recipes
 */
function updateRecipeUI() {
    // Update table view
    updateTableView();
    
    // Update card view
    updateCardView();
    
    // Update edit recipe select
    updateEditRecipeSelect();
}

/**
 * Update the table view with current recipes
 */
function updateTableView() {
    const tableBody = document.getElementById('recipeTableBody');
    tableBody.innerHTML = '';
    
    if (Object.keys(recipes).length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="5" class="text-center">No recipes found. Add a recipe to get started.</td>`;
        tableBody.appendChild(row);
        return;
    }
    
    // Add each recipe to the table
    for (const [name, recipe] of Object.entries(recipes)) {
        const row = document.createElement('tr');
        row.dataset.recipe = name;
        
        // Get ingredients as string
        const ingredientsStr = Array.isArray(recipe.ingredients) 
            ? recipe.ingredients.join(', ')
            : 'No ingredients';
        
        row.innerHTML = `
            <td>${name}</td>
            <td>${recipe.type}</td>
            <td>${recipe.output}</td>
            <td>${ingredientsStr.length > 50 ? ingredientsStr.substring(0, 50) + '...' : ingredientsStr}</td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-outline-primary view-recipe-btn" data-recipe="${name}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary edit-recipe-btn" data-recipe="${name}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-recipe-btn" data-recipe="${name}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    }
    
    // Add event listeners for the buttons
    addTableButtonListeners();
}

/**
 * Add event listeners to table row buttons
 */
function addTableButtonListeners() {
    // View recipe buttons
    document.querySelectorAll('.view-recipe-btn').forEach(button => {
        button.addEventListener('click', () => {
            const recipeName = button.dataset.recipe;
            showRecipeDetails(recipeName);
        });
    });
    
    // Edit recipe buttons
    document.querySelectorAll('.edit-recipe-btn').forEach(button => {
        button.addEventListener('click', () => {
            const recipeName = button.dataset.recipe;
            editRecipe(recipeName);
        });
    });
    
    // Delete recipe buttons
    document.querySelectorAll('.delete-recipe-btn').forEach(button => {
        button.addEventListener('click', () => {
            const recipeName = button.dataset.recipe;
            showDeleteConfirmation(recipeName);
        });
    });
}

/**
 * Update the card view with current recipes
 */
function updateCardView() {
    const cardView = document.getElementById('cardView');
    cardView.innerHTML = '';
    
    if (Object.keys(recipes).length === 0) {
        const col = document.createElement('div');
        col.className = 'col';
        col.innerHTML = `
            <div class="card h-100">
                <div class="card-body text-center">
                    <h5 class="card-title">No recipes found</h5>
                    <p class="card-text">Add a recipe to get started.</p>
                </div>
            </div>
        `;
        cardView.appendChild(col);
        return;
    }
    
    // Add each recipe as a card
    for (const [name, recipe] of Object.entries(recipes)) {
        const col = document.createElement('div');
        col.className = 'col';
        
        // Get ingredients as string
        const ingredientsStr = Array.isArray(recipe.ingredients) 
            ? recipe.ingredients.join(', ')
            : 'No ingredients';
        
        col.innerHTML = `
            <div class="card h-100 recipe-card" data-recipe="${name}">
                <div class="card-header">
                    <h5 class="card-title mb-0">${name}</h5>
                </div>
                <div class="card-body">
                    <p class="card-text"><strong>Type:</strong> ${recipe.type}</p>
                    <p class="card-text"><strong>Output:</strong> ${recipe.output}</p>
                    <p class="card-text"><strong>Ingredients:</strong> ${ingredientsStr.length > 100 ? ingredientsStr.substring(0, 100) + '...' : ingredientsStr}</p>
                </div>
                <div class="card-footer d-flex justify-content-between">
                    <button class="btn btn-sm btn-outline-primary view-recipe-btn" data-recipe="${name}">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-sm btn-outline-secondary edit-recipe-btn" data-recipe="${name}">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </div>
            </div>
        `;
        
        cardView.appendChild(col);
    }
    
    // Add event listeners to the card buttons
    addCardButtonListeners();
}

/**
 * Add event listeners to card buttons
 */
function addCardButtonListeners() {
    // View recipe buttons
    document.querySelectorAll('.card .view-recipe-btn').forEach(button => {
        button.addEventListener('click', () => {
            const recipeName = button.dataset.recipe;
            showRecipeDetails(recipeName);
        });
    });
    
    // Edit recipe buttons
    document.querySelectorAll('.card .edit-recipe-btn').forEach(button => {
        button.addEventListener('click', () => {
            const recipeName = button.dataset.recipe;
            editRecipe(recipeName);
        });
    });
    
    // Make the entire card clickable to view recipe details
    document.querySelectorAll('.recipe-card').forEach(card => {
        card.addEventListener('click', (event) => {
            // Don't trigger if a button was clicked
            if (!event.target.closest('button')) {
                const recipeName = card.dataset.recipe;
                showRecipeDetails(recipeName);
            }
        });
    });
}

/**
 * Update the edit recipe select dropdown
 */
function updateEditRecipeSelect() {
    const select = document.getElementById('editRecipeSelect');
    select.innerHTML = '<option value="">-- Select Recipe --</option>';
    
    // Add each recipe to the select
    for (const name of Object.keys(recipes).sort()) {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        select.appendChild(option);
    }
}

/**
 * Update the addon UI with fetched addons
 */
function updateAddonUI() {
    const addonSelect = document.getElementById('addonSelect');
    addonSelect.innerHTML = '<option value="">-- Select Addon --</option>';
    
    if (addons.length === 0) {
        return;
    }
    
    // Add each addon to the select
    addons.forEach(addon => {
        const option = document.createElement('option');
        option.value = addon.name;
        option.textContent = addon.name;
        option.dataset.url = addon.url;
        addonSelect.appendChild(option);
    });
    
    // Enable the select
    addonSelect.disabled = false;
    
    // Show addon info when selected
    addonSelect.addEventListener('change', updateAddonInfo);
}

/**
 * Update addon info display
 */
function updateAddonInfo() {
    const addonSelect = document.getElementById('addonSelect');
    const addonInfo = document.getElementById('addonInfo');
    
    if (addonSelect.value) {
        const selectedOption = addonSelect.options[addonSelect.selectedIndex];
        const url = selectedOption.dataset.url;
        
        addonInfo.innerHTML = `
            <strong>${addonSelect.value}</strong><br>
            URL: <a href="${url}" target="_blank">${url}</a><br>
            <small>See addon documentation for specific recipe types and formats.</small>
        `;
        addonInfo.style.display = 'block';
    } else {
        addonInfo.style.display = 'none';
    }
}

/**
 * Display search results
 * @param {Array} results - Search results
 * @param {string} searchTerm - The search term
 */
function displaySearchResults(results, searchTerm) {
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = '';
    
    if (results.length === 0) {
        searchResults.innerHTML = `
            <div class="alert alert-warning">
                No recipes found matching <strong>${searchTerm}</strong>.
            </div>
        `;
        return;
    }
    
    // Show results count
    const resultsHeading = document.createElement('h3');
    resultsHeading.innerHTML = `Found <span class="badge bg-primary">${results.length}</span> result${results.length !== 1 ? 's' : ''} for <strong>${searchTerm}</strong>`;
    searchResults.appendChild(resultsHeading);
    
    // Create results list
    const resultsList = document.createElement('div');
    resultsList.className = 'list-group mt-3';
    
    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'list-group-item list-group-item-action';
        
        // Get ingredients as string
        const ingredientsStr = Array.isArray(result.recipe.ingredients) 
            ? result.recipe.ingredients.join(', ')
            : 'No ingredients';
        
        // Highlight matches
        const nameHighlighted = highlightSearchTerm(result.name, searchTerm);
        const typeHighlighted = highlightSearchTerm(result.recipe.type, searchTerm);
        const outputHighlighted = highlightSearchTerm(result.recipe.output, searchTerm);
        const ingredientsHighlighted = highlightSearchTerm(ingredientsStr, searchTerm);
        
        item.innerHTML = `
            <div class="d-flex justify-content-between">
                <h5 class="mb-1">${nameHighlighted}</h5>
                <span class="badge bg-secondary">${typeHighlighted}</span>
            </div>
            <p class="mb-1"><strong>Output:</strong> ${outputHighlighted}</p>
            <p class="mb-1"><strong>Ingredients:</strong> ${ingredientsHighlighted}</p>
            <div class="mt-2">
                <button class="btn btn-sm btn-outline-primary view-search-result" data-recipe="${result.name}">
                    <i class="fas fa-eye"></i> View
                </button>
                <button class="btn btn-sm btn-outline-secondary edit-search-result" data-recipe="${result.name}">
                    <i class="fas fa-edit"></i> Edit
                </button>
            </div>
        `;
        
        resultsList.appendChild(item);
    });
    
    searchResults.appendChild(resultsList);
    
    // Add event listeners to search result buttons
    document.querySelectorAll('.view-search-result').forEach(button => {
        button.addEventListener('click', () => {
            const recipeName = button.dataset.recipe;
            showRecipeDetails(recipeName);
        });
    });
    
    document.querySelectorAll('.edit-search-result').forEach(button => {
        button.addEventListener('click', () => {
            const recipeName = button.dataset.recipe;
            editRecipe(recipeName);
        });
    });
}

/**
 * Show recipe details in a modal
 * @param {string} recipeName - Name of the recipe to show
 */
function showRecipeDetails(recipeName) {
    if (!recipes[recipeName]) {
        showToast(`Recipe '${recipeName}' not found`, 'error');
        return;
    }
    
    const recipe = recipes[recipeName];
    const modal = document.getElementById('recipeDetailsModal');
    const modalTitle = document.getElementById('recipeDetailsModalLabel');
    const modalBody = document.getElementById('recipeDetailsModalBody');
    const editBtn = document.getElementById('editRecipeBtn');
    
    // Set modal title
    modalTitle.textContent = recipeName;
    
    // Set modal body content
    const ingredientsStr = Array.isArray(recipe.ingredients) 
        ? recipe.ingredients.join(', ')
        : 'No ingredients';
    
    modalBody.innerHTML = `
        <div class="card mb-3">
            <div class="card-header bg-light">
                <strong>Recipe Details</strong>
            </div>
            <div class="card-body">
                <p><strong>Type:</strong> ${recipe.type}</p>
                <p><strong>Output:</strong> ${recipe.output}</p>
                <p><strong>Ingredients:</strong></p>
                <ul>
                    ${recipe.ingredients.map(ingredient => `<li>${ingredient}</li>`).join('')}
                </ul>
                ${recipe.addon ? `<p><strong>Addon:</strong> ${recipe.addon}</p>` : ''}
                ${recipe.addon_url ? `<p><strong>Addon URL:</strong> <a href="${recipe.addon_url}" target="_blank">${recipe.addon_url}</a></p>` : ''}
            </div>
        </div>
        
        <div class="card">
            <div class="card-header bg-light">
                <strong>JSON</strong>
            </div>
            <div class="card-body">
                <pre class="mb-0"><code>${JSON.stringify(recipe, null, 2)}</code></pre>
            </div>
        </div>
    `;
    
    // Set up edit button
    editBtn.dataset.recipe = recipeName;
    editBtn.onclick = () => {
        // Close the modal
        const bsModal = bootstrap.Modal.getInstance(modal);
        bsModal.hide();
        // Open the edit form
        editRecipe(recipeName);
    };
    
    // Show the modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Show delete confirmation modal
 * @param {string} recipeName - Name of the recipe to delete
 */
function showDeleteConfirmation(recipeName) {
    if (!recipes[recipeName]) {
        showToast(`Recipe '${recipeName}' not found`, 'error');
        return;
    }
    
    const modal = document.getElementById('deleteConfirmModal');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    // Update modal content
    modal.querySelector('.modal-body').innerHTML = `
        Are you sure you want to delete recipe <strong>${recipeName}</strong>? 
        This action cannot be undone.
    `;
    
    // Set up confirm button
    confirmBtn.dataset.recipe = recipeName;
    confirmBtn.onclick = async () => {
        // Close the modal
        const bsModal = bootstrap.Modal.getInstance(modal);
        bsModal.hide();
        
        // Delete the recipe
        await deleteRecipe(recipeName);
    };
    
    // Show the modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Load a recipe for editing
 * @param {string} recipeName - Name of the recipe to edit
 */
function editRecipe(recipeName) {
    if (!recipes[recipeName]) {
        showToast(`Recipe '${recipeName}' not found`, 'error');
        return;
    }
    
    // Switch to edit tab
    const editTab = document.getElementById('edit-tab');
    bootstrap.Tab.getOrCreateInstance(editTab).show();
    
    // Set recipe in select
    const editRecipeSelect = document.getElementById('editRecipeSelect');
    editRecipeSelect.value = recipeName;
    
    // Load recipe data into form
    const recipe = recipes[recipeName];
    document.getElementById('editRecipeType').value = recipe.type;
    document.getElementById('editOutputItem').value = recipe.output;
    document.getElementById('editIngredients').value = recipe.ingredients.join(', ');
    
    // Show the form
    document.getElementById('editFormContent').style.display = 'block';
    
    // Set active recipe
    activeRecipe = recipeName;
}

// ==========================================
// Event Handlers
// ==========================================

/**
 * Initialize all event listeners
 */
function initEventListeners() {
    // View toggle buttons
    document.getElementById('tableViewBtn').addEventListener('click', () => setView('table'));
    document.getElementById('cardViewBtn').addEventListener('click', () => setView('card'));
    
    // Refresh button
    document.getElementById('refreshRecipesBtn').addEventListener('click', loadRecipes);
    
    // Export button
    document.getElementById('exportBtn').addEventListener('click', exportRecipes);
    
    // Search button
    document.getElementById('searchBtn').addEventListener('click', () => {
        const searchInput = document.getElementById('searchInput');
        searchRecipes(searchInput.value.trim());
    });
    
    // Search input Enter key
    document.getElementById('searchInput').addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            searchRecipes(event.target.value.trim());
        }
    });
    
    // Add Recipe form
    document.getElementById('addRecipeForm').addEventListener('submit', handleAddRecipeSubmit);
    
    // Edit Recipe form
    document.getElementById('editRecipeForm').addEventListener('submit', handleEditRecipeSubmit);
    
    // Recipe mode radios
    document.querySelectorAll('input[name="recipeMode"]').forEach(radio => {
        radio.addEventListener('change', toggleAddonSelection);
    });
    
    // Fetch addons button
    document.getElementById('fetchAddonsBtn').addEventListener('click', fetchAddons);
    
    // Edit recipe select change
    document.getElementById('editRecipeSelect').addEventListener('change', handleEditRecipeSelectChange);
    
    // Reset edit form button
    document.getElementById('resetEditFormBtn').addEventListener('click', resetEditForm);
}

/**
 * Set the current view (table or card)
 * @param {string} view - View type ('table' or 'card')
 */
function setView(view) {
    if (view !== 'table' && view !== 'card') {
        console.error('Invalid view type:', view);
        return;
    }
    
    // Update current view
    currentView = view;
    
    // Update UI
    const tableView = document.getElementById('tableView');
    const cardView = document.getElementById('cardView');
    const tableViewBtn = document.getElementById('tableViewBtn');
    const cardViewBtn = document.getElementById('cardViewBtn');
    
    if (view === 'table') {
        tableView.style.display = 'block';
        cardView.style.display = 'none';
        tableViewBtn.classList.add('active');
        cardViewBtn.classList.remove('active');
    } else {
        tableView.style.display = 'none';
        cardView.style.display = 'block';
        tableViewBtn.classList.remove('active');
        cardViewBtn.classList.add('active');
    }
}

/**
 * Handle Add Recipe form submission
 * @param {Event} event - Form submit event
 */
function handleAddRecipeSubmit(event) {
    event.preventDefault();
    
    // Get form values
    const recipeName = document.getElementById('recipeFilename').value.trim();
    const recipeType = document.getElementById('recipeType').value;
    const outputItem = document.getElementById('outputItem').value.trim();
    const ingredientsText = document.getElementById('ingredients').value.trim();
    const recipeMode = document.querySelector('input[name="recipeMode"]:checked').value;
    
    // Validate form
    if (!recipeName) {
        showToast('Recipe filename is required', 'error');
        return;
    }
    
    if (recipes[recipeName]) {
        showToast('A recipe with this filename already exists', 'error');
        return;
    }
    
    if (!recipeType) {
        showToast('Recipe type is required', 'error');
        return;
    }
    
    if (!outputItem) {
        showToast('Output item is required', 'error');
        return;
    }
    
    if (!ingredientsText) {
        showToast('Ingredients are required', 'error');
        return;
    }
    
    // Parse ingredients
    const ingredients = ingredientsText.split(',')
        .map(ingredient => ingredient.trim())
        .filter(ingredient => ingredient);
    
    if (ingredients.length === 0) {
        showToast('At least one valid ingredient is required', 'error');
        return;
    }
    
    // Create recipe object
    const recipe = {
        type: recipeType,
        output: outputItem,
        ingredients: ingredients
    };
    
    // Add addon info if modded
    if (recipeMode === 'modded') {
        const addonSelect = document.getElementById('addonSelect');
        if (addonSelect.value) {
            const selectedOption = addonSelect.options[addonSelect.selectedIndex];
            recipe.addon = addonSelect.value;
            recipe.addon_url = selectedOption.dataset.url;
        }
    }
    
    // Save recipe
    saveRecipe(recipe, recipeName, true).then(success => {
        if (success) {
            // Reset form
            document.getElementById('addRecipeForm').reset();
            document.getElementById('addonSelectionArea').style.display = 'none';
            document.getElementById('addonInfo').style.display = 'none';
            
            // Switch to edit tab for the new recipe
            editRecipe(recipeName);
        }
    });
}

/**
 * Handle Edit Recipe form submission
 * @param {Event} event - Form submit event
 */
function handleEditRecipeSubmit(event) {
    event.preventDefault();
    
    if (!activeRecipe || !recipes[activeRecipe]) {
        showToast('No recipe selected for editing', 'error');
        return;
    }
    
    // Get form values
    const recipeType = document.getElementById('editRecipeType').value;
    const outputItem = document.getElementById('editOutputItem').value.trim();
    const ingredientsText = document.getElementById('editIngredients').value.trim();
    
    // Validate form
    if (!recipeType) {
        showToast('Recipe type is required', 'error');
        return;
    }
    
    if (!outputItem) {
        showToast('Output item is required', 'error');
        return;
    }
    
    if (!ingredientsText) {
        showToast('Ingredients are required', 'error');
        return;
    }
    
    // Parse ingredients
    const ingredients = ingredientsText.split(',')
        .map(ingredient => ingredient.trim())
        .filter(ingredient => ingredient);
    
    if (ingredients.length === 0) {
        showToast('At least one valid ingredient is required', 'error');
        return;
    }
    
    // Create updated recipe object
    const updatedRecipe = {
        ...recipes[activeRecipe], // Keep any addon info or other properties
        type: recipeType,
        output: outputItem,
        ingredients: ingredients
    };
    
    // Save recipe
    saveRecipe(updatedRecipe, activeRecipe, false).then(success => {
        if (success) {
            // Switch to view tab
            const viewTab = document.getElementById('view-tab');
            bootstrap.Tab.getOrCreateInstance(viewTab).show();
        }
    });
}

/**
 * Toggle addon selection based on recipe mode
 */
function toggleAddonSelection() {
    const recipeMode = document.querySelector('input[name="recipeMode"]:checked').value;
    const addonSelectionArea = document.getElementById('addonSelectionArea');
    const addonInfo = document.getElementById('addonInfo');
    
    if (recipeMode === 'modded') {
        addonSelectionArea.style.display = 'block';
        
        // Show addon info if an addon is selected
        const addonSelect = document.getElementById('addonSelect');
        if (addonSelect.value) {
            addonInfo.style.display = 'block';
        }
    } else {
        addonSelectionArea.style.display = 'none';
        addonInfo.style.display = 'none';
    }
}

/**
 * Handle edit recipe select change
 */
function handleEditRecipeSelectChange() {
    const editRecipeSelect = document.getElementById('editRecipeSelect');
    const recipeName = editRecipeSelect.value;
    
    if (recipeName) {
        editRecipe(recipeName);
    } else {
        // Hide the form
        document.getElementById('editFormContent').style.display = 'none';
        activeRecipe = null;
    }
}

/**
 * Reset edit form to original values
 */
function resetEditForm() {
    if (!activeRecipe || !recipes[activeRecipe]) {
        return;
    }
    
    // Get original recipe
    const recipe = recipes[activeRecipe];
    
    // Reset form values
    document.getElementById('editRecipeType').value = recipe.type;
    document.getElementById('editOutputItem').value = recipe.output;
    document.getElementById('editIngredients').value = recipe.ingredients.join(', ');
    
    showToast('Form reset to original values', 'info');
}

/**
 * Validate form fields and show error messages
 * @param {string} formId - ID of the form to validate
 * @returns {boolean} True if valid, false otherwise
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    // Clear previous error messages
    form.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    // Check required fields
    let isValid = true;
    form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
            
            // Create error message if doesn't exist
            let feedback = field.nextElementSibling;
            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.insertBefore(feedback, field.nextSibling);
            }
            
            feedback.textContent = `${field.labels[0]?.textContent || 'This field'} is required`;
        }
    });
    
    return isValid;
}

/**
 * Parse ingredients from string to array
 * @param {string} ingredientsStr - Comma-separated ingredients string
 * @returns {string[]} Array of ingredients
 */
function parseIngredients(ingredientsStr) {
    return ingredientsStr
        .split(',')
        .map(ingredient => ingredient.trim())
        .filter(ingredient => ingredient);
}

/**
 * Format ingredients array to string
 * @param {string[]} ingredients - Array of ingredients
 * @returns {string} Comma-separated ingredients string
 */
function formatIngredients(ingredients) {
    return Array.isArray(ingredients) ? ingredients.join(', ') : '';
}

// ==========================================
// Initial Setup
// ==========================================

// Initialize with table view
setView('table');
