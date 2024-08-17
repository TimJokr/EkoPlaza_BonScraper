#!/usr/bin/env python3
import locale
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any

import config
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

site_base = "https://www.ekoplaza.nl/nl"
site_orders = site_base + "/account/orders"
site_transaction = site_orders + "/history/transaction/"


def setup():
    close = False
    print(
        "Welcome to the EkoPlaza BonScraper. This is the first time you used this program. Some settings need to be intialized."
    )

    with open(Path("config.py"), "x") as f:
        input_email = input("Enter email used for EkoPlaza (this is stored locally): ")
        input_password = input(
            "Enter password used for EkoPlaza (this is stored locally): "
        )
        f.write(f"email = '{input_email}'\n")
        f.write(f"password = '{input_password}'\n")

        input_headless: str = input(
            "Do you want to see what is happening? [Yes/No] (enables headless): "
        ).lower()
        if input_headless == "yes" or input_headless == "y":
            f.write("headless = True\n")
        elif input_headless == "no" or input_headless == "n":
            f.write("headless = False\n")
        else:
            print("Please enter yes or no next time...")
            close = True

        if not close:
            input_driver: str = input(
                "What driver do you want to use? [Firefox/Chrome/Edge/Safari/Internet Explorer]: "
            ).lower()
            match input_driver:
                case "firefox":
                    f.write("driver_type = 'ff'\n")
                case "chrome":
                    f.write("driver_type = 'chr'\n")
                case "edge":
                    f.write("driver_type = 'edge'\n")
                case "safari":
                    f.write("driver_type = 'saf'\n")
                case "internet explorer":
                    f.write("driver_type = 'ie'\n")
                case _:
                    print("Please enter a valid option next time...")
                    close = True

        if not close:
            input_combine = input(
                "Do you want to combine transactions and orders? [Yes/No] (Combining is recommended, keeping them apart is more SQL like): "
            ).lower()
            if input_combine == "yes" or input_combine == "y":
                f.write("combine = True\n")
            elif input_combine == "no" or input_combine == "n":
                f.write("combine = False\n")
            else:
                print("Please enter yes or no next time...")
                close = True

    if close:
        Path.unlink(Path("config.py"))
        quit()
    else:
        print("Setup succesfull")


def initiate_driver():
    match config.driver_type:
        case "ff":
            options = FirefoxOptions()
            if config.headless:
                options.add_argument("--headless")
            options.set_preference("permissions.default.image", 2)
            driver = webdriver.Firefox(options=options)
        case "chr":

            options = ChromeOptions()
            if config.headless:
                options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=options)
            driver.execute_cdp_cmd(
                "Network.setBlockedURLs", {"urls": ["*.jpg", "*.png", "*.gif", "*.svg"]}
            )
            driver.execute_cdp_cmd("Network.enable", {})
        case "edge":

            options = EdgeOptions()
            if config.headless:
                options.add_argument("--headless=new")
            driver = webdriver.Edge(options=options)
        case "saf":

            options = SafariOptions()
            if config.headless:
                print("Safari does not support headless mode")
            driver = webdriver.Safari(options=options)
        case "ie":

            options = IeOptions()
            if config.headless:
                print("Internet Explorer does not support headless mode")
            driver = webdriver.Ie(options=options)
        case _:
            print(
                "Driver is not given or wrong. Please change this in 'config.py' or delete the file."
            )
            quit()

    driver.implicitly_wait(5)
    driver.maximize_window()
    print("Driver initiated")
    return driver


def decline_cookie(
    driver: (
        webdriver.Firefox
        | webdriver.Chrome
        | webdriver.Edge
        | webdriver.Safari
        | webdriver.Ie
    ),
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
    driver: (
        webdriver.Firefox
        | webdriver.Chrome
        | webdriver.Edge
        | webdriver.Safari
        | webdriver.Ie
    ),
):
    login = driver.find_element(By.ID, "user-dropdown")
    login.click()
    print("Login button clicked")


def log_in(
    driver: (
        webdriver.Firefox
        | webdriver.Chrome
        | webdriver.Edge
        | webdriver.Safari
        | webdriver.Ie
    ),
):
    wait = WebDriverWait(driver, 5)

    # Find the fields
    email_field = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[id*=login-email]"))
    )
    password_field = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[id^=Wachtwoord-]"))
    )
    login_submit = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-success:nth-child(1)"))
    )
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
    wait.until(lambda d: d.get_cookie("asppref"))  # Wait for login cookie
    print("Logged in")


def to_order_history(
    driver: (
        webdriver.Firefox
        | webdriver.Chrome
        | webdriver.Edge
        | webdriver.Safari
        | webdriver.Ie
    ),
):
    driver.get(site_orders)
    print("Orders opened")


def expand_all_transactions(
    driver: (
        webdriver.Firefox
        | webdriver.Chrome
        | webdriver.Edge
        | webdriver.Safari
        | webdriver.Ie
    ),
):
    first_print = True
    while True:
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".loadmore-btn"))
            ).click()
            if first_print:
                print("Clicked 'Meer'", end="")
                first_print = False
            else:
                print(".", end="")
        except (TimeoutException, StaleElementReferenceException):
            print("\nNo 'Meer' button anymore")
            break


