import requests
from bs4 import BeautifulSoup
import json
import time

CATEGORY_URLS = [
    "https://www.mega.pk/mobiles/4/",
    "https://www.mega.pk/bluetoothhandfree/",
    "https://www.mega.pk/watches/",
    "https://www.mega.pk/trimmer/",
    "https://www.mega.pk/powerbank/",
    "https://www.mega.pk/mobilecables/",
    "https://www.mega.pk/mobilespeakers/",
    "https://www.mega.pk/multimediatablets/",
    "https://www.mega.pk/laptop-price-pakistan/"
]

def get_category_from_url(url):
    parts = url.strip("/").split("/")
    for part in reversed(parts):
        if not part.isdigit() and part != "":
            return part
    return "unknown"


def scrape_megaPK_all_categories(max_pages=2):
    all_products = []

    for base_url in CATEGORY_URLS:
        category = get_category_from_url(base_url)
        print(f"\n Scraping category: {category}")

        if category == "mobiles":
           max_pages = 4
        elif category == "bluetoothhandfree":
           max_pages = 2
        elif category == "watches":
           max_pages = 2
        elif category == "mobilecables ":
            max_pages = 2
        elif category == "multimediatablets":
            max_pages = 3
        elif category == "laptop-price-pakistan":
            max_pages = 8
        elif category == "powerbank":
            max_pages = 1
        elif category == "trimmer":
            max_pages = 1
        else:
            max_pages = 1    

        for page in range(1, max_pages + 1):
            url = f"{base_url}?page={page}"
            print(f"   Page {page}: {url}")
            response = requests.get(url)

            if response.status_code != 200:
                print("   Failed to load this page.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

           
            product_cards = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-4 col-lg-3')


            if not product_cards:
                print("   No more products. Moving to next category.")
                break

            for card in product_cards:
              try:
                img_tag = card.find('img')
                image_url = img_tag['src'] if img_tag else None

                title_div = card.find('div', id='lap_name_div')
                title_tag = title_div.find('a') if title_div else None
                title = title_tag.text.strip() if title_tag else "N/A"
                product_url = title_tag['href'] if title_tag and title_tag.has_attr('href') else None

                price_tag = card.find('div', class_='cat_price')
                price_text = price_tag.get_text(strip=True).replace("Rs", "").replace(",", "") if price_tag else "N/A"

                all_products.append({
                     "category": category,
                     "title": title,
                     "price": price_text,
                    "image_url": image_url,
                    "product_url": product_url
                    })

              except Exception as e:
               print(f"   Error parsing product: {e}")


            time.sleep(1)  

    print(f"\n Total products scraped: {len(all_products)}")
    print("\n Sample scraped data:")
    for product in all_products[:5]:  # show only first 5 products
      print(json.dumps(product, indent=2, ensure_ascii=False))
    # Save all products to a JSON file
    with open('megaPK_products.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=4, ensure_ascii=False)

    print(" Data saved to priceoye_products.json")

if __name__ == "__main__":
    scrape_megaPK_all_categories()