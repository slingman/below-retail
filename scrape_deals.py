from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding Nike Air Max 1 deals...\n")
    deals = scrape_nike_air_max_1()

    if not deals:
        print("No deals found.")
        return

    print("\nFinal Nike Air Max 1 Deals:\n")
    for deal in deals:
        print(f"{deal['title']} ({deal['style']})")
        print(f"  Current Price: {deal['price']}")
        if deal.get('original_price') and deal['original_price'] != deal['price']:
            print(f"  Original Price: {deal['original_price']}")
        if deal.get('discount_percent'):
            print(f"  Discount: {deal['discount_percent']} off")
        print(f"  URL: {deal['url']}\n")

    print("Summary:")
    print(f"  Total unique products: {len(deals)}")
    sale_count = sum(1 for deal in deals if deal.get('discount_percent'))
    print(f"  Variants on sale: {sale_count}")

if __name__ == "__main__":
    main()
