import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from automation.login import login_to_dutchie

def scrape_receive_inventory(debug=False):
    driver = login_to_dutchie()
    if not driver:
        print("LOGIN FAILED")
        return

    # 1) Navigate
    url = "https://peak.backoffice.dutchie.com/products/inventory/receive-inventory"
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # 2) XPaths (tweak these if the structure shifts)
    dropdown_xpath  = "/html/body/div[1]/div/div[2]/div[2]/div[1]/section/article/div/div[2]/div[2]/div/div"
    list_item_xpath = "/html/body/div[3]/div[3]/ul/li"
    rows_xpath      = "/html/body/div[1]/div/div[2]/div[2]/div[1]/div[6]/div/div[2]/div[2]/div/div/div[1]/div"

    def open_and_fetch_items():
        # a) Click the dropdown
        dd = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
        try:
            dd.click()
        except Exception:
            # fallback if click is intercepted
            driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", dd)

        # b) Wait for the list items to appear
        wait.until(EC.visibility_of_any_elements_located((By.XPATH, list_item_xpath)))
        return driver.find_elements(By.XPATH, list_item_xpath)

    # 3) Prime the menu and grab all titles
    items = open_and_fetch_items()
    titles = [el.text.strip() for el in items]
    print(f"FOUND {len(titles)} manifests:")
    for i, t in enumerate(titles, 1):
        print(f"  {i}. {t!r}")

    if debug:
        driver.quit()
        return titles

    # 4) Loop through each option
    results = {}
    for idx, title in enumerate(titles, start=1):
        print(f"\n→ SELECTING #{idx}: {title}")
        items = open_and_fetch_items()
        if idx-1 >= len(items):
            print(f"  !! index {idx} out of range")
            break

        opt = items[idx-1]
        # ensure it's clickable
        wait.until(EC.element_to_be_clickable((By.XPATH, f"({list_item_xpath})[{idx}]")))
        try:
            opt.click()
        except Exception:
            # JS fallback
            driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", opt)

        # 5) Wait for the table to render
        try:
            wait.until(EC.presence_of_all_elements_located((By.XPATH, rows_xpath)))
        except TimeoutException:
            print("  !! table rows never appeared")
            continue

        # 6) Scrape rows
        rows = driver.find_elements(By.XPATH, rows_xpath)
        data = []
        for r in rows:
            cells = r.find_elements(By.XPATH, "./div")
            data.append({
                "name": cells[1].text.strip(),
                "qty":  cells[3].text.strip(),
                "unit": cells[4].text.strip(),
                "cost": cells[9].text.strip(),
                "rec":  cells[11].text.strip(),
            })
        results[title] = data

        # 7) Close the pop‑up (ESC)
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.3)

    driver.quit()
    return results

if __name__ == "__main__":
    out = scrape_receive_inventory(debug=False)
    print(out)
