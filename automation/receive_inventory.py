# automation/receive_inventory.py
"""Scrape Dutchie's 'Receive Inventory' manifests and their product details."""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.login import login_to_dutchie


def scrape_receive_inventory():
    """Log in and scrape Receive Inventory manifests and their products."""
    # 1) Log in and get Selenium driver
    driver = login_to_dutchie()
    if not driver:
        print("[Receive Inventory] Login failed.")
        return {}

    # 2) Navigate to Receive Inventory page
    url = "https://peak.backoffice.dutchie.com/products/inventory/receive-inventory"
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div/h1"),
            "Receive Inventory"
        )
    )
    time.sleep(1)

    # 3) Open manifest dropdown
    dropdown_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/section/article/div/div[2]/div[2]/div/div"
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
    ).click()
    time.sleep(1)

    # 4) Collect manifest entries
    list_item_xpath = "/html/body/div[3]/div[3]/ul/li"
    manifest_elements = driver.find_elements(By.XPATH, list_item_xpath)
    manifest_titles = [el.text.strip() for el in manifest_elements]

    results = {}
    total = len(manifest_titles)
    for idx, title in enumerate(manifest_titles, start=1):
        print(f"[Scraping {idx}/{total}] {title}")
        # a) Re-open dropdown and select this manifest
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
        ).click()
        time.sleep(0.5)
        option_xpath = f"/html/body/div[3]/div[3]/ul/li[{idx}]"
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        ).click()
        time.sleep(1)

        # b) Scrape product rows
        rows_base = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[6]/div/div[2]/div[2]/div/div/div[1]"
        rows = driver.find_elements(By.XPATH, rows_base + "/div")
        items = []
        for i in range(1, len(rows) + 1):
            row_xpath = f"{rows_base}/div[{i}]"
            name = driver.find_element(By.XPATH, row_xpath + "/div[2]/div").text.strip()
            qty = driver.find_element(By.XPATH, row_xpath + "/div[4]/div").text.strip()
            unit = driver.find_element(By.XPATH, row_xpath + "/div[5]/div").text.strip()
            cost = driver.find_element(By.XPATH, row_xpath + "/div[10]/div").text.strip()
            rec_price = driver.find_element(By.XPATH, row_xpath + "/div[12]/div").text.strip()
            items.append({
                'name': name,
                'quantity': qty,
                'unit': unit,
                'cost': cost,
                'rec_price': rec_price
            })

        results[title] = items

    # 5) Clean up and return results
    driver.quit()
    return results


if __name__ == "__main__":
    data = scrape_receive_inventory()
    for title, items in data.items():
        print(f"\nManifest: {title}")
        for item in items:
            print(f"  - {item}")

