from playwright_test   import sync_playwright
import csv
import os
from datetime import datetime
import random
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

URL_BASE = "https://allegro.pl/kategoria/utrzymanie-czystosci-chemia-gospodarcza-317369"

def safe_goto(page, url, retries=3):
    for attempt in range(retries):
        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle")
            return True
        except:
            print(f"Błąd wejścia, próba {attempt+1}")
            time.sleep(random.randint(2, 5))
    return False


def human_delay(min_s=2, max_s=5):
    time.sleep(random.uniform(min_s, max_s))


def scrape_page(page, writer, data):
    
    page.mouse.wheel(0, random.randint(2000, 4000))
    human_delay(1, 2)

    products = page.locator("article")
    count = min(20, products.count())

    print(f"Znaleziono produktów: {count}")

    for i in range(count):
        product = products.nth(i)

        try:
            title = product.locator("h2 a").first

            nazwa = title.inner_text(timeout=2000)
            link = title.get_attribute("href")

            if not link:
                continue

            link = link.split("?")[0]

            if not ("allegro.pl/oferta" in link or "allegro.pl/produkt" in link):
                continue

            # cena
            price = product.locator('[aria-label*="cena"]')
            cena = price.first.inner_text() if price.count() > 0 else "brak"

            # kupiono
            kupily = product.locator('[aria-label*="kup"]')
            if kupily.count() > 0:
                text = kupily.first.get_attribute("aria-label")
                liczba = text.split(" ")[0]
            else:
                liczba = "0"

            writer.writerow([nazwa, cena, liczba, data, link])

        except:
            continue


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    page = context.new_page()

    file_exists = os.path.exists("produkty.csv")

    with open("produkty.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")

        if not file_exists:
            writer.writerow(["nazwa","cena","kupilo","data","link"])

        data = datetime.now().strftime("%Y-%m-%d")

       
        MAX_PAGES = 10

        for page_num in range(1, MAX_PAGES + 1):

            url = f"{URL_BASE}?p={page_num}"
            print(f"\n--- Strona {page_num} ---")

            if not safe_goto(page, url):
                continue

            human_delay(2, 4)

            scrape_page(page, writer, data)

            
            human_delay(3, 6)

    browser.close()

print("\n SCRAPING ZAKOŃCZONY")