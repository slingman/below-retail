from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    deals = scrape_nike_air_max_1()
    print("\nFinal Nike Air Max 1 Deals:\n")

    if not deals:
        print("No deals found.")
        return

    for deal in deals:
        line = f"- {deal['title']} ({deal['style']}) — "
        if deal['sale_price']:
            line += f"SALE: {deal['sale_price']} (was {deal['price']})"
        else:
            line += f"{deal['price']}"
        line += f" → {deal['url']}"
        print(line)

    print("\nSummary:")
    print(f"  Total unique products: {len(deals)}")
    print(f"  Variants on sale: {sum(1 for d in deals if d['sale_price'])}")

if __name__ == "__main__":
    main()
