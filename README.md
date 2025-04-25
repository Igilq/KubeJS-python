# KubeJS Recipe Manager

A Python-based tool for managing KubeJS recipes for Minecraft modding.

## Overview

KubeJS Recipe Manager is a utility that helps Minecraft modders create, edit, and manage recipes for the KubeJS mod. KubeJS is a popular Minecraft mod that allows players to add custom scripts and recipes to the game using JavaScript.

This tool provides a simple interface for managing these recipes without having to manually edit JS files, making the modding process more accessible and less error-prone.

The application offers two interface modes:
- A graphical user interface (GUI) for a more visual, user-friendly experience (default)
- A command-line interface (CLI) for terminal-based usage

Both modes are available in a single script. The GUI mode is launched by default, and the application will automatically fall back to CLI mode if the GUI cannot be displayed (e.g., if Tkinter is not available).

## Features

- **Create Recipes**: Add new recipes with custom filenames, types, outputs, and ingredients
- **Modded Recipes**: Create recipes using KubeJS addons from https://kubejs.com/wiki/addons
- **Edit Recipes**: Modify existing recipes (now with direct editing after creation)
- **Delete Recipes**: Remove unwanted recipes
- **View Recipes**: Display all recipes in the collection
- **Search Recipes**: Find recipes by filename or content
- **Export Recipes**: Save recipes to a different JS file

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

### Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/KubeJS-Recipe-Manager.git
   cd KubeJS-Recipe-Manager
   ```

2. Set up a virtual environment (recommended):
   ```bash
   # Create a virtual environment
   python -m venv .venv

   # Activate the virtual environment
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. Install development dependencies (optional):
   ```bash
   pip install -r requirements.txt
   ```

4. Make the script executable (Unix-like systems):
   ```bash
   chmod +x kubejs.py
   ```

5. Configuration:
   - The application uses a `config.json` file to store configuration settings
   - By default, recipes are stored in `recipes.json` in the project directory
   - You can modify settings in the config file to change file paths and other options

The core application uses only standard library modules, so you don't need to install any external dependencies for basic functionality.

#### Installing Tkinter

Tkinter is usually included with Python, but some installations might not have it. If you encounter an error like `ModuleNotFoundError: No module named '_tkinter'`, you need to install Tkinter:

- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **macOS with Homebrew**: `brew install python-tk@3.x` (replace 3.x with your Python version)
- **Windows**: Tkinter is included in the standard Python installer from python.org

If you can't install Tkinter, you can still use the CLI mode with the `--cli` flag.

### Installation

1. Clone or download this repository
2. Navigate to the project directory

### Usage

The application can be run in either command-line interface (CLI) mode or graphical user interface (GUI) mode.

#### Graphical User Interface (GUI)

Run the GUI version using Python (default):

```bash
python kubejs.py
```

When you run the application in GUI mode, it will:
1. Attempt to launch the GUI window
2. Ask you if you can see the GUI window
3. If you can see it, you can proceed with using the GUI
4. If you can't see it, you'll be asked if you want to try again or fall back to CLI mode

This ensures that you can always use the application, even if there are issues with displaying the GUI.

The GUI provides a more user-friendly interface with the following tabs:
- **View Recipes**: Browse and manage existing recipes
- **Add Recipe**: Create new recipes with a form interface (now with direct editing after creation)
- **Edit Recipe**: Modify existing recipes
- **Search Recipes**: Find recipes by filename or content

#### Command-Line Interface (CLI)

If you prefer to use the CLI version, you can run it using Python with the --cli flag:

```bash
python kubejs.py --cli
```

Follow the on-screen prompts to manage your recipes.

## Recipe Format

Recipes are stored in a JS file with the following structure:

```js
{
    "recipe_filename": {
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

### Creating a Normal Minecraft Recipe

#### CLI Version

Here's an example of creating a simple crafting recipe using the command-line interface:

1. Run `python kubejs.py --cli`
2. Select option 1 to create a new recipe
3. Enter a unique recipe filename (e.g., "diamond_sword")
4. When asked if you want to make a normal Minecraft recipe or a modded one, select option 1 for normal
5. Enter the recipe type (e.g., "shaped")
6. Enter the output item (e.g., "minecraft:diamond_sword")
7. Enter the ingredients (e.g., "minecraft:stick,minecraft:diamond")
8. The editor will automatically open to allow you to make additional changes

#### GUI Version

Run the GUI version using Python (default):

```bash
# With virtual environment activated
python kubejs.py

# Or directly with the executable (Unix-like systems)
./kubejs.py

# Explicitly specify GUI mode
python kubejs.py --gui
```

When you run the application in GUI mode, it will:
1. Attempt to launch the GUI window
2. Ask you if you can see the GUI window
3. If you can see it, you can proceed with using the GUI
4. If you can't see it, you'll be asked if you want to try again or fall back to CLI mode

This ensures that you can always use the application, even if there are issues with displaying the GUI.

The GUI provides a more user-friendly interface with the following tabs:
- **View Recipes**: Browse and manage existing recipes
- **Add Recipe**: Create new recipes with a form interface (now with direct editing after creation)
- **Edit Recipe**: Modify existing recipes
- **Search Recipes**: Find recipes by filename or content

#### Command-Line Interface (CLI)

If you prefer to use the CLI version, you can run it using Python with the --cli flag:

```bash
# With virtual environment activated
python kubejs.py --cli

# Or directly with the executable (Unix-like systems)
./kubejs.py --cli
```

Follow the on-screen prompts to manage your recipes.

#### GUI Version

Here's how to create a modded recipe using the graphical interface:

1. Run `python kubejs.py` (or without any arguments)
2. Click on the "Add Recipe" tab
3. Fill in the recipe details:
   - Recipe filename: Enter a unique identifier (e.g., "modded_item")
   - Recipe Mode: Select "Modded (KubeJS Addons)"
   - Click "Fetch Addons" to retrieve the list of available addons
   - Select an addon from the dropdown
   - Recipe Type: Select from the dropdown or type (e.g., "custom")
   - Output Item: Enter the item ID (e.g., "modpack:special_item")
   - Ingredients: Enter comma-separated ingredients (e.g., "minecraft:diamond,minecraft:emerald")
4. Click the "Add Recipe" button to save the recipe
5. The editor will automatically open the recipe in the Edit tab for further modifications

## File Structure

- `kubejs.py`: The main script that supports both CLI and GUI modes
- `recipes.json`: The file where recipes are stored in JSON format
- `config.json`: Configuration file for application settings
- `requirements.txt`: List of development dependencies
- `README.md`: Documentation (this file)

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.
