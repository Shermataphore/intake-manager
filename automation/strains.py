# automation/strains.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def remove_banner(driver, max_attempts=3, delay=0.25):
    for attempt in range(max_attempts):
        try:
            banners = driver.find_elements(By.CSS_SELECTOR, "div.sc-cUPSFq")
            if banners:
                for banner in banners:
                    driver.execute_script("arguments[0].remove();", banner)
            else:
                break
        except Exception:
            pass
        time.sleep(delay)

def fill_strain_form(driver, strain, editing=False):
    name_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div[1]/div/div/input"
    desc_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/input"
    abbr_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div[3]/div/div/input"

    name_input = driver.find_element(By.XPATH, name_xpath)
    desc_input = driver.find_element(By.XPATH, desc_xpath)
    abbr_input = driver.find_element(By.XPATH, abbr_xpath)

    if editing:
        for element in [name_input, desc_input, abbr_input]:
            element.send_keys(Keys.BACKSPACE * 20)
    else:
        for element in [name_input, desc_input, abbr_input]:
            element.clear()

    name_input.send_keys(strain)
    time.sleep(0.25)
    desc_input.send_keys(strain)
    time.sleep(0.25)
    abbr_input.send_keys(strain)

def create_or_edit_strain(driver, strain_name: str):
    driver.get("https://peak.backoffice.dutchie.com/products/strains")
    time.sleep(1)
    remove_banner(driver)
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[1]/header/div/div/h1"),
            "Strains"
        )
    )

    # Enter strain in search
    search_box = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div/div[1]/div/input")
    search_box.send_keys(strain_name)
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div/button[2]").click()
    time.sleep(2)

    # Look for "No data available"
    no_data_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]/div/div/p[1]"
    no_data_elements = driver.find_elements(By.XPATH, no_data_xpath)

    if no_data_elements and no_data_elements[0].is_displayed() and no_data_elements[0].text.strip() == "No data available":
        print(f"Strain '{strain_name}' not found. Creating...")
        add_strain(driver, strain_name)
    else:
        print(f"Strain '{strain_name}' exists. Editing...")
        edit_strain(driver, strain_name)

def add_strain(driver, strain):
    add_button_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/header/div[2]/button[2]"
    driver.find_element(By.XPATH, add_button_xpath).click()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[1]/header/div/div/h1"), "Add strain"
        )
    )
    fill_strain_form(driver, strain, editing=False)
    save_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[1]/div/div/button"))
    )
    save_button.click()
    WebDriverWait(driver, 10).until_not(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[1]/div/div/button"))
    )
    print(f"[Strain] Created: {strain}")

def edit_strain(driver, strain):
    row_xpath = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[2]/div/div/div[1]"
    driver.find_element(By.XPATH, row_xpath).click()
    time.sleep(2)
    fill_strain_form(driver, strain, editing=True)
    save_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[1]/div/div/button"))
    )
    save_button.click()
    print(f"[Strain] Edited: {strain}")
