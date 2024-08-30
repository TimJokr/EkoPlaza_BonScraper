#!/usr/bin/env python3
import configparser
import locale
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any

import numpy as np
from numpy._typing import NDArray
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver import (
    ChromeOptions,
    EdgeOptions,
    FirefoxOptions,
    IeOptions,
    SafariOptions,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_input():

    input_email = input("Enter email used for EkoPlaza (this is stored locally): ")
    input_password = input("Enter password used for EkoPlaza (this is stored locally): ")
    input_driver: str = input(
        "What driver do you want to use? [Firefox/Chrome/Edge/Safari/Internet Explorer]: "
    ).lower()
    input_headless: str = input("Do you want to see what is happening? [Yes/No] (toggles headless): ").lower()

    return (input_email, input_password, input_driver, input_headless)


def setup():

    print(
        "Welcome to the EkoPlaza BonScraper. This is the first time you used this program. Some settings need to be intialized."
    )

    (conf_email, conf_password, input_driver, input_headless) = setup_input()

    match input_driver:
        case "firefox":
            conf_driver = "ff"
        case "chrome":
            conf_driver = "chr"
        case "edge":
            conf_driver = "edge"
        case "safari":
            conf_driver = "saf"
        case "internet explorer":
            conf_driver = "ie"
        case _:
            print("Input incorrect...")
            quit()

    if input_headless == "yes" or input_headless == "y":
        conf_headless = "False"
    elif input_headless == "no" or input_headless == "n":
        conf_headless = "True"
    else:
        print("Input incorrect...")
        quit()

    config = configparser.ConfigParser()

    config["Personal"] = {"email": conf_email, "password": conf_password}
    config["Preferences"] = {
        "driver": conf_driver,
        "headless": conf_headless,
    }

    with open("config.ini", "x") as configfile:
        config.write(configfile)

    print("Setup succesfull")


def initiate_driver():

    config = configparser.ConfigParser()
    config.read("config.ini")

    match config["Preferences"]["driver"]:
        case "ff":
            options = FirefoxOptions()
            if config["Preferences"]["headless"] == "True":
                options.add_argument("--headless")
            options.set_preference("permissions.default.image", 2)
            driver = webdriver.Firefox(options=options)

        case "chr":
            options = ChromeOptions()
            if config["Preferences"]["headless"] == "True":
                options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=options)
            driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["*.jpg", "*.png", "*.gif", "*.svg"]})
            driver.execute_cdp_cmd("Network.enable", {})

        case "edge":
            options = EdgeOptions()
            if config["Preferences"]["headless"] == "True":
                options.add_argument("--headless=new")
            driver = webdriver.Edge(options=options)

        case "saf":
            options = SafariOptions()
            if config["Preferences"]["headless"] == "True":
                print("Safari does not support headless mode")

            driver = webdriver.Safari(options=options)
        case "ie":
            options = IeOptions()
            if config["Preferences"]["headless"] == "True":
                print("Internet Explorer does not support headless mode")
            driver = webdriver.Ie(options=options)

        case _:
            print("Driver is not given or wrong. Please change this in 'config.ini' or delete the file.")
            quit()

    driver.implicitly_wait(5)
    driver.maximize_window()
    print("Driver initiated")

    return driver


def decline_cookie(
    driver: webdriver.Firefox | webdriver.Chrome | webdriver.Edge | webdriver.Safari | webdriver.Ie,
):
    try:
        cookie_decline = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
        )
        cookie_decline.location_once_scrolled_into_view
        sleep(0.5)
        cookie_decline.click()
        print("Cookies denied")
    except TimeoutException:
        print("No cookie popup")


def click_log_in(
    driver: webdriver.Firefox | webdriver.Chrome | webdriver.Edge | webdriver.Safari | webdriver.Ie,
):
    login = driver.find_element(By.ID, "user-dropdown")
    login.click()
    print("Login button clicked")


def log_in(
    driver: webdriver.Firefox | webdriver.Chrome | webdriver.Edge | webdriver.Safari | webdriver.Ie,
):

    wait = WebDriverWait(driver, 5)

    config = configparser.ConfigParser()
    config.read("config.ini")

    # Find the fields
    email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[id*=login-email]")))
    password_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[id^=Wachtwoord-]")))
    login_submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-success:nth-child(1)")))
    print("Fields found")

    # Click email field and fill in email
    email_field.click()
    email_field.clear()
    email_field.send_keys(config["Personal"]["email"])
    print("Email filled in")

    # Click password field and fill in password
    password_field.click()
    password_field.clear()
    password_field.send_keys(config["Personal"]["password"])
    print("Password filled in")

    # Click login
    login_submit.click()
    print("Login submitted")
    wait.until(lambda d: d.get_cookie("asppref"))  # Wait for login cookie
    print("Logged in")


