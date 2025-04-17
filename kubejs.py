import json
import os
import argparse
import requests
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Tuple
import tkinter as tk

# Define the file to store recipes
RECIPES_FILE = '../kubejs-python/recipes.js'

# Define the file to store addons database
ADDONS_DB_FILE = 'addons_db.json'

# Define the maximum age of the database in days before it needs to be updated
DB_MAX_AGE_DAYS = 7

# Initialize the recipes dictionary
recipes: Dict[str, Dict[str, Any]] = {}

# KubeJS Addons URL
KUBEJS_ADDONS_URL = "https://kubejs.com/wiki/addons"

def save_addons_to_db(addons: List[Dict[str, str]]) -> bool:
    """Save addons to the local database file.

    Args:
        addons (List[Dict[str, str]]): The list of addons to save

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a database object with timestamp
        db = {
            "timestamp": datetime.now().isoformat(),
            "addons": addons
        }

        with open(ADDONS_DB_FILE, 'w') as file:
            json.dump(db, file, indent=4)

        print(f"Saved {len(addons)} addons to local database.")
        return True
    except Exception as e:
        print(f"Error saving addons to database: {str(e)}")
        return False

def load_addons_from_db() -> Tuple[List[Dict[str, str]], Optional[datetime]]:
    """Load addons from the local database file.

    Returns:
        Tuple[List[Dict[str, str]], Optional[datetime]]: A tuple containing:
            - List of addons
            - Timestamp of the database (None if not available)
    """
    try:
        if not os.path.exists(ADDONS_DB_FILE):
            print("Addons database file not found.")
            return [], None

        with open(ADDONS_DB_FILE, 'r') as file:
            db = json.load(file)

        timestamp = None
        if "timestamp" in db:
            try:
                timestamp = datetime.fromisoformat(db["timestamp"])
            except ValueError:
                print("Invalid timestamp format in database.")

        addons = db.get("addons", [])
        print(f"Loaded {len(addons)} addons from local database.")
        return addons, timestamp
    except Exception as e:
        print(f"Error loading addons from database: {str(e)}")
        return [], None

def is_db_outdated(timestamp: Optional[datetime]) -> bool:
    """Check if the database is outdated.

    Args:
        timestamp (Optional[datetime]): The timestamp of the database

    Returns:
        bool: True if outdated or timestamp is None, False otherwise
    """
    if timestamp is None:
        return True

    max_age = timedelta(days=DB_MAX_AGE_DAYS)
    return datetime.now() - timestamp > max_age

def fetch_kubejs_addons() -> List[Dict[str, str]]:
    """Fetch KubeJS addons from the wiki page or local database.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing addon information
    """
    # First try to load from local database
    addons, timestamp = load_addons_from_db()

    # If database exists and is not outdated, use it
    if addons and not is_db_outdated(timestamp):
        print("Using addons from local database.")
        return addons

    # Otherwise, try to fetch from the web
    print("Fetching addons from the web...")
    try:
        response = requests.get(KUBEJS_ADDONS_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')
        web_addons = []

        # Find all addon links in the page
        # This is a generic approach and might need adjustment based on the actual page structure
        main_content = soup.find('main')
        if main_content:
            addon_links = main_content.find_all('a')
            for link in addon_links:
                href = link.get('href')
                name = link.text.strip()
                if href and name and '/wiki/addons/' in href:
                    web_addons.append({
                        'name': name,
                        'url': f"https://kubejs.com{href}" if href.startswith('/') else href
                    })

        # If we got addons from the web, save them to the database
        if web_addons:
            save_addons_to_db(web_addons)
            return web_addons

        # If web fetch failed but we have old addons, use them
        if addons:
            print("Web fetch failed, using older addons from local database.")
            return addons

        # Otherwise, return empty list
        return []
    except Exception as e:
        print(f"Error fetching KubeJS addons from web: {str(e)}")
        # If web fetch failed but we have old addons, use them
        if addons:
            print("Using older addons from local database.")
            return addons
        return []

def choose_recipe_type() -> Tuple[bool, Optional[Dict[str, str]]]:
    """Ask user if they want to make normal Minecraft recipes or modded ones.

    Returns:
        Tuple[bool, Optional[Dict[str, str]]]: A tuple containing:
            - bool: True if modded, False if normal
            - Optional[Dict[str, str]]: Selected addon info if modded, None otherwise
    """
    print("\nDo you want to make a normal Minecraft recipe or a modded one?")
    print("1. Normal Minecraft recipe")
    print("2. Modded recipe (using KubeJS addons)")

    choice = input("Enter your choice (1-2): ").strip()

    if choice == '2':
        # Fetch addons
        print("\nFetching KubeJS addons...")
        addons = fetch_kubejs_addons()

        if not addons:
            print("No addons found or error fetching addons. Defaulting to normal recipe.")
            return False, None

        print("\nAvailable KubeJS addons:")
        for i, addon in enumerate(addons, 1):
            print(f"{i}. {addon['name']}")

        addon_choice = input(f"Enter addon number (1-{len(addons)}) or 0 to cancel: ").strip()

        try:
            addon_index = int(addon_choice) - 1
            if addon_index == -1:  # User entered 0
                print("Addon selection cancelled. Defaulting to normal recipe.")
                return False, None
            elif 0 <= addon_index < len(addons):
                return True, addons[addon_index]
            else:
                print("Invalid selection. Defaulting to normal recipe.")
                return False, None
        except ValueError:
            print("Invalid input. Defaulting to normal recipe.")
            return False, None
    else:
        # Default to normal recipe for any input other than '2'
        return False, None

def load_recipes() -> None:
    """Load recipes from the JS file."""
    global recipes
    try:
        if os.path.exists(RECIPES_FILE):
            with open(RECIPES_FILE, 'r') as file:
                recipes = json.load(file)
            print(f"Loaded {len(recipes)} recipes from {RECIPES_FILE}")
        else:
            print(f"Recipe file {RECIPES_FILE} not found. Starting with empty recipe collection.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {RECIPES_FILE}. Starting with empty recipe collection.")
    except Exception as e:
        print(f"Error loading recipes: {str(e)}")

def save_recipes() -> bool:
    """Save recipes to the JS file.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(RECIPES_FILE, 'w') as file:
            json.dump(recipes, file, indent=4)
        print(f"Saved {len(recipes)} recipes to {RECIPES_FILE}")
        return True
    except Exception as e:
        # Use messagebox in GUI mode if available, otherwise print
        if 'messagebox' in globals() and TKINTER_AVAILABLE:
            messagebox.showerror("Error", f"Error saving recipes: {str(e)}")
        else:
            print(f"Error saving recipes: {str(e)}")
        return False

def create_recipe() -> None:
    """Create a new recipe and add it to the collection."""
    try:
        recipe_name = input("Enter the recipe filename (without extension): ").strip()
        if not recipe_name:
            print("Recipe filename cannot be empty.")
            return

        if recipe_name in recipes:
            print("A recipe with this filename already exists.")
            return

        # Ask if user wants normal or modded recipe
        is_modded, addon_info = choose_recipe_type()

        # Define recipe types
        recipe_types = [
            "shaped",
            "shapeless",
            "smithing",
            "smelting",
            "blasting",
            "smoking",
            "campfire_cooking",
            "stonecutting",
            "brewing",
            "custom"
        ]

        # If modded and addon info is available, display it
        if is_modded and addon_info:
            print(f"\nUsing addon: {addon_info['name']}")
            print(f"Addon URL: {addon_info['url']}")
            print("Note: You may need to refer to the addon documentation for specific recipe types and formats.")

        # Display recipe types with numbers
        print("\nSelect recipe type:")
        for i, rt in enumerate(recipe_types, 1):
            print(f"{i}. {rt}")

        # Get user selection
        selection = input("Enter number (1-10): ").strip()
        try:
            selection_index = int(selection) - 1
            if 0 <= selection_index < len(recipe_types):
                recipe_type = recipe_types[selection_index]
            else:
                print("Invalid selection. Please enter a number between 1 and 10.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        output = input("Enter the output item: ").strip()
        if not output:
            print("Output item cannot be empty.")
            return

        ingredients_input = input("Enter the ingredients (comma-separated): ").strip()
        if not ingredients_input:
            print("Ingredients cannot be empty.")
            return

        ingredients = [item.strip() for item in ingredients_input.split(',') if item.strip()]

        if not ingredients:
            print("At least one valid ingredient is required.")
            return

        recipe = {
            "type": recipe_type,
            "output": output,
            "ingredients": ingredients
        }

        # Add addon info if modded
        if is_modded and addon_info:
            recipe["addon"] = addon_info["name"]
            recipe["addon_url"] = addon_info["url"]

        recipes[recipe_name] = recipe
        if save_recipes():
            print("Recipe created successfully.")
            # Allow direct editing after creation
            edit_recipe(recipe_name)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def edit_recipe(recipe_name: Optional[str] = None) -> None:
    """Edit an existing recipe."""
    try:
        if recipe_name is None:
            recipe_name = input("Enter the recipe filename to edit: ").strip()

        if not recipe_name:
            print("Recipe filename cannot be empty.")
            return

        if recipe_name not in recipes:
            print("Recipe not found.")
            return

        print("Current recipe:")
        print(json.dumps(recipes[recipe_name], indent=4))

        # Define recipe types
        recipe_types = [
            "shaped",
            "shapeless",
            "smithing",
            "smelting",
            "blasting",
            "smoking",
            "campfire_cooking",
            "stonecutting",
            "brewing",
            "custom"
        ]

        # Display recipe types with numbers
        print("Select recipe type (or press Enter to keep the current type):")
        print("0. Keep current type")
        for i, rt in enumerate(recipe_types, 1):
            print(f"{i}. {rt}")

        # Get user selection
        selection = input("Enter number (0-10): ").strip()
        if selection:
            try:
                selection_index = int(selection)
                if selection_index == 0:
                    recipe_type = ""  # Keep current type
                elif 1 <= selection_index <= len(recipe_types):
                    recipe_type = recipe_types[selection_index - 1]
                else:
                    print("Invalid selection. Using current type.")
                    recipe_type = ""
            except ValueError:
                print("Invalid input. Using current type.")
                recipe_type = ""
        else:
            recipe_type = ""  # Keep current type if Enter is pressed

        output = input("Enter the new output item (or press Enter to keep the current output): ").strip()
        ingredients_input = input("Enter the new ingredients (comma-separated, or press Enter to keep the current ingredients): ").strip()

        if recipe_type:
            recipes[recipe_name]["type"] = recipe_type

        if output:
            recipes[recipe_name]["output"] = output

        if ingredients_input:
            ingredients = [item.strip() for item in ingredients_input.split(',') if item.strip()]
            if ingredients:  # Only update if there's at least one valid ingredient
                recipes[recipe_name]["ingredients"] = ingredients
            else:
                print("Warning: No valid ingredients provided. Keeping existing ingredients.")

        if save_recipes():
            print("Recipe edited successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def delete_recipe() -> None:
    """Delete an existing recipe."""
    try:
        recipe_name = input("Enter the recipe filename to delete: ").strip()
        if not recipe_name:
            print("Recipe filename cannot be empty.")
            return

        if recipe_name not in recipes:
            print("Recipe not found.")
            return

        confirm = input(f"Are you sure you want to delete recipe '{recipe_name}'? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return

        del recipes[recipe_name]
        if save_recipes():
            print("Recipe deleted successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def view_recipes() -> None:
    """Display all recipes in the collection."""
    try:
        if not recipes:
            print("No recipes found.")
            return

        for recipe_name, recipe in recipes.items():
            print(f"Recipe filename: {recipe_name}")
            print(json.dumps(recipe, indent=4))
            print("-" * 30)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def search_recipe() -> None:
    """Search for recipes by filename or content."""
    try:
        if not recipes:
            print("No recipes found.")
            return

        search_term = input("Enter search term: ").strip().lower()
        if not search_term:
            print("Search term cannot be empty.")
            return

        found = False

        for recipe_name, recipe in recipes.items():
            # Search in recipe filename
            if search_term in recipe_name.lower():
                found = True
                print(f"Recipe filename: {recipe_name}")
                print(json.dumps(recipe, indent=4))
                print("-" * 30)
                continue

            # Search in recipe content
            recipe_str = json.dumps(recipe).lower()
            if search_term in recipe_str:
                found = True
                print(f"Recipe filename: {recipe_name}")
                print(json.dumps(recipe, indent=4))
                print("-" * 30)

        if not found:
            print(f"No recipes found matching '{search_term}'.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def export_recipes() -> None:
    """Export recipes to a different file."""
    try:
        filename = input("Enter export filename (e.g., export.js): ").strip()
        if not filename:
            print("Filename cannot be empty.")
            return

        if not filename.endswith('.js'):
            filename += '.js'

        with open(filename, 'w') as file:
            json.dump(recipes, file, indent=4)

        print(f"Recipes exported successfully to {filename}.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def run_cli() -> None:
    """Run the command-line interface version of the KubeJS Recipe Manager."""
    # Load recipes at startup
    load_recipes()

    while True:
        print("\nKubeJS Recipe Manager")
        print("=" * 30)
        print("1. Create a new recipe")
        print("2. Edit an existing recipe")
        print("3. Delete a recipe")
        print("4. View all recipes")
        print("5. Search recipes")
        print("6. Export recipes")
        print("7. Exit")
        print("=" * 30)

        choice = input("Enter your choice (1-7): ").strip()

        if choice == '1':
            create_recipe()
        elif choice == '2':
            edit_recipe()
        elif choice == '3':
            delete_recipe()
        elif choice == '4':
            view_recipes()
        elif choice == '5':
            search_recipe()
        elif choice == '6':
            export_recipes()
        elif choice == '7':
            print("Thank you for using KubeJS Recipe Manager!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

# GUI-related code
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext, filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

class RecipeManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KubeJS Recipe Manager")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.create_view_tab()
        self.create_add_tab()
        self.create_edit_tab()
        self.create_search_tab()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Menu
        self.create_menu()

        # Load recipes
        load_recipes()
        self.update_recipe_list()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Recipes", command=self.export_recipes)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def create_view_tab(self):
        view_tab = ttk.Frame(self.notebook)
        self.notebook.add(view_tab, text="View Recipes")

        # Left panel - Recipe list
        left_panel = ttk.Frame(view_tab)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

        ttk.Label(left_panel, text="Recipes:").pack(anchor=tk.W)

        self.recipe_listbox = tk.Listbox(left_panel, width=30, height=20)
        self.recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.recipe_listbox.bind('<<ListboxSelect>>', self.on_recipe_select)

        scrollbar = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.recipe_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recipe_listbox.config(yscrollcommand=scrollbar.set)

        # Right panel - Recipe details
        right_panel = ttk.Frame(view_tab)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(right_panel, text="Recipe Details:").pack(anchor=tk.W)

        self.recipe_details = scrolledtext.ScrolledText(right_panel, width=50, height=20, wrap=tk.WORD)
        self.recipe_details.pack(fill=tk.BOTH, expand=True)
        self.recipe_details.config(state=tk.DISABLED)

        # Buttons
        button_frame = ttk.Frame(right_panel)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Delete Recipe", command=self.delete_recipe).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Edit Recipe", command=self.edit_selected_recipe).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.update_recipe_list).pack(side=tk.LEFT)

    def create_add_tab(self):
        add_tab = ttk.Frame(self.notebook)
        self.notebook.add(add_tab, text="Add Recipe")

        # Form frame
        form_frame = ttk.Frame(add_tab, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Recipe filename
        ttk.Label(form_frame, text="Recipe filename:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.add_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.add_name_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)

        # Recipe Mode (Normal or Modded)
        ttk.Label(form_frame, text="Recipe Mode:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.add_mode_var = tk.StringVar(value="Normal")
        mode_frame = ttk.Frame(form_frame)
        mode_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text="Normal Minecraft", variable=self.add_mode_var, value="Normal", command=self.toggle_addon_selection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="Modded (KubeJS Addons)", variable=self.add_mode_var, value="Modded", command=self.toggle_addon_selection).pack(side=tk.LEFT)

        # Addon Selection (initially hidden)
        self.addon_frame = ttk.Frame(form_frame)
        self.addon_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.addon_frame.grid_remove()  # Hide initially

        ttk.Label(self.addon_frame, text="Select Addon:").pack(side=tk.LEFT, padx=(0, 5))
        self.addon_var = tk.StringVar()
        self.addon_combo = ttk.Combobox(self.addon_frame, textvariable=self.addon_var, width=40, state="readonly")
        self.addon_combo.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.addon_frame, text="Fetch Addons", command=self.fetch_addons_for_gui).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.addon_frame, text="Update Database", command=self.force_update_addons_database).pack(side=tk.LEFT)

        # Addon Info (initially hidden)
        self.addon_info_frame = ttk.LabelFrame(form_frame, text="Addon Information")
        self.addon_info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        self.addon_info_frame.grid_remove()  # Hide initially

        self.addon_info_text = scrolledtext.ScrolledText(self.addon_info_frame, width=60, height=3, wrap=tk.WORD)
        self.addon_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.addon_info_text.config(state=tk.DISABLED)

        # Store addon data
        self.addons_data = []

        # Recipe Type
        ttk.Label(form_frame, text="Recipe Type:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.add_type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=self.add_type_var, width=38)
        type_combo['values'] = ('shaped', 'shapeless', 'smithing', 'smelting', 'blasting', 'smoking', 'campfire_cooking', 'stonecutting', 'brewing', 'custom')
        type_combo.grid(row=4, column=1, sticky=tk.W, pady=5)

        # Output
        ttk.Label(form_frame, text="Output Item:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.add_output_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.add_output_var, width=40).grid(row=5, column=1, sticky=tk.W, pady=5)

        # Ingredients
        ttk.Label(form_frame, text="Ingredients:").grid(row=6, column=0, sticky=tk.W, pady=5)
        ttk.Label(form_frame, text="(comma-separated)").grid(row=7, column=0, sticky=tk.W)
        self.add_ingredients_text = scrolledtext.ScrolledText(form_frame, width=40, height=10, wrap=tk.WORD)
        self.add_ingredients_text.grid(row=6, column=1, rowspan=2, sticky=tk.W, pady=5)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Clear Form", command=self.clear_add_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add Recipe", command=self.add_recipe).pack(side=tk.LEFT)

    def create_edit_tab(self):
        edit_tab = ttk.Frame(self.notebook)
        self.notebook.add(edit_tab, text="Edit Recipe")

        # Recipe selection
        selection_frame = ttk.Frame(edit_tab, padding="10")
        selection_frame.pack(fill=tk.X)

        ttk.Label(selection_frame, text="Select Recipe:").pack(side=tk.LEFT, padx=5)
        self.edit_recipe_var = tk.StringVar()
        self.edit_recipe_combo = ttk.Combobox(selection_frame, textvariable=self.edit_recipe_var, width=40)
        self.edit_recipe_combo.pack(side=tk.LEFT, padx=5)
        self.edit_recipe_combo.bind('<<ComboboxSelected>>', self.on_edit_recipe_select)

        ttk.Button(selection_frame, text="Load Recipe", command=self.load_recipe_for_edit).pack(side=tk.LEFT, padx=5)

        # Form frame
        form_frame = ttk.Frame(edit_tab, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Recipe Type
        ttk.Label(form_frame, text="Recipe Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.edit_type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=self.edit_type_var, width=38)
        type_combo['values'] = ('shaped', 'shapeless', 'smithing', 'smelting', 'blasting', 'smoking', 'campfire_cooking', 'stonecutting', 'brewing', 'custom')
        type_combo.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Output
        ttk.Label(form_frame, text="Output Item:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.edit_output_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.edit_output_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=5)

        # Ingredients
        ttk.Label(form_frame, text="Ingredients:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(form_frame, text="(comma-separated)").grid(row=3, column=0, sticky=tk.W)
        self.edit_ingredients_text = scrolledtext.ScrolledText(form_frame, width=40, height=10, wrap=tk.WORD)
        self.edit_ingredients_text.grid(row=2, column=1, rowspan=2, sticky=tk.W, pady=5)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Reset Changes", command=self.reset_edit_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Changes", command=self.save_edited_recipe).pack(side=tk.LEFT)

    def create_search_tab(self):
        search_tab = ttk.Frame(self.notebook)
        self.notebook.add(search_tab, text="Search Recipes")

        # Search frame
        search_frame = ttk.Frame(search_tab, padding="10")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Search Term:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_recipes).pack(side=tk.LEFT, padx=5)

        # Results frame
        results_frame = ttk.Frame(search_tab, padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(results_frame, text="Search Results:").pack(anchor=tk.W)

        self.search_results = scrolledtext.ScrolledText(results_frame, width=80, height=20, wrap=tk.WORD)
        self.search_results.pack(fill=tk.BOTH, expand=True)
        self.search_results.config(state=tk.DISABLED)

    def update_recipe_list(self):
        """Update the recipe list in the view tab."""
        self.recipe_listbox.delete(0, tk.END)
        self.edit_recipe_combo['values'] = []

        if not recipes:
            self.status_var.set("No recipes found")
            return

        recipe_names = sorted(recipes.keys())
        for recipe_name in recipe_names:
            self.recipe_listbox.insert(tk.END, recipe_name)

        self.edit_recipe_combo['values'] = recipe_names
        self.status_var.set(f"Loaded {len(recipes)} recipes")

    def on_recipe_select(self, event):
        """Handle recipe selection in the view tab."""
        selection = self.recipe_listbox.curselection()
        if not selection:
            return

        recipe_name = self.recipe_listbox.get(selection[0])
        self.display_recipe_details(recipe_name)

    def display_recipe_details(self, recipe_name):
        """Display recipe details in the view tab."""
        if recipe_name not in recipes:
            return

        recipe = recipes[recipe_name]

        self.recipe_details.config(state=tk.NORMAL)
        self.recipe_details.delete(1.0, tk.END)

        self.recipe_details.insert(tk.END, f"Recipe filename: {recipe_name}\n\n")
        self.recipe_details.insert(tk.END, f"Type: {recipe['type']}\n\n")
        self.recipe_details.insert(tk.END, f"Output: {recipe['output']}\n\n")
        self.recipe_details.insert(tk.END, "Ingredients:\n")

        for ingredient in recipe['ingredients']:
            self.recipe_details.insert(tk.END, f"- {ingredient}\n")

        self.recipe_details.config(state=tk.DISABLED)

    def add_recipe(self):
        """Add a new recipe."""
        recipe_name = self.add_name_var.get().strip()
        recipe_type = self.add_type_var.get().strip()
        output = self.add_output_var.get().strip()
        ingredients_input = self.add_ingredients_text.get(1.0, tk.END).strip()
        is_modded = self.add_mode_var.get() == "Modded"

        # Validate inputs
        if not recipe_name:
            messagebox.showerror("Error", "Recipe filename cannot be empty.")
            return

        if recipe_name in recipes:
            messagebox.showerror("Error", "A recipe with this filename already exists.")
            return

        if not recipe_type:
            messagebox.showerror("Error", "Recipe type cannot be empty.")
            return

        if not output:
            messagebox.showerror("Error", "Output item cannot be empty.")
            return

        if not ingredients_input:
            messagebox.showerror("Error", "Ingredients cannot be empty.")
            return

        ingredients = [item.strip() for item in ingredients_input.split(',') if item.strip()]

        if not ingredients:
            messagebox.showerror("Error", "At least one valid ingredient is required.")
            return

        # Check if modded and addon is selected
        addon_info = None
        if is_modded:
            selected_addon = self.addon_var.get()
            if not selected_addon:
                messagebox.showerror("Error", "Please select an addon or switch to Normal recipe mode.")
                return

            # Find the selected addon in the data
            for addon in self.addons_data:
                if addon['name'] == selected_addon:
                    addon_info = addon
                    break

            if not addon_info:
                messagebox.showerror("Error", "Selected addon information not found.")
                return

        # Create recipe
        recipe = {
            "type": recipe_type,
            "output": output,
            "ingredients": ingredients
        }

        # Add addon info if modded
        if is_modded and addon_info:
            recipe["addon"] = addon_info["name"]
            recipe["addon_url"] = addon_info["url"]

        recipes[recipe_name] = recipe
        if save_recipes():
            messagebox.showinfo("Success", "Recipe created successfully.")
            self.clear_add_form()
            # Set the edit_recipe_var before updating the recipe list
            self.edit_recipe_var.set(recipe_name)
            self.update_recipe_list()
            # Allow direct editing after creation
            self.load_recipe_for_edit()
            self.notebook.select(2)  # Switch to Edit tab

    def toggle_addon_selection(self):
        """Show or hide addon selection based on recipe mode."""
        if self.add_mode_var.get() == "Modded":
            self.addon_frame.grid()
            # If we already have addons data, show the addon info frame
            if self.addons_data:
                self.addon_info_frame.grid()
        else:
            self.addon_frame.grid_remove()
            self.addon_info_frame.grid_remove()

    def force_update_addons_database(self):
        """Force update the addons database from the web."""
        try:
            self.status_var.set("Forcing update of addons database...")
            self.root.update_idletasks()  # Update the UI to show status

            # Delete the existing database file if it exists
            if os.path.exists(ADDONS_DB_FILE):
                os.remove(ADDONS_DB_FILE)
                print("Deleted existing addons database file.")

            # Fetch addons from the web
            response = requests.get(KUBEJS_ADDONS_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            web_addons = []

            main_content = soup.find('main')
            if main_content:
                addon_links = main_content.find_all('a')
                for link in addon_links:
                    href = link.get('href')
                    name = link.text.strip()
                    if href and name and '/wiki/addons/' in href:
                        web_addons.append({
                            'name': name,
                            'url': f"https://kubejs.com{href}" if href.startswith('/') else href
                        })

            if not web_addons:
                messagebox.showinfo("No Addons Found", "No addons found on the web.")
                self.status_var.set("No addons found")
                return

            # Save the addons to the database
            if save_addons_to_db(web_addons):
                messagebox.showinfo("Success", f"Successfully updated addons database with {len(web_addons)} addons.")

                # Update the GUI with the new addons
                self.addons_data = web_addons

                # Update the combo box with addon names
                addon_names = [addon['name'] for addon in self.addons_data]
                self.addon_combo['values'] = addon_names

                # Select the first addon
                if addon_names:
                    self.addon_combo.current(0)
                    self.update_addon_info()

                # Show the addon info frame
                self.addon_info_frame.grid()

                self.status_var.set(f"Updated database with {len(web_addons)} addons")
            else:
                messagebox.showerror("Error", "Failed to save addons to database.")
                self.status_var.set("Failed to update database")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating addons database: {str(e)}")
            self.status_var.set("Error updating database")

    def fetch_addons_for_gui(self):
        """Fetch KubeJS addons for the GUI."""
        try:
            self.status_var.set("Fetching KubeJS addons...")
            self.root.update_idletasks()  # Update the UI to show status

            # Fetch addons
            self.addons_data = fetch_kubejs_addons()

            if not self.addons_data:
                messagebox.showinfo("No Addons Found", "No addons found or error fetching addons.")
                self.status_var.set("No addons found")
                return

            # Update the combo box with addon names
            addon_names = [addon['name'] for addon in self.addons_data]
            self.addon_combo['values'] = addon_names

            # Select the first addon
            if addon_names:
                self.addon_combo.current(0)
                self.update_addon_info()

            # Show the addon info frame
            self.addon_info_frame.grid()

            # Bind the combobox selection event
            self.addon_combo.bind('<<ComboboxSelected>>', lambda e: self.update_addon_info())

            self.status_var.set(f"Fetched {len(self.addons_data)} KubeJS addons")
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching addons: {str(e)}")
            self.status_var.set("Error fetching addons")

    def update_addon_info(self):
        """Update the addon information text."""
        selected_addon = self.addon_var.get()
        if not selected_addon:
            return

        # Find the selected addon in the data
        addon_info = None
        for addon in self.addons_data:
            if addon['name'] == selected_addon:
                addon_info = addon
                break

        if not addon_info:
            return

        # Update the addon info text
        self.addon_info_text.config(state=tk.NORMAL)
        self.addon_info_text.delete(1.0, tk.END)
        self.addon_info_text.insert(tk.END, f"Name: {addon_info['name']}\n")
        self.addon_info_text.insert(tk.END, f"URL: {addon_info['url']}\n")
        self.addon_info_text.insert(tk.END, "Note: You may need to refer to the addon documentation for specific recipe types and formats.")
        self.addon_info_text.config(state=tk.DISABLED)

    def clear_add_form(self):
        """Clear the add recipe form."""
        self.add_name_var.set("")
        self.add_mode_var.set("Normal")
        self.add_type_var.set("")
        self.add_output_var.set("")
        self.add_ingredients_text.delete(1.0, tk.END)
        self.toggle_addon_selection()  # Hide addon selection

    def on_edit_recipe_select(self, event):
        """Handle recipe selection in the edit tab."""
        self.load_recipe_for_edit()

    def load_recipe_for_edit(self):
        """Load a recipe for editing."""
        recipe_name = self.edit_recipe_var.get()
        if not recipe_name or recipe_name not in recipes:
            messagebox.showerror("Error", "Please select a valid recipe.")
            return

        recipe = recipes[recipe_name]

        self.edit_type_var.set(recipe['type'])
        self.edit_output_var.set(recipe['output'])

        self.edit_ingredients_text.delete(1.0, tk.END)
        self.edit_ingredients_text.insert(tk.END, ", ".join(recipe['ingredients']))

    def reset_edit_form(self):
        """Reset the edit form to the original recipe values."""
        self.load_recipe_for_edit()

    def save_edited_recipe(self):
        """Save the edited recipe."""
        recipe_name = self.edit_recipe_var.get()
        if not recipe_name or recipe_name not in recipes:
            messagebox.showerror("Error", "Please select a valid recipe.")
            return

        recipe_type = self.edit_type_var.get().strip()
        output = self.edit_output_var.get().strip()
        ingredients_input = self.edit_ingredients_text.get(1.0, tk.END).strip()

        # Validate inputs
        if not recipe_type:
            messagebox.showerror("Error", "Recipe type cannot be empty.")
            return

        if not output:
            messagebox.showerror("Error", "Output item cannot be empty.")
            return

        if not ingredients_input:
            messagebox.showerror("Error", "Ingredients cannot be empty.")
            return

        ingredients = [item.strip() for item in ingredients_input.split(',') if item.strip()]

        if not ingredients:
            messagebox.showerror("Error", "At least one valid ingredient is required.")
            return

        # Update recipe
        recipes[recipe_name]['type'] = recipe_type
        recipes[recipe_name]['output'] = output
        recipes[recipe_name]['ingredients'] = ingredients

        if save_recipes():
            messagebox.showinfo("Success", "Recipe updated successfully.")
            self.update_recipe_list()

    def edit_selected_recipe(self):
        """Edit the selected recipe from the view tab."""
        selection = self.recipe_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a recipe to edit.")
            return

        recipe_name = self.recipe_listbox.get(selection[0])
        self.edit_recipe_var.set(recipe_name)
        self.load_recipe_for_edit()
        self.notebook.select(2)  # Switch to Edit tab

    def delete_recipe(self):
        """Delete the selected recipe."""
        selection = self.recipe_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a recipe to delete.")
            return

        recipe_name = self.recipe_listbox.get(selection[0])

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete recipe '{recipe_name}'?")
        if not confirm:
            return

        del recipes[recipe_name]
        if save_recipes():
            messagebox.showinfo("Success", "Recipe deleted successfully.")
            self.update_recipe_list()
            self.recipe_details.config(state=tk.NORMAL)
            self.recipe_details.delete(1.0, tk.END)
            self.recipe_details.config(state=tk.DISABLED)

    def search_recipes(self):
        """Search for recipes."""
        search_term = self.search_var.get().strip().lower()

        if not search_term:
            messagebox.showerror("Error", "Search term cannot be empty.")
            return

        self.search_results.config(state=tk.NORMAL)
        self.search_results.delete(1.0, tk.END)

        found = False

        for recipe_name, recipe in recipes.items():
            # Search in recipe filename
            if search_term in recipe_name.lower():
                found = True
                self.search_results.insert(tk.END, f"Recipe filename: {recipe_name}\n")
                self.search_results.insert(tk.END, json.dumps(recipe, indent=4) + "\n")
                self.search_results.insert(tk.END, "-" * 30 + "\n")
                continue

            # Search in recipe content
            recipe_str = json.dumps(recipe).lower()
            if search_term in recipe_str:
                found = True
                self.search_results.insert(tk.END, f"Recipe filename: {recipe_name}\n")
                self.search_results.insert(tk.END, json.dumps(recipe, indent=4) + "\n")
                self.search_results.insert(tk.END, "-" * 30 + "\n")

        if not found:
            self.search_results.insert(tk.END, f"No recipes found matching '{search_term}'.")

        self.search_results.config(state=tk.DISABLED)

    def export_recipes(self):
        """Export recipes to a different file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".js",
            filetypes=[("JavaScript files", "*.js"), ("All files", "*.*")],
            title="Export Recipes"
        )

        if not filename:
            return

        try:
            with open(filename, 'w') as file:
                json.dump(recipes, file, indent=4)

            messagebox.showinfo("Success", f"Recipes exported successfully to {filename}.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About KubeJS Recipe Manager",
            "KubeJS Recipe Manager\n\n"
            "A GUI tool for managing KubeJS recipes for Minecraft modding.\n\n"
            "This tool helps Minecraft modders create, edit, and manage recipes "
            "for the KubeJS mod without having to manually edit JSON files."
        )

def run_gui() -> None:
    """Run the GUI version of the KubeJS Recipe Manager."""
    if not TKINTER_AVAILABLE:
        print("Error: Tkinter is not available. Cannot run GUI mode.")
        print("Falling back to CLI mode...")
        run_cli()
        return

    try:
        root = tk.Tk()
        app = RecipeManagerApp(root)
        root.mainloop()
    except Exception as e:
        if TKINTER_AVAILABLE:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        else:
            print(f"An unexpected error occurred: {str(e)}")

def main() -> None:
    """Main function to run the KubeJS Recipe Manager."""
    parser = argparse.ArgumentParser(description='KubeJS Recipe Manager')
    parser.add_argument('--gui', action='store_true', help='Run in GUI mode (default)')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    args = parser.parse_args()

    # Try to run GUI first unless CLI is explicitly requested
    if args.cli:
        run_cli()
    else:
        # Try to run GUI, will fall back to CLI if Tkinter is not available
        run_gui()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
