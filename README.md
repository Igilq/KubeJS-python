# KubeJS Recipe Manager

A Python-based tool for managing KubeJS recipes for Minecraft modding.

## Overview

KubeJS Recipe Manager is a utility that helps Minecraft modders create, edit, and manage recipes for the KubeJS mod. KubeJS is a popular Minecraft mod that allows players to add custom scripts and recipes to the game using JavaScript.

This tool provides a simple interface for managing these recipes without having to manually edit JSON files, making the modding process more accessible and less error-prone.

The application offers two interface modes:
- A command-line interface (CLI) for terminal-based usage
- A graphical user interface (GUI) for a more visual, user-friendly experience

Both modes are available in a single script, which you can run with or without the `--gui` flag.

## Features

- **Create Recipes**: Add new recipes with custom IDs, types, outputs, and ingredients
- **Edit Recipes**: Modify existing recipes
- **Delete Recipes**: Remove unwanted recipes
- **View Recipes**: Display all recipes in the collection
- **Search Recipes**: Find recipes by ID or content
- **Export Recipes**: Save recipes to a different JSON file
- **Logging**: All operations are logged for troubleshooting

## Recipe Types

The tool supports various KubeJS recipe types, including:
- Shaped crafting
- Shapeless crafting
- Smithing
- Smelting
- And more!

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Tkinter (included in standard Python installation) for the GUI version

### Installation

1. Clone or download this repository
2. Navigate to the project directory

### Usage

The application can be run in either command-line interface (CLI) mode or graphical user interface (GUI) mode.

#### Command-Line Interface (CLI)

Run the CLI version using Python:

```bash
python kubejs.py
```

Follow the on-screen prompts to manage your recipes.

#### Graphical User Interface (GUI)

Run the GUI version using Python with the --gui flag:

```bash
python kubejs.py --gui
```

The GUI provides a more user-friendly interface with the following tabs:
- **View Recipes**: Browse and manage existing recipes
- **Add Recipe**: Create new recipes with a form interface
- **Edit Recipe**: Modify existing recipes
- **Search Recipes**: Find recipes by ID or content

## Recipe Format

Recipes are stored in a JSON file with the following structure:

```json
{
    "recipe_id": {
        "type": "recipe_type",
        "output": "output_item",
        "ingredients": [
            "ingredient1",
            "ingredient2",
            "..."
        ]
    }
}
```

## Examples

### CLI Version

Here's an example of creating a simple crafting recipe using the command-line interface:

1. Run `python kubejs.py`
2. Select option 1 to create a new recipe
3. Enter a unique recipe ID (e.g., "diamond_sword")
4. Enter the recipe type (e.g., "shaped")
5. Enter the output item (e.g., "minecraft:diamond_sword")
6. Enter the ingredients (e.g., "minecraft:stick,minecraft:diamond")

### GUI Version

Here's how to create a recipe using the graphical interface:

1. Run `python kubejs.py --gui`
2. Click on the "Add Recipe" tab
3. Fill in the recipe details:
   - Recipe ID: Enter a unique identifier (e.g., "diamond_sword")
   - Recipe Type: Select from the dropdown or type (e.g., "shaped")
   - Output Item: Enter the item ID (e.g., "minecraft:diamond_sword")
   - Ingredients: Enter comma-separated ingredients (e.g., "minecraft:stick,minecraft:diamond")
4. Click the "Add Recipe" button to save the recipe

## File Structure

- `kubejs.py`: The main script that supports both CLI and GUI modes
- `recipes.json`: The file where recipes are stored
- `recipe_log.log`: Log file for tracking operations

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.
