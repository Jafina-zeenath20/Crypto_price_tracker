# crypto_tracker.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
from datetime import datetime
import os
import time

def create_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        # For recent Chrome versions: "--headless=new" works; fallback to "--headless" if needed
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_top_coins(driver, top_n=10):
    url = "https://coinmarketcap.com/"
    driver.get(url)

    wait = WebDriverWait(driver, 20)
    # wait until table rows appear (try a few common locators)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.cmc-table-row, tbody tr")))

    # try common row selector used by many scrapers
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.cmc-table-row")
    if not rows:
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    results = []
    for row in rows[:top_n]:
        # try robust extraction with multiple fallbacks
        try:
            # Attempt selector-based extraction first (better when class names exist)
            name = ""
            try:
                name = row.find_element(By.CSS_SELECTOR, "a.cmc-table__column-name--name, a.cmc-link").text
            except:
                # fallback: get the first link text in row
                try:
                    name = row.find_element(By.TAG_NAME, "a").text
                except:
                    name = ""

            price = ""
            try:
                price = row.find_element(By.CSS_SELECTOR, "td.cmc-table__cell--sort-by__price, td[class*='price']").text
            except:
                # fallback: search for a cell containing '$'
                tds = row.find_elements(By.TAG_NAME, "td")
                for td in tds:
                    t = td.text.strip()
                    if t.startswith("$") or "$" in t:
                        price = t
                        break

            change_24h = ""
            try:
                change_24h = row.find_element(By.CSS_SELECTOR,
                    "td.cmc-table__cell--sort-by__percent-change-24-h, td[data-sort*='percent']").text
            except:
                # fallback: pick first cell that contains '%' sign
                tds = row.find_elements(By.TAG_NAME, "td")
                for td in tds:
                    if "%" in td.text:
                        change_24h = td.text.strip()
                        break

            market_cap = ""
            try:
                market_cap = row.find_element(By.CSS_SELECTOR, "td.cmc-table__cell--sort-by__market-cap").text
            except:
                # fallback: often market cap is in a later td (index 6 or 7)
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) > 6:
                    market_cap = tds[6].text.strip()

            results.append({
                "timestamp": datetime.utcnow().isoformat(),
                "name": name,
                "price": price,
                "change_24h": change_24h,
                "market_cap": market_cap
            })
        except Exception as e:
            # skip row on unexpected error but continue
            print("row parse error:", e)
            continue

    return results

def save_to_csv(data, filename="crypto_prices.csv"):
    if not data:
        return
    df = pd.DataFrame(data)
    file_exists = os.path.isfile(filename)
    df.to_csv(filename, mode="a", header=not file_exists, index=False)

def main():
    driver = create_driver(headless=True)
    try:
        data = scrape_top_coins(driver, top_n=10)
        save_to_csv(data)
        print(f"Saved {len(data)} rows to CSV.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()