const recipeEditorArea = document.getElementById('recipeEditorArea');

async function saveRecipe() {
    const data = JSON.parse(recipeEditorArea.value);
    const result = await window.api.saveRecipe(data);
    if (result.success) {
        alert('Przepis zapisany pomyślnie!');
    }
}

async function loadRecipe() {
    const data = await window.api.loadRecipe();
    recipeEditorArea.value = JSON.stringify(data, null, 4);
}

async function loadBlocks() {
    const modpackPath = document.getElementById('modpackPath').value;
    try {
        const blocks = await window.api.loadBlocks(modpackPath);
        const blocksList = document.getElementById('blocks');
        blocksList.innerHTML = ''; // Wyczyść listę
        blocks.forEach(block => {
            const li = document.createElement('li');
            li.textContent = block;
            blocksList.appendChild(li);
        });
    } catch (error) {
        alert('Nie udało się wczytać bloków: ' + error.message);
    }
}