# automation/catalog.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_catalog_product(driver, product_name, timeout=15):
    try:
        # Navigate directly to the catalog page
        driver.get("https://peak.backoffice.dutchie.com/products/catalog")
        time.sleep(2)

        # Search input
        search_input_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div/div[1]/div/input"
        search_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, search_input_xpath))
        )
        search_input.clear()
        search_input.send_keys(product_name)
        search_input.send_keys(Keys.ENTER)
        time.sleep(3)

        # Wait for first row
        row_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[2]/div/div/div[1]/div[1]"
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, row_xpath))
        )
        row = driver.find_element(By.XPATH, row_xpath)

        product_data = {
            'Product Name': row.find_element(By.XPATH, './div[2]/div').text.strip(),
            'Category Name': row.find_element(By.XPATH, './div[3]/div').text.strip(),
            'Vendor Name': row.find_element(By.XPATH, './div[4]/div').text.strip(),
            'SKU': row.find_element(By.XPATH, './div[5]/div').text.strip(),
            'Rec Price': row.find_element(By.XPATH, './div[8]/div').text.strip(),
            'Measurement Type': row.find_element(By.XPATH, './div[9]/div').text.strip()
        }

        return product_data

    except Exception as e:
        print(f"[Catalog Search] No match for '{product_name}': {e}")
        return None
