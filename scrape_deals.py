from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding Nike Air Max 1 deals...\n")
    deals = scrape_nike_air_max_1()

    print("\nFinal Nike Air Max 1 Deals:\n")
    for deal in deals:
        try:
            line = f"{deal['title']} - {deal['style_id']} - "
            if deal.get('sale_price'):
                line += f"SALE ${deal['sale_price']} (was ${deal['price']})"
            else:
                line += f"${deal['price']}"
            print(line)
        except KeyError as e:
            print(f"Skipping deal due to missing key: {e}")

    print("\nSummary:")
    print(f"  Total unique products: {len(deals)}")
    print(f"  Variants on sale: {sum(1 for d in deals if d.get('sale_price'))}")

if __name__ == "__main__":
    main()
