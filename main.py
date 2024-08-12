import time
import locale
from datetime import datetime, date
import numpy as np
# from numpy.dtypes import StringDTyes
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

import config
site_base = "https://www.ekoplaza.nl/nl"
site_orders = site_base + "/account/orders"
site_transaction = site_orders + "/history/transaction/"

def initiate_driver():
    options = FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    print("Driver initiated")
    return driver

def decline_cookie():
    try:
        cookie_decline = wait.until(EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline")))
        cookie_decline.location_once_scrolled_into_view
        time.sleep(0.5)
        cookie_decline.click()
        print("Cookies denied")
    except TimeoutException:
        print("No cookie popup")

def click_log_in():
    login = driver.find_element(By.ID, "user-dropdown")
    login.click()
    print("Login button clicked")
    time.sleep(3)

def log_in():
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
    wait.until(lambda d: d.get_cookie('asppref'))   # Wait for login cookie
    print("Logged in")

def to_order_history():
    driver.get(site_orders)
    print("Orders opened")

def expand_all_transactions():
    first_print = True
    while True:
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".loadmore-btn"))).click()
            if first_print:
                print("Clicked 'Meer'", end='')
                first_print = False
            else:
                print('.', end='')
        except (TimeoutException, StaleElementReferenceException):
            print("\nNo 'Meer' button anymore")
            break

def get_transaction_dates():
    transaction_dates = [elem.text.split(" - ")[1] for elem in driver.find_elements(By.XPATH, "//ul[@class='list-unstyled']/li/a/div/p[@class='title']")]

    locale.setlocale(locale.LC_ALL, 'nl_NL')
    transaction_dates[transaction_dates == "Vandaag"] = date.today().strftime(r'%d %B %Y')
    return [datetime.strptime(date, r'%d %B %Y').strftime(r'%d/%m/%Y') for date in transaction_dates]

def get_transaction_numbers():
    return [elem.get_attribute("href").removeprefix(site_transaction) for elem in driver.find_elements(By.XPATH, "//ul[@class='list-unstyled']/li/a")]

def get_order_transaction_info():
    first_print = True

    order_transaction_numbers = list()
    items_info = list()
    items_amount = list()
    transaction_summaries = list() 

    for transaction_number in transaction_numbers:        # td doesnt work for single number
        driver.get(site_transaction + transaction_number)

        try:
            items = wait_long.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='cart-list__info']")))
        except TimeoutException:    #
            print("Error")
            quit()

        items_info.extend([order_item.text for order_item in items])
        items_amount.extend([elem.text for elem in driver.find_elements(By.XPATH, "//a[@class='number-btn']")])
        order_transaction_numbers.extend([transaction_number] * len(items))
        transaction_summaries.extend([driver.find_element(By.XPATH, "//div[@class='order-summary__text']").text])

        if first_print:
            print(f"Retrieved {transaction_number}", end='')
            first_print = False
        else:
            print(f", {transaction_number}", end='')

    print("\nAll transactions retrieved")

    return (items_info, order_transaction_numbers, items_amount, transaction_summaries)

def procces_order_transactions(items_info: list[str], transaction_summaries: list[str]):
        
    items_name = [elem.splitlines()[0] for elem in items_info]
    items_price = [elem.splitlines()[1].split('(')[0].strip().replace(',','.') for elem in items_info]
    items_amount_unit = [elem.splitlines()[1].split(')')[1].strip() for elem in items_info]

    unit_list = { "Gram": "g", "Liter": "L", "Ml": "ml"}
    for key, value in unit_list.items():
        items_amount_unit = [amount_unit.replace(key, value) for amount_unit in items_amount_unit]

    transaction_order_numbers = [trans_sum.splitlines()[1].removeprefix("Bestelnummer: ") for trans_sum in transaction_summaries]
    transaction_prices = [trans_sum.splitlines()[2].split(' - ')[0].removeprefix("€").replace(',','.') for trans_sum in transaction_summaries]
    transaction_locations = [trans_sum.splitlines()[2].split(' - ')[1] for trans_sum in transaction_summaries]

    items_name.insert(0, "Productnaam")
    items_price.insert(0, "Prijs")
    items_amount_unit.insert(0, "Hoeveelheid")

    transaction_order_numbers.insert(0, "Bestelnummer")
    transaction_prices.insert(0, "Totale prijs")
    transaction_locations.insert(0, "Locatie")

    print("All transactions proccessed")

    return (items_name, items_price, items_amount_unit, transaction_order_numbers, transaction_prices, transaction_locations)

def save(transactions_info, orders_info, combine = True):
    if combine:

        combined_data = np.empty((orders_info.shape[0], orders_info.shape[1] + transactions_info.shape[1] - 1), dtype=object)
        combined_data[:, :orders_info.shape[1]] = orders_info

        for i, order_number in enumerate(orders_info[:,0]):
            combined_data[i, orders_info.shape[1]:] = transactions_info[np.where(transactions_info[:,0] == order_number)][0][1:]

        np.savetxt('trans_orders.csv', combined_data, fmt='%s', delimiter=';', encoding='utf8')

    else:
        np.savetxt('trans.csv', transactions_info, fmt='%s', delimiter=';', encoding='utf8')
        np.savetxt('orders.csv', orders_info, fmt='%s', delimiter=';', encoding='utf8')


driver = initiate_driver()

wait = WebDriverWait(driver, 5)
wait_long = WebDriverWait(driver, 30)

driver.get(site_base)
print("Site opened")

decline_cookie()

click_log_in()

log_in()

to_order_history()

expand_all_transactions()

transaction_numbers = get_transaction_numbers()[:5]
transaction_dates = get_transaction_dates()[:5]
print("Order numbers retrieved")

(items_info, order_transaction_numbers, items_amount, transaction_summaries) = get_order_transaction_info()

driver.delete_all_cookies()
driver.quit()


(items_name, items_price, items_amount_unit, transaction_order_numbers, transaction_prices, transaction_locations) = procces_order_transactions(items_info, transaction_summaries)

transaction_numbers.insert(0, "Transactienummer")
transaction_dates.insert(0, "Datum")
order_transaction_numbers.insert(0, "Transactienummer")
items_amount.insert(0, "Aantal")

transactions_info = np.array([transaction_numbers, transaction_dates, transaction_order_numbers, transaction_prices, transaction_locations]).transpose()
orders_info = np.array([order_transaction_numbers, items_name, items_price, items_amount_unit, items_amount]).transpose()

save(transactions_info, orders_info)

print("Script executed succesfully")