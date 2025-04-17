import json
import os
import logging
import argparse
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    filename='../kubejs-python/recipe_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define the file to store recipes
RECIPES_FILE = '../kubejs-python/recipes.json'

# Initialize the recipes dictionary
recipes: Dict[str, Dict[str, Any]] = {}

def load_recipes() -> None:
    """Load recipes from the JSON file."""
    global recipes
    try:
        if os.path.exists(RECIPES_FILE):
            with open(RECIPES_FILE, 'r') as file:
                recipes = json.load(file)
            logging.info(f"Loaded {len(recipes)} recipes from {RECIPES_FILE}")
        else:
            logging.info(f"Recipe file {RECIPES_FILE} not found. Starting with empty recipe collection.")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {RECIPES_FILE}. Starting with empty recipe collection.")
    except Exception as e:
        logging.error(f"Error loading recipes: {str(e)}")

def save_recipes() -> bool:
    """Save recipes to the JSON file.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(RECIPES_FILE, 'w') as file:
            json.dump(recipes, file, indent=4)
        logging.info(f"Saved {len(recipes)} recipes to {RECIPES_FILE}")
        return True
    except Exception as e:
        logging.error(f"Error saving recipes: {str(e)}")
        # Use messagebox in GUI mode if available, otherwise print
        if 'messagebox' in globals() and TKINTER_AVAILABLE:
            messagebox.showerror("Error", f"Error saving recipes: {str(e)}")
        else:
            print(f"Error saving recipes: {str(e)}")
        return False

def create_recipe() -> None:
    """Create a new recipe and add it to the collection."""
    try:
        recipe_id = input("Enter the recipe ID: ").strip()
        if not recipe_id:
            print("Recipe ID cannot be empty.")
            logging.warning("Attempted to create recipe with empty ID")
            return

        if recipe_id in recipes:
            print("A recipe with this ID already exists.")
            logging.warning(f"Attempted to create duplicate recipe with ID: {recipe_id}")
            return

        recipe_type = input("Enter the recipe type (shaped, shapeless, smithing, smelting, etc.): ").strip()
        if not recipe_type:
            print("Recipe type cannot be empty.")
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

        recipes[recipe_id] = recipe
        if save_recipes():
            print("Recipe created successfully.")
            logging.info(f"Created new recipe with ID: {recipe_id}")

    except Exception as e:
        logging.error(f"Error creating recipe: {str(e)}")
        print(f"An error occurred: {str(e)}")

def edit_recipe() -> None:
    """Edit an existing recipe."""
    try:
        recipe_id = input("Enter the recipe ID to edit: ").strip()
        if not recipe_id:
            print("Recipe ID cannot be empty.")
            return

        if recipe_id not in recipes:
            print("Recipe not found.")
            logging.warning(f"Attempted to edit non-existent recipe with ID: {recipe_id}")
            return

        print("Current recipe:")
        print(json.dumps(recipes[recipe_id], indent=4))

        recipe_type = input("Enter the new recipe type (or press Enter to keep the current type): ").strip()
        output = input("Enter the new output item (or press Enter to keep the current output): ").strip()
        ingredients_input = input("Enter the new ingredients (comma-separated, or press Enter to keep the current ingredients): ").strip()

        if recipe_type:
            recipes[recipe_id]["type"] = recipe_type

        if output:
            recipes[recipe_id]["output"] = output

        if ingredients_input:
            ingredients = [item.strip() for item in ingredients_input.split(',') if item.strip()]
            if ingredients:  # Only update if there's at least one valid ingredient
                recipes[recipe_id]["ingredients"] = ingredients
            else:
                print("Warning: No valid ingredients provided. Keeping existing ingredients.")

        if save_recipes():
            print("Recipe edited successfully.")
            logging.info(f"Edited recipe with ID: {recipe_id}")

    except Exception as e:
        logging.error(f"Error editing recipe: {str(e)}")
        print(f"An error occurred: {str(e)}")

def delete_recipe() -> None:
    """Delete an existing recipe."""
    try:
        recipe_id = input("Enter the recipe ID to delete: ").strip()
        if not recipe_id:
            print("Recipe ID cannot be empty.")
            return

        if recipe_id not in recipes:
            print("Recipe not found.")
            logging.warning(f"Attempted to delete non-existent recipe with ID: {recipe_id}")
            return

        confirm = input(f"Are you sure you want to delete recipe '{recipe_id}'? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return

        del recipes[recipe_id]
        if save_recipes():
            print("Recipe deleted successfully.")
            logging.info(f"Deleted recipe with ID: {recipe_id}")

    except Exception as e:
        logging.error(f"Error deleting recipe: {str(e)}")
        print(f"An error occurred: {str(e)}")

def view_recipes() -> None:
    """Display all recipes in the collection."""
    try:
        if not recipes:
            print("No recipes found.")
            return

        for recipe_id, recipe in recipes.items():
            print(f"Recipe ID: {recipe_id}")
            print(json.dumps(recipe, indent=4))
            print("-" * 30)

        logging.info("Viewed all recipes")

    except Exception as e:
        logging.error(f"Error viewing recipes: {str(e)}")
        print(f"An error occurred: {str(e)}")

def search_recipe() -> None:
    """Search for recipes by ID or content."""
    try:
        if not recipes:
            print("No recipes found.")
            return

        search_term = input("Enter search term: ").strip().lower()
        if not search_term:
            print("Search term cannot be empty.")
            return

        found = False

        for recipe_id, recipe in recipes.items():
            # Search in recipe ID
            if search_term in recipe_id.lower():
                found = True
                print(f"Recipe ID: {recipe_id}")
                print(json.dumps(recipe, indent=4))
                print("-" * 30)
                continue

            # Search in recipe content
            recipe_str = json.dumps(recipe).lower()
            if search_term in recipe_str:
                found = True
                print(f"Recipe ID: {recipe_id}")
                print(json.dumps(recipe, indent=4))
                print("-" * 30)

        if not found:
            print(f"No recipes found matching '{search_term}'.")
        else:
            logging.info(f"Searched for recipes with term: {search_term}")

    except Exception as e:
        logging.error(f"Error searching recipes: {str(e)}")
        print(f"An error occurred: {str(e)}")

def export_recipes() -> None:
    """Export recipes to a different file."""
    try:
        filename = input("Enter export filename (e.g., export.json): ").strip()
        if not filename:
            print("Filename cannot be empty.")
            return

        if not filename.endswith('.json'):
            filename += '.json'

        with open(filename, 'w') as file:
            json.dump(recipes, file, indent=4)

        print(f"Recipes exported successfully to {filename}.")
        logging.info(f"Exported recipes to {filename}")

    except Exception as e:
        logging.error(f"Error exporting recipes: {str(e)}")
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
            logging.info("Application exited")
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

        # Recipe ID
        ttk.Label(form_frame, text="Recipe ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.add_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.add_id_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)

        # Recipe Type
        ttk.Label(form_frame, text="Recipe Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.add_type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=self.add_type_var, width=38)
        type_combo['values'] = ('shaped', 'shapeless', 'smithing', 'smelting', 'blasting', 'smoking', 'campfire_cooking')
        type_combo.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Output
        ttk.Label(form_frame, text="Output Item:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.add_output_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.add_output_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)

        # Ingredients
        ttk.Label(form_frame, text="Ingredients:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(form_frame, text="(comma-separated)").grid(row=4, column=0, sticky=tk.W)
        self.add_ingredients_text = scrolledtext.ScrolledText(form_frame, width=40, height=10, wrap=tk.WORD)
        self.add_ingredients_text.grid(row=3, column=1, rowspan=2, sticky=tk.W, pady=5)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

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
        type_combo['values'] = ('shaped', 'shapeless', 'smithing', 'smelting', 'blasting', 'smoking', 'campfire_cooking')
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

        recipe_ids = sorted(recipes.keys())
        for recipe_id in recipe_ids:
            self.recipe_listbox.insert(tk.END, recipe_id)

        self.edit_recipe_combo['values'] = recipe_ids
        self.status_var.set(f"Loaded {len(recipes)} recipes")

    def on_recipe_select(self, event):
        """Handle recipe selection in the view tab."""
        selection = self.recipe_listbox.curselection()
        if not selection:
            return

        recipe_id = self.recipe_listbox.get(selection[0])
        self.display_recipe_details(recipe_id)

    def display_recipe_details(self, recipe_id):
        """Display recipe details in the view tab."""
        if recipe_id not in recipes:
            return

        recipe = recipes[recipe_id]

        self.recipe_details.config(state=tk.NORMAL)
        self.recipe_details.delete(1.0, tk.END)

        self.recipe_details.insert(tk.END, f"Recipe ID: {recipe_id}\n\n")
        self.recipe_details.insert(tk.END, f"Type: {recipe['type']}\n\n")
        self.recipe_details.insert(tk.END, f"Output: {recipe['output']}\n\n")
        self.recipe_details.insert(tk.END, "Ingredients:\n")

        for ingredient in recipe['ingredients']:
            self.recipe_details.insert(tk.END, f"- {ingredient}\n")

        self.recipe_details.config(state=tk.DISABLED)

    def add_recipe(self):
        """Add a new recipe."""
        recipe_id = self.add_id_var.get().strip()
        recipe_type = self.add_type_var.get().strip()
        output = self.add_output_var.get().strip()
        ingredients_input = self.add_ingredients_text.get(1.0, tk.END).strip()

        # Validate inputs
        if not recipe_id:
            messagebox.showerror("Error", "Recipe ID cannot be empty.")
            return

        if recipe_id in recipes:
            messagebox.showerror("Error", "A recipe with this ID already exists.")
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

        # Create recipe
        recipe = {
            "type": recipe_type,
            "output": output,
            "ingredients": ingredients
        }

        recipes[recipe_id] = recipe
        if save_recipes():
            messagebox.showinfo("Success", "Recipe created successfully.")
            logging.info(f"Created new recipe with ID: {recipe_id}")
            self.clear_add_form()
            self.update_recipe_list()

    def clear_add_form(self):
        """Clear the add recipe form."""
        self.add_id_var.set("")
        self.add_type_var.set("")
        self.add_output_var.set("")
        self.add_ingredients_text.delete(1.0, tk.END)

    def on_edit_recipe_select(self, event):
        """Handle recipe selection in the edit tab."""
        self.load_recipe_for_edit()

    def load_recipe_for_edit(self):
        """Load a recipe for editing."""
        recipe_id = self.edit_recipe_var.get()
        if not recipe_id or recipe_id not in recipes:
            messagebox.showerror("Error", "Please select a valid recipe.")
            return

        recipe = recipes[recipe_id]

        self.edit_type_var.set(recipe['type'])
        self.edit_output_var.set(recipe['output'])

        self.edit_ingredients_text.delete(1.0, tk.END)
        self.edit_ingredients_text.insert(tk.END, ", ".join(recipe['ingredients']))

    def reset_edit_form(self):
        """Reset the edit form to the original recipe values."""
        self.load_recipe_for_edit()

    def save_edited_recipe(self):
        """Save the edited recipe."""
        recipe_id = self.edit_recipe_var.get()
        if not recipe_id or recipe_id not in recipes:
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
        recipes[recipe_id]['type'] = recipe_type
        recipes[recipe_id]['output'] = output
        recipes[recipe_id]['ingredients'] = ingredients

        if save_recipes():
            messagebox.showinfo("Success", "Recipe updated successfully.")
            logging.info(f"Updated recipe with ID: {recipe_id}")
            self.update_recipe_list()

    def edit_selected_recipe(self):
        """Edit the selected recipe from the view tab."""
        selection = self.recipe_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a recipe to edit.")
            return

        recipe_id = self.recipe_listbox.get(selection[0])
        self.edit_recipe_var.set(recipe_id)
        self.load_recipe_for_edit()
        self.notebook.select(2)  # Switch to Edit tab

    def delete_recipe(self):
        """Delete the selected recipe."""
        selection = self.recipe_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a recipe to delete.")
            return

        recipe_id = self.recipe_listbox.get(selection[0])

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete recipe '{recipe_id}'?")
        if not confirm:
            return

        del recipes[recipe_id]
        if save_recipes():
            messagebox.showinfo("Success", "Recipe deleted successfully.")
            logging.info(f"Deleted recipe with ID: {recipe_id}")
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

        for recipe_id, recipe in recipes.items():
            # Search in recipe ID
            if search_term in recipe_id.lower():
                found = True
                self.search_results.insert(tk.END, f"Recipe ID: {recipe_id}\n")
                self.search_results.insert(tk.END, json.dumps(recipe, indent=4) + "\n")
                self.search_results.insert(tk.END, "-" * 30 + "\n")
                continue

            # Search in recipe content
            recipe_str = json.dumps(recipe).lower()
            if search_term in recipe_str:
                found = True
                self.search_results.insert(tk.END, f"Recipe ID: {recipe_id}\n")
                self.search_results.insert(tk.END, json.dumps(recipe, indent=4) + "\n")
                self.search_results.insert(tk.END, "-" * 30 + "\n")

        if not found:
            self.search_results.insert(tk.END, f"No recipes found matching '{search_term}'.")
        else:
            logging.info(f"Searched for recipes with term: {search_term}")

        self.search_results.config(state=tk.DISABLED)

    def export_recipes(self):
        """Export recipes to a different file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Recipes"
        )

        if not filename:
            return

        try:
            with open(filename, 'w') as file:
                json.dump(recipes, file, indent=4)

            messagebox.showinfo("Success", f"Recipes exported successfully to {filename}.")
            logging.info(f"Exported recipes to {filename}")
        except Exception as e:
            logging.error(f"Error exporting recipes: {str(e)}")
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
        logging.error("Attempted to run GUI mode but Tkinter is not available")
        return

    try:
        root = tk.Tk()
        app = RecipeManagerApp(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Unhandled exception in GUI mode: {str(e)}")
        if TKINTER_AVAILABLE:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        else:
            print(f"An unexpected error occurred: {str(e)}")

def main() -> None:
    """Main function to run the KubeJS Recipe Manager."""
    parser = argparse.ArgumentParser(description='KubeJS Recipe Manager')
    parser.add_argument('--gui', action='store_true', help='Run in GUI mode')
    args = parser.parse_args()

    if args.gui:
        run_gui()
    else:
        run_cli()

if __name__ == "__main__":
    try:
        logging.info("Application started")
        main()
    except KeyboardInterrupt:
        logging.info("Application terminated by user (KeyboardInterrupt)")
        print("\nApplication terminated by user.")
    except Exception as e:
        logging.critical(f"Unhandled exception: {str(e)}")
        print(f"An unexpected error occurred: {str(e)}")