def to_order_history(
    driver: webdriver.Firefox | webdriver.Chrome | webdriver.Edge | webdriver.Safari | webdriver.Ie,
    site_orders,
):
    driver.get(site_orders)
    print("Orders opened")


def expand_all_transactions(
    driver: webdriver.Firefox | webdriver.Chrome | webdriver.Edge | webdriver.Safari | webdriver.Ie,
):
    first_print = True
    while True:
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".loadmore-btn"))
            ).click()
            sleep(3)  # Annoying, but prevents duplicate orders for some reason
            if first_print:
                print("Clicked 'Meer'", end="")
                first_print = False
            else:
                print(".", end="")
        except (TimeoutException, StaleElementReferenceException):
            print("\nNo 'Meer' button anymore")
            break


def get_transaction_numbers(
    driver: webdriver.Firefox | webdriver.Chrome | webdriver.Edge | webdriver.Safari | webdriver.Ie,
    site_transaction,
):
    return [
        str(elem.get_attribute("href")).removeprefix(site_transaction)
        for elem in driver.find_elements(By.XPATH, "//ul[@class='list-unstyled']/li/a")
    ]


def get_transaction_dates(
    driver: webdriver.Firefox | webdriver.Chrome | webdriver.Edge | webdriver.Safari | webdriver.Ie,
):
    transaction_dates = [
        elem.text.split(" - ")[1]  # td werkt bij vandaag?
        for elem in driver.find_elements(By.XPATH, "//ul[@class='list-unstyled']/li/a/div/p[@class='title']")
    ]

    locale.setlocale(locale.LC_TIME, "nl_NL")
    transaction_dates[transaction_dates == "Vandaag"] = datetime.today().strftime(r"%d %B %Y")
    return [datetime.strptime(date, r"%d %B %Y").strftime(r"%d/%m/%Y") for date in transaction_dates]


def remove_processed_transactions(transaction_numbers: list[str], transaction_dates: list[str]):
    config = configparser.ConfigParser()
    config.read("config.ini")

    try:
        latest_date = config["Data"]["latest_date"]
        index = transaction_dates.index(latest_date)
        del transaction_numbers[index:]  # Removes already proccesed stuff in place
        del transaction_dates[index:]
    except:
        print("No 'latest_date' found, continuing as normal")


def get_order_transaction_info(
    driver: webdriver.Firefox | webdriver.Chrome | webdriver.Edge | webdriver.Safari | webdriver.Ie,
    transaction_numbers: list[str],
    site_transaction,
):
    first_print = True

    order_transaction_numbers: list[str] = list()
    items_info: list[str] = list()
    items_amount: list[str] = list()
    transaction_summaries: list[str] = list()

    for transaction_number in transaction_numbers:  # td doesnt work for single number
        driver.get(site_transaction + transaction_number)

        try:
            items = WebDriverWait(driver, 30).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='cart-list__info']"))
            )
        except TimeoutException:  #
            print("\nError: pagina laden duurde te lang")
            quit()

        items_info.extend([order_item.text for order_item in items])
        items_amount.extend(
            [elem.text for elem in driver.find_elements(By.XPATH, "//a[@class='number-btn']")]
        )
        order_transaction_numbers.extend([transaction_number] * len(items))
        transaction_summaries.extend(
            [driver.find_element(By.XPATH, "//div[@class='order-summary__text']").text]
        )

        if first_print:
            print(f"Retrieved {transaction_number}", end="")
            first_print = False
        else:
            print(f", {transaction_number}", end="")

    print("\nAll transactions retrieved")

    return (items_info, order_transaction_numbers, items_amount, transaction_summaries)


def procces_order_transactions(items_info: list[str], transaction_summaries: list[str]):

    items_name = [elem.splitlines()[0] for elem in items_info]
    items_price = [elem.splitlines()[1].split("(")[0].strip().replace(",", ".") for elem in items_info]
    items_amount_unit = [elem.splitlines()[1].split(")")[1].strip() for elem in items_info]

    unit_list = {"Gram": "g", "Liter": "L", "Ml": "ml"}
    for key, value in unit_list.items():
        items_amount_unit = [amount_unit.replace(key, value) for amount_unit in items_amount_unit]

    transaction_order_numbers = [
        trans_sum.splitlines()[1].removeprefix("Bestelnummer: ") for trans_sum in transaction_summaries
    ]
    transaction_prices = [
        trans_sum.splitlines()[2].split(" - ")[0].removeprefix("€").replace(",", ".")
        for trans_sum in transaction_summaries
    ]
    transaction_locations = [trans_sum.splitlines()[2].split(" - ")[1] for trans_sum in transaction_summaries]

    print("All transactions proccessed")

    return (
        items_name,
        items_price,
        items_amount_unit,
        transaction_order_numbers,
        transaction_prices,
        transaction_locations,
    )