def get_transaction_numbers(
    driver: (
        webdriver.Firefox
        | webdriver.Chrome
        | webdriver.Edge
        | webdriver.Safari
        | webdriver.Ie
    ),
):
    return [
        str(elem.get_attribute("href")).removeprefix(site_transaction)
        for elem in driver.find_elements(By.XPATH, "//ul[@class='list-unstyled']/li/a")
    ]


def get_transaction_dates(
    driver: (
        webdriver.Firefox
        | webdriver.Chrome
        | webdriver.Edge
        | webdriver.Safari
        | webdriver.Ie
    ),
):
    transaction_dates = [
        elem.text.split(" - ")[1]
        for elem in driver.find_elements(
            By.XPATH, "//ul[@class='list-unstyled']/li/a/div/p[@class='title']"
        )
    ]

    locale.setlocale(locale.LC_TIME, "nl_NL")
    transaction_dates[transaction_dates == "Vandaag"] = datetime.today().strftime(
        r"%d %B %Y"
    )
    return [
        datetime.strptime(date, r"%d %B %Y").strftime(r"%d/%m/%Y")
        for date in transaction_dates
    ]


def get_order_transaction_info(
    driver: (
        webdriver.Firefox
        | webdriver.Chrome
        | webdriver.Edge
        | webdriver.Safari
        | webdriver.Ie
    ),
    transaction_numbers: list[str],
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
                EC.visibility_of_all_elements_located(
                    (By.XPATH, "//div[@class='cart-list__info']")
                )
            )
        except TimeoutException:  #
            print("\nError: pagina laden duurde te lang")
            quit()

        items_info.extend([order_item.text for order_item in items])
        items_amount.extend(
            [
                elem.text
                for elem in driver.find_elements(By.XPATH, "//a[@class='number-btn']")
            ]
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
    items_price = [
        elem.splitlines()[1].split("(")[0].strip().replace(",", ".")
        for elem in items_info
    ]
    items_amount_unit = [
        elem.splitlines()[1].split(")")[1].strip() for elem in items_info
    ]

    unit_list = {"Gram": "g", "Liter": "L", "Ml": "ml"}
    for key, value in unit_list.items():
        items_amount_unit = [
            amount_unit.replace(key, value) for amount_unit in items_amount_unit
        ]

    transaction_order_numbers = [
        trans_sum.splitlines()[1].removeprefix("Bestelnummer: ")
        for trans_sum in transaction_summaries
    ]
    transaction_prices = [
        trans_sum.splitlines()[2].split(" - ")[0].removeprefix("€").replace(",", ".")
        for trans_sum in transaction_summaries
    ]
    transaction_locations = [
        trans_sum.splitlines()[2].split(" - ")[1] for trans_sum in transaction_summaries
    ]

    items_name.insert(0, "Productnaam")
    items_price.insert(0, "Prijs")
    items_amount_unit.insert(0, "Hoeveelheid")

    transaction_order_numbers.insert(0, "Bestelnummer")
    transaction_prices.insert(0, "Totale prijs")
    transaction_locations.insert(0, "Locatie")

    print("All transactions proccessed")

    return (
        items_name,
        items_price,
        items_amount_unit,
        transaction_order_numbers,
        transaction_prices,
        transaction_locations,
    )


def save(transactions_info: NDArray[Any], orders_info: NDArray[Any], combine: bool):
    if combine:
        (order_rows, order_cols) = orders_info.shape

        combined_data = np.empty(
            (order_rows, order_cols + transactions_info.shape[1] - 1), dtype=object
        )
        combined_data[:, :order_cols] = orders_info

        for i, order_number in enumerate(orders_info[:, 0]):
            combined_data[i, order_cols:] = transactions_info[
                np.where(transactions_info[:, 0] == order_number)
            ][0][1:]

        np.savetxt(
            "trans_orders.csv", combined_data, fmt="%s", delimiter=";", encoding="utf8"
        )
    else:
        np.savetxt(
            "trans.csv", transactions_info, fmt="%s", delimiter=";", encoding="utf8"
        )
        np.savetxt("orders.csv", orders_info, fmt="%s", delimiter=";", encoding="utf8")


def main():

    if not Path("config.py").is_file():
        setup()

    driver = initiate_driver()

    driver.get(site_base)
    print("Site opened")

    decline_cookie(driver)

    click_log_in(driver)

    log_in(driver)

    to_order_history(driver)

    expand_all_transactions(driver)

    transaction_numbers = get_transaction_numbers(driver)
    transaction_dates = get_transaction_dates(driver)
    print("Order numbers retrieved")

    (items_info, order_transaction_numbers, items_amount, transaction_summaries) = (
        get_order_transaction_info(driver, transaction_numbers)
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

    transaction_numbers.insert(0, "Transactienummer")
    transaction_dates.insert(0, "Datum")
    order_transaction_numbers.insert(0, "Transactienummer")
    items_amount.insert(0, "Aantal")

    transactions_info: NDArray[Any] = np.array(
        [
            transaction_numbers,
            transaction_dates,
            transaction_order_numbers,
            transaction_prices,
            transaction_locations,
        ]
    ).transpose()
    orders_info: NDArray[Any] = np.array(
        [
            order_transaction_numbers,
            items_name,
            items_price,
            items_amount_unit,
            items_amount,
        ]
    ).transpose()

    save(transactions_info, orders_info, config.combine)

    print("Script executed succesfully")


if __name__ == "__main__":
    main()
