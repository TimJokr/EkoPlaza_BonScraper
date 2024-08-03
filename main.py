import time
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

import config
email = config.email
password = config.password
abs_path_login = "/html[1]/body[1]/div[1]/div[1]/div[1]/header[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/form[1]/fieldset[1]/div[1]/"

options = FirefoxOptions()
options.add_argument("--headless=new")

driver = webdriver.Firefox(options=options)
driver.implicitly_wait(5)
driver.get("https://www.ekoplaza.nl/")
time.sleep(1)   # Wait for page to load

# Click "Log in"
login = driver.find_element(By.ID, "user-dropdown")
login.click()
time.sleep(3)

# Find the fields
email_field = driver.find_element(By.XPATH, abs_path_login + "div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]")
password_field = driver.find_element(By.XPATH, abs_path_login + "div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]")
login_submit = driver.find_element(By.XPATH, abs_path_login + "div[2]/div[1]/button[1]")

# Click email field and fill in email
email_field.click()
time.sleep(0.5)
email_field.clear()
email_field.send_keys(email)
time.sleep(0.5)

# Click password field and fill in password
password_field.click()
time.sleep(0.5)
password_field.clear()
password_field.send_keys(password)
time.sleep(0.5)

# Click login
login_submit.click()
time.sleep(1)

driver.get("https://www.ekoplaza.nl/nl/account/orders")

time.sleep(2)

driver.quit()