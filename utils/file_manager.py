import json

def save_deals(deals, filename="deals.json"):
    """
    Saves scraped deals to a JSON file.
    
    Ensures data is structured as a dictionary with style_id as keys.
    """
    structured_deals = {}
    
    for deal in deals:
        style_id = deal.get("style_id")
        if style_id:
            structured_deals[style_id] = deal  # Save by style_id as key
        else:
            print(f"⚠️ Warning: Missing style_id for {deal.get('name', 'Unknown Product')}, skipping.")

    with open(filename, "w") as f:
        json.dump(structured_deals, f, indent=4)

    print(f"\n✅ Deals successfully saved to {filename}")
