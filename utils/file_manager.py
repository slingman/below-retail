import json

def save_deals_to_json(price_comparison, filename="deals.json"):
    """Saves scraped deals to a JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(price_comparison, f, indent=4)
        print(f"✅ Saved {len(price_comparison)} products to {filename}!")
    except Exception as e:
        print(f"❌ Error saving deals: {e}")

def load_deals_from_json(filename="deals.json"):
    """Loads deals from a JSON file."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ No existing deals file found.")
        return {}

