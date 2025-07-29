# automation/login.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secrets import username, password  # Loaded from .env

def login_to_dutchie():
    driver = webdriver.Chrome()
    driver.get("https://peak.backoffice.dutchie.com/")

    try:
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "input-input_"))
        )
        username_input.send_keys(username)

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)

        time.sleep(10)  # Wait for post-login navigation
        return driver  # Keep driver open for next tasks

    except Exception as e:
        print(f"Login failed: {e}")
        driver.quit()
        return None
