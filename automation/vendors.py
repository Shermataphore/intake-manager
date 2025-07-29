# automation/vendors.py
"""
Search and create vendors in Dutchie Backoffice.
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from automation.login import login_to_dutchie

VENDOR_PAGE_URL = "https://peak.backoffice.dutchie.com/products/vendors"

# XPaths
HEADER_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/header/div[1]/div/h1"
SEARCH_INPUT_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div/div[1]/div/input"
ROWS_BASE_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[2]/div/div/div[1]"
ADD_BUTTON_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/header/div[2]/button[2]"
ADD_HEADER_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div/h1"
NEW_NAME_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[1]/div/div/input"
NEW_LICENSE_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div/div/input"
SAVE_BUTTON_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/button"


def search_vendor(driver, vendor_name, timeout=15):
    """
    Search the vendor table for rows matching `vendor_name`.
    Returns a list of dicts: {'name': ..., 'license': ...}.
    """
    driver.get(VENDOR_PAGE_URL)
    # Wait for page header
    WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element((By.XPATH, HEADER_XPATH), "Vendors")
    )
    time.sleep(1)

    # Enter search
    search_input = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, SEARCH_INPUT_XPATH))
    )
    search_input.clear()
    search_input.send_keys(vendor_name)
    search_input.send_keys(Keys.ENTER)
    time.sleep(2)

    # Collect rows
    rows = driver.find_elements(By.XPATH, ROWS_BASE_XPATH + "/div")
    results = []
    for idx in range(1, len(rows) + 1):
        row_xpath = f"{ROWS_BASE_XPATH}/div[{idx}]"
        try:
            name = driver.find_element(By.XPATH, row_xpath + "/div[1]/div").text.strip()
        except:
            name = ""
        try:
            license_num = driver.find_element(By.XPATH, row_xpath + "/div[2]/div").text.strip()
        except:
            license_num = ""
        results.append({'name': name, 'license': license_num})
    return results


def create_vendor(driver, vendor_name, license_number, timeout=15):
    """
    Create a new vendor with the given name and license number.
    """
    # Navigate and click Add Vendor
    driver.get(VENDOR_PAGE_URL)
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, ADD_BUTTON_XPATH))
    ).click()
    # Wait for 'Add vendor' header
    WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element((By.XPATH, ADD_HEADER_XPATH), "Add vendor")
    )
    time.sleep(1)

    # Fill form
    name_input = driver.find_element(By.XPATH, NEW_NAME_XPATH)
    license_input = driver.find_element(By.XPATH, NEW_LICENSE_XPATH)
    name_input.clear()
    name_input.send_keys(vendor_name)
    license_input.clear()
    license_input.send_keys(license_number)
    time.sleep(2)

    # Save
    save_btn = driver.find_element(By.XPATH, SAVE_BUTTON_XPATH)
    save_btn.click()
    # Wait for redirect back to vendor page
    time.sleep(3)
    WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element((By.XPATH, HEADER_XPATH), "Vendors")
    )
    print(f"[Vendors] Created: {vendor_name} ({license_number})")


def upsert_vendor(vendor_name, license_number):
    """
    Log in, search for vendor_name, create if not found.
    """
    driver = login_to_dutchie()
    if not driver:
        print("[Vendors] Login failed.")
        return
    existing = search_vendor(driver, vendor_name)
    matches = [v for v in existing if v['name'].lower() == vendor_name.lower()]
    if matches:
        print(f"[Vendors] Found existing: {matches}")
    else:
        create_vendor(driver, vendor_name, license_number)
    driver.quit()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python vendors.py <Vendor Name> <License Number>")
        sys.exit(1)
    name, lic = sys.argv[1], sys.argv[2]
    upsert_vendor(name, lic)