def save_latest_date(date):
    config = configparser.ConfigParser()
    config.read("config.ini")
    config["Data"] = {"latest_date": date}
    with open("config.ini", "w") as configfile:
        config.write(configfile)


def make_transaction_info(
    transaction_numbers: list[str],
    transaction_dates: list[str],
    transaction_order_numbers: list[str],
    transaction_prices: list[str],
    transaction_locations: list[str],
) -> NDArray[Any]:

    transactions_info: NDArray[Any] = np.array(
        [
            transaction_numbers,
            transaction_dates,
            transaction_order_numbers,
            transaction_prices,
            transaction_locations,
        ]
    ).transpose()

    return transactions_info


def make_orders_info(
    order_transaction_numbers: list[str],
    items_name: list[str],
    items_price: list[str],
    items_amount_unit: list[str],
    items_amount: list[str],
) -> NDArray[Any]:

    orders_info: NDArray[Any] = np.array(
        [
            order_transaction_numbers,
            items_name,
            items_price,
            items_amount_unit,
            items_amount,
        ]
    ).transpose()

    return orders_info


def combine_info(transactions_info, orders_info):
    (order_rows, order_cols) = orders_info.shape

    combined_data = np.empty((order_rows, order_cols + transactions_info.shape[1] - 1), dtype=object)
    combined_data[:, :order_cols] = orders_info

    for i, order_number in enumerate(orders_info[:, 0]):
        combined_data[i, order_cols:] = transactions_info[np.where(transactions_info[:, 0] == order_number)][
            0
        ][1:]

    return combined_data


def combine_data(combined_data: NDArray[Any]):
    if Path("data.csv").is_file():
        old_data = np.loadtxt("data.csv", dtype=str, delimiter=";", encoding="utf8")
        combined_data = np.vstack((combined_data, old_data))

    save("data.csv", combined_data)

    return combined_data


def add_header(combined_data: NDArray[Any]):

    header = np.array(
        [
            [
                "Transactienummer",
                "Productnaam",
                "Prijs",
                "Hoeveelheid",
                "Aantal",
                "Datum",
                "Bestelnummer",
                "Totale prijs",
                "Locatie",
            ]
        ]
    )
    output = np.vstack((header, combined_data))

    return output


def save(name, combined_data: NDArray[Any]):
    np.savetxt(name, combined_data, fmt="%s", delimiter=";", encoding="utf8")


def main():
    site_base = "https://www.ekoplaza.nl/nl"
    site_orders = site_base + "/account/orders"
    site_transaction = site_orders + "/history/transaction/"

    if not Path("config.ini").is_file():
        setup()

    driver = initiate_driver()

    driver.get(site_base)
    print("Site opened")

    decline_cookie(driver)

    click_log_in(driver)

    log_in(driver)

    to_order_history(driver, site_orders)

    expand_all_transactions(driver)

    transaction_numbers = get_transaction_numbers(driver, site_transaction)[-7:]
    transaction_dates = get_transaction_dates(driver)[-7:]
    print("Order numbers retrieved")

    remove_processed_transactions(transaction_numbers, transaction_dates)

    (items_info, order_transaction_numbers, items_amount, transaction_summaries) = get_order_transaction_info(
        driver, transaction_numbers, site_transaction
    )

    driver.delete_all_cookies()
    driver.quit()

    (
        items_name,
        items_price,
        items_amount_unit,
        transaction_order_numbers,
        transaction_prices,
        transaction_locations,
    ) = procces_order_transactions(items_info, transaction_summaries)

    transactions_info = make_transaction_info(
        transaction_numbers,
        transaction_dates,
        transaction_order_numbers,
        transaction_prices,
        transaction_locations,
    )

    orders_info = make_orders_info(
        order_transaction_numbers,
        items_name,
        items_price,
        items_amount_unit,
        items_amount,
    )

    combined_data = combine_info(transactions_info, orders_info)

    combined_data = combine_data(combined_data)

    output = add_header(combined_data)

    save("output.csv", output)

    save_latest_date(transaction_dates[0])

    print("Script executed succesfully")


if __name__ == "__main__":
    main()
