# automation/catalog_search.py
"""
Search Dutchie's product catalog for a given term and return all matching rows.
"""
import sys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.login import login_to_dutchie


def search_catalog(product_name, timeout=15):
    """
    Log into Dutchie, navigate to the Catalog page, search for `product_name`,
    and return a list of dicts for every matching row.
    """
    driver = login_to_dutchie()
    if not driver:
        print("[Catalog Search] Login failed.")
        return []

    # 1) Go to catalog
    driver.get("https://peak.backoffice.dutchie.com/products/catalog")
    # Wait for header 'Catalog'
    header_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/header/div[1]/div/h1"
    WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element((By.XPATH, header_xpath), "Catalog")
    )

    # 2) Enter search term
    search_input_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div/div[1]/div/input"
    search_input = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, search_input_xpath))
    )
    search_input.clear()
    search_input.send_keys(product_name)
    search_input.send_keys(Keys.ENTER)
    time.sleep(2)

    # 3) Locate table rows
    rows_base = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[2]/div/div/div[1]"
    rows = driver.find_elements(By.XPATH, rows_base + "/div")

    results = []
    for i in range(1, len(rows) + 1):
        row_xpath = f"{rows_base}/div[{i}]"
        try:
            name = driver.find_element(By.XPATH, row_xpath + "/div[2]/div").text.strip()
            category = driver.find_element(By.XPATH, row_xpath + "/div[3]/div").text.strip()
            vendor = driver.find_element(By.XPATH, row_xpath + "/div[4]/div").text.strip()
            rec_price = driver.find_element(By.XPATH, row_xpath + "/div[6]/div").text.strip()
            strain_name = driver.find_element(By.XPATH, row_xpath + "/div[10]/div").text.strip()
            cost = driver.find_element(By.XPATH, row_xpath + "/div[11]/div").text.strip()
        except Exception as e:
            print(f"[Catalog Search] Skipping row {i} due to error: {e}")
            continue

        results.append({
            "product_name": name,
            "category": category,
            "vendor": vendor,
            "rec_price": rec_price,
            "strain_name": strain_name,
            "cost": cost
        })

    driver.quit()
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python catalog_search.py <search_term>")
        sys.exit(1)

    term = sys.argv[1]
    matches = search_catalog(term)
    if not matches:
        print(f"No matches found for '{term}'.")
    else:
        print(f"Found {len(matches)} matches for '{term}':")
        for m in matches:
            print(m)
