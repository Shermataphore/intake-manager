# automation/add_product.py
"""
Add a new Cannabis Flower product to Dutchie’s product catalog.
"""
import sys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from automation.login import login_to_dutchie

# URLs and XPaths
NEW_PRODUCT_URL = "https://peak.backoffice.dutchie.com/products/catalog/newProduct"
HEADER_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/header/div[1]/div/h1"

NAME_INPUT_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div/div/input"
GENERATE_SKU_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/div/div/div/button"

CATEGORY_DROPDOWN_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[5]/div/div"
CATEGORY_OPTION_XPATH = "/html/body/div[3]/div[3]/ul/li[2]"  # Cannabis Flower

EXTERNAL_CAT_DROPDOWN_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[6]/div/div"
EXTERNAL_CAT_OPTION_XPATH = "/html/body/div[3]/div[3]/ul/li[2]"  # Buds by Strain

TYPE_DROPDOWN_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[8]/div/div"
TYPE_OPTION_XPATH = "/html/body/div[3]/div[3]/ul/li[2]"  # Weight

UNIT_DROPDOWN_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[9]/div/div"
UNIT_OPTION_XPATH = "/html/body/div[3]/div[3]/ul/li[1]"  # Gram

RETAIL_INPUT_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[14]/div/div/input"
COST_INPUT_XPATH   = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[18]/div/div/input"

STRAIN_DROPDOWN_XPATH     = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[22]/div/div/div"
STRAIN_OPTION_XPATH       = "/html/body/div[3]/div/div[2]/div/div/div/ul/li[1]/div/div"

VENDOR_DROPDOWN_XPATH     = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[23]/div/div"
VENDOR_OPTION_XPATH       = "/html/body/div[3]/div/div[2]/div/div/div/ul/li[1]"

PRICING_TIER_DROPDOWN_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[33]/div/div/div/svg"
PRICING_TIER_OPTION_XPATH   = "/html/body/div[3]/div/div[2]/div/div/div/ul/li[3]/div/div/span"

SAVE_BUTTON_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div/button"


def add_cannabis_flower_product(driver, product_name, retail_price, cost_price, strain_name, vendor_name, timeout=15):
    """
    Create a new Cannabis Flower product in Dutchie.
    """
    # 1) Navigate to New Product page
    driver.get(NEW_PRODUCT_URL)
    WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element((By.XPATH, HEADER_XPATH), "New Product")
    )
    time.sleep(1)

    # 2) Fill product name & generate SKU
    driver.find_element(By.XPATH, NAME_INPUT_XPATH).send_keys(product_name)
    driver.find_element(By.XPATH, GENERATE_SKU_XPATH).click()
    time.sleep(1)

    # 3) Select Category
    driver.find_element(By.XPATH, CATEGORY_DROPDOWN_XPATH).click()
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, CATEGORY_OPTION_XPATH))
    ).click()
    time.sleep(0.5)

    # 4) Select External Category
    driver.find_element(By.XPATH, EXTERNAL_CAT_DROPDOWN_XPATH).click()
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, EXTERNAL_CAT_OPTION_XPATH))
    ).click()
    time.sleep(0.5)

    # 5) Select Type
    driver.find_element(By.XPATH, TYPE_DROPDOWN_XPATH).click()
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, TYPE_OPTION_XPATH))
    ).click()
    time.sleep(0.5)

    # 6) Select Unit
    driver.find_element(By.XPATH, UNIT_DROPDOWN_XPATH).click()
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, UNIT_OPTION_XPATH))
    ).click()
    time.sleep(0.5)

    # 7) Enter prices
    driver.find_element(By.XPATH, RETAIL_INPUT_XPATH).send_keys(str(retail_price))
    driver.find_element(By.XPATH, COST_INPUT_XPATH).send_keys(str(cost_price))
    time.sleep(0.5)

    # 8) Select Strain
    driver.find_element(By.XPATH, STRAIN_DROPDOWN_XPATH).click()
    time.sleep(0.5)
    search_box = driver.find_element(By.XPATH, STRAIN_DROPDOWN_XPATH + "/input")
    search_box.send_keys(strain_name)
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, STRAIN_OPTION_XPATH))
    ).click()
    time.sleep(0.5)

    # 9) Select Vendor
    driver.find_element(By.XPATH, VENDOR_DROPDOWN_XPATH).click()
    time.sleep(0.5)
    vendor_box = driver.find_element(By.XPATH, VENDOR_DROPDOWN_XPATH + "/input")
    vendor_box.send_keys(vendor_name)
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, VENDOR_OPTION_XPATH))
    ).click()
    time.sleep(0.5)

    # 10) Select Pricing Tier
    driver.find_element(By.XPATH, PRICING_TIER_DROPDOWN_XPATH).click()
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, PRICING_TIER_OPTION_XPATH))
    ).click()
    time.sleep(0.5)

    # 11) Save new product
    driver.find_element(By.XPATH, SAVE_BUTTON_XPATH).click()
    time.sleep(2)
    print(f"[Add Product] Created: {product_name}")


def main():
    if len(sys.argv) < 6:
        print("Usage: python add_product.py <name> <retail> <cost> <strain> <vendor>")
        sys.exit(1)
    name, retail, cost, strain, vendor = sys.argv[1:6]
    driver = login_to_dutchie()
    if not driver:
        print("Login failed.")
        sys.exit(1)
    add_cannabis_flower_product(driver, name, retail, cost, strain, vendor)
    driver.quit()

if __name__ == "__main__":
    main()

