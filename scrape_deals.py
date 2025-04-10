# scrape_deals.py

from scrapers.sneakers.nike import scrape_nike_air_max_1
import pandas as pd
import os
from datetime import datetime

def main():
    print("Finding Nike Air Max 1 deals...\n")

    deals = scrape_nike_air_max_1()

    print("\nFinal Nike Air Max 1 Deals:\n")

    sorted_deals = sorted(deals, key=lambda x: x["discount_pct"], reverse=True)
    air_max_1_only = [d for d in sorted_deals if "air max 1" in d["title"].lower()]

    for deal in air_max_1_only:
        print(f"{deal['title']} ({deal['style_id']})")
        print(f"  Current Price: ${deal['current_price']}")
        if deal['original_price'] and deal['original_price'] != deal['current_price']:
            print(f"  Original Price: ${deal['original_price']}")
            print(f"  Discount: {deal['discount_pct']}% off")
        print(f"  URL: {deal['url']}\n")

    # Export to CSV
    if air_max_1_only:
        df = pd.DataFrame(air_max_1_only)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"air_max_1_deals_{timestamp}.csv"
        export_path = os.path.join("exports", filename)

        os.makedirs("exports", exist_ok=True)
        df.to_csv(export_path, index=False)
        print(f"✅ Exported to {export_path}")

    print("Summary:")
    print(f"  Total unique products: {len(air_max_1_only)}")
    print(f"  Variants on sale: {sum(1 for d in air_max_1_only if d['discount_pct'] > 0)}")

if __name__ == "__main__":
    main()
