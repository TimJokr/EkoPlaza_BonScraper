import time
import locale
from datetime import datetime, date
import numpy as np
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
# options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(5)
wait = WebDriverWait(driver, 5)
wait_long = WebDriverWait(driver, 30)
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
    except (TimeoutException, StaleElementReferenceException):
        print("No 'Meer' button anymore")
        break

transaction_numbers = [elem.get_attribute("href").removeprefix(site_transaction) for elem in driver.find_elements(By.XPATH, "//ul[@class='list-unstyled']/li/a")][:5]
transaction_dates = [elem.text.split(" - ")[1] for elem in driver.find_elements(By.XPATH, "//ul[@class='list-unstyled']/li/a/div/p[@class='title']")][:5]

locale.setlocale(locale.LC_ALL, 'nl_NL')
transaction_dates[transaction_dates == "Vandaag"] = date.today().strftime(r'%d %B %Y')
transaction_dates = [datetime.strptime(date, r'%d %B %Y').strftime(r'%d/%m/%Y') for date in transaction_dates]
print("Order numbers retrieved")
# np.savetxt('order_numbers.txt', order_numbers_retrieved)

order_items_name = list()
order_items_price = list()
order_items_amount_unit = list()
order_items_amount_number = list()
order_transaction_numbers = list()

transaction_order_numbers = list() 
transaction_prices = list()
transaction_locations = list()

for transaction_number in transaction_numbers:        # Each order; td doesnt work for single number
    driver.get(site_transaction + transaction_number)

    try:
        order_items = wait_long.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='cart-list__info']")))
    except TimeoutException:    #
        print("Error")
        quit()

    order_items_info = [order_item.text for order_item in order_items]
    order_items_name.extend([elem.splitlines()[0] for elem in order_items_info])
    order_items_price.extend([elem.splitlines()[1].split('(')[0].strip().replace(',','.') for elem in order_items_info])
    
    # order_items_amount_unit.extend([elem.splitlines()[1].split(')')[1].strip() for elem in order_items_info])
    old_units = list([elem.splitlines()[1].split(')')[1].strip() for elem in order_items_info])
    word_list = { "Gram": "g", "Liter": "L", "Ml": "ml"}
    for key, value in word_list.items():
        old_units = [amount_unit.replace(key, value) for amount_unit in old_units]
    order_items_amount_unit.extend(old_units)
    
    order_items_amount_number.extend([elem.text for elem in driver.find_elements(By.XPATH, "//a[@class='number-btn']")])
    order_transaction_numbers.extend([transaction_number] * len(order_items))

    transaction_summary = driver.find_elements(By.XPATH, "//div[@class='order-summary__text']/p")
    transaction_order_numbers.extend([transaction_summary[1].text.removeprefix("Bestelnummer: ")])
    transaction_prices.extend([transaction_summary[2].text.split(' - ')[0].removeprefix("€").replace(',','.')])
    transaction_locations.extend([transaction_summary[2].text.split(' - ')[1]])

    print(f"Processed {transaction_number}")


transactions_info = np.array([transaction_numbers, transaction_dates, transaction_order_numbers, transaction_prices, transaction_locations]).transpose()
orders_info = np.array([order_transaction_numbers, order_items_name, order_items_price, order_items_amount_unit, order_items_amount_number]).transpose()

driver.delete_all_cookies()
driver.quit()


np.savetxt('transs.txt', transactions_info, fmt='%s', delimiter=';', encoding='utf8')
np.savetxt('orders.txt', orders_info, fmt='%s', delimiter=';', encoding='utf8')

# time.sleep(10)x