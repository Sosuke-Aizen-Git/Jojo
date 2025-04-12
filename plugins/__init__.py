import os
import importlib
from pyrogram import Client

# Function to load all plugins
def load_plugins(app: Client):
    """Load all plugin modules"""
    plugins_dir = os.path.dirname(__file__)
    plugins_path = os.path.realpath(plugins_dir)
    
    for filename in os.listdir(plugins_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove .py extension
            module_path = f"plugins.{module_name}"
            
            try:
                module = importlib.import_module(module_path)
                print(f"Loaded plugin: {module_name}")
            except Exception as e:
                print(f"Failed to load plugin {module_name}: {e}")
