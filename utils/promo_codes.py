import re

def apply_promo_code(price, promo_text):
    """Applies promo code discount if applicable and returns the new 
price."""
    try:
        if not promo_text:
            return price, None  # No promo available

        # Check for percentage discount
        percent_match = re.search(r"(\d+)% off", promo_text)
        if percent_match:
            discount = float(percent_match.group(1))
            return round(price * (1 - discount / 100), 2), f"{discount}% OFF"

        # Check for fixed amount discount
        amount_match = re.search(r"\$([\d.]+) off", promo_text)
        if amount_match:
            discount = float(amount_match.group(1))
            return max(price - discount, 0), f"${discount} OFF"

    except Exception as e:
        print(f"⚠️ Error applying promo code: {e}")

    return price, None

