from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

print("\nFetching Nike deals...\n")
nike_deals = get_nike_deals()

nike_style_map = {deal["style_id"]: deal for deal in nike_deals}

print("\nFetching Foot Locker deals...\n")
footlocker_deals = get_footlocker_deals()

# Compare deals and determine the lowest price (Nike vs Foot Locker)
for deal in footlocker_deals:
    style_id = deal["style_id"]
    if style_id in nike_style_map:
        nike_price = float(nike_style_map[style_id]["price"].replace("$", ""))
        footlocker_price = float(deal["price"].replace("$", ""))
        
        if footlocker_price < nike_price:
            print(f"🔥 Better Deal at Foot Locker: {deal['name']} - {deal['price']} ({deal['url']})")
        else:
            print(f"✅ Best Price at Nike: {nike_style_map[style_id]['name']} - {nike_style_map[style_id]['price']} ({nike_style_map[style_id]['url']})")
    else:
        print(f"🆕 New Deal (Foot Locker): {deal['name']} - {deal['price']} ({deal['url']})")

print("\n✅ Done fetching sneaker deals!\n")
