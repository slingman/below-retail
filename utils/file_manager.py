import json
import os

def save_deals(deals, filename="deals.json"):
    """
    Save the collected sneaker deals to a JSON file.
    
    Args:
        deals (dict): Dictionary of deals with style IDs as keys.
        filename (str): The filename to save the data.
    """
    try:
        with open(filename, "w") as file:
            json.dump(deals, file, indent=4)
        print(f"✅ Deals successfully saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving deals: {e}")

def load_deals(filename="deals.json"):
    """
    Load sneaker deals from a JSON file.

    Args:
        filename (str): The filename to load the data from.

    Returns:
        dict: Loaded deals data or an empty dictionary if the file doesn't exist.
    """
    if not os.path.exists(filename):
        return {}

    try:
        with open(filename, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ Error loading deals: {e}")
        return {}
