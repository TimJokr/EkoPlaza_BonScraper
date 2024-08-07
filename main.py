import time
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

import config
site_base = "https://www.ekoplaza.nl/nl"
site_orders = site_base + "/account/orders"
site_transaction = site_orders + "/history/transaction/"

options = FirefoxOptions()
options.add_argument("--headless=new")
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(5)
wait = WebDriverWait(driver, 5)
driver.maximize_window()
print("Driver initiated")

driver.get(site_base)
print("Site opened")

# Decline cookie
try:
    cookie_decline = wait.until(EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline")))
    cookie_decline.location_once_scrolled_into_view
    time.sleep(0.5)
    cookie_decline.click()
    print("Cookies denied")
except TimeoutException:
    print("No cookie popup")

# Click "Log in"
login = driver.find_element(By.ID, "user-dropdown")
login.click()
print("Login button clicked")
time.sleep(3)

# Find the fields
email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[id*=login-email]")))
password_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[id^=Wachtwoord-]")))
login_submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-success:nth-child(1)")))
print("Fields found")

# Click email field and fill in email
email_field.click()
email_field.clear()
email_field.send_keys(config.email)
print("Email filled in")

# Click password field and fill in password
password_field.click()
password_field.clear()
password_field.send_keys(config.password)
print("Password filled in")

# Click login
login_submit.click()
print("Login submitted")
time.sleep(1)

# Go to the order history
driver.get(site_orders)
print("Orders opened")
time.sleep(1)

# Expand all transactions
while True:
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".loadmore-btn"))).click()
        print("Clicked 'Meer'")
    except TimeoutException or StaleElementReferenceException:
        print("No 'Meer' button anymore")
        break

transaction_links = driver.find_elements(By.XPATH, "//ul[@class='list-unstyled']/li/a")
transaction_numbers_retrieved = [transaction_link.get_attribute("href").removeprefix(site_transaction) for transaction_link in transaction_links]
# transaction_numbers_retrieved = [transaction_link.text for transaction_link in transaction_links]
print("Order numbers retrieved")
# print(order_numbers_retrieved)
# np.savetxt('order_numbers.txt', order_numbers_retrieved)


order_date = list() 
order_number = list() 
order_price = list()
order_location = list()
order_items_info = list()
order_items_name = list()
order_items_price = list()
order_items_amount = list()

for transaction_number in transaction_numbers_retrieved:        # Each order; td doesnt work for single number
    driver.get(site_transaction + transaction_number)

    order_items = driver.find_elements(By.XPATH, "//div[@class='cart-list__info']")
    order_items_info.extend([order_item.text for order_item in order_items])
    order_items_name.extend([order_item_info.splitlines()[0] for order_item_info in order_items_info])
    order_items_amount.extend([order_item_info.splitlines()[1].split(')')[1].strip() for order_item_info in order_items_info])

    number_of_items = len(order_items)

    order_summary = driver.find_elements(By.XPATH, "//div[@class='order-summary__text']/p")
    order_date.extend([order_summary[0].text] * number_of_items)
    order_number.extend([order_summary[1].text] * number_of_items)
    order_price.extend([order_summary[2].text.split(' - ')[0]] * number_of_items)
    order_location.extend([order_summary[2].text.split(' - ')[1]]  * number_of_items)

    time.sleep(10)

    a = pd.DataFrame({'date': order_date, 'number': order_number, 'location': order_location, 'name': order_items_name, 'price': order_items_price, 'amount': order_items_amount})
    print(a)

    time.sleep(10)


time.sleep(100)
driver.delete_all_cookies()
driver.quit()