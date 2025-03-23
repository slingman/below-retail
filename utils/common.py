import re

def extract_price(text):
    """
    Extract a float price from a string like "$109.97" or "Now: $79.99".
    Returns None if no price is found.
    """
    if not text:
        return None
    match = re.search(r'\$?(\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{2})?', text.replace(',', ''))
    return float(match.group(0).replace('$', '')) if match else None
