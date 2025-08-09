import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

# 1. Log in
driver.get("http://127.0.0.1:8000/login/")
driver.find_element(By.NAME, "username").send_keys("")
driver.find_element(By.NAME, "password").send_keys("your_password")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


# 2. Wait until login is successful and Add Participant page is available
WebDriverWait(driver, 10).until(EC.url_changes(" "))
driver.get("http://127.0.0.1:8000/add-participants/")


# 3. Fill in the participant form
driver.find_element(By.NAME, "first_name").send_keys("Jim")
time.sleep(0.5)

driver.find_element(By.NAME, "last_name").send_keys("Doe")
time.sleep(0.5)

driver.find_element(By.NAME, "ppsn").send_keys("8234567A")
time.sleep(0.5)

Select(driver.find_element(By.NAME, "department")).select_by_index(1)  # assumes at least 1 real dept exists
time.sleep(0.5)

driver.find_element(By.NAME, "address").send_keys("123 Test Street")
time.sleep(0.5)

driver.find_element(By.NAME, "birth_date").send_keys("01/01/1990")
time.sleep(0.5)

driver.find_element(By.NAME, "scheme_start_date").send_keys("01/09/2024")
time.sleep(0.5)

driver.find_element(By.NAME, "phone").send_keys("0871234567")
time.sleep(0.5)

driver.find_element(By.NAME, "email").send_keys("joejoe@example.com")
time.sleep(0.5)

driver.find_element(By.NAME, "emerg_phone").send_keys("0877654321")
time.sleep(0.5)

driver.find_element(By.NAME, "manual_start_date").send_keys("01/10/2024")
time.sleep(0.5)

driver.find_element(By.NAME, "bank_iban").send_keys("IE29AIBK93195212345678")
time.sleep(0.5)

# Wait 1 seconds before submitting
time.sleep(1)

driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

# Optional: pause before closing
time.sleep(2)

driver.quit()
