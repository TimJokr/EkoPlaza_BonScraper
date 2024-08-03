import time
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

options = FirefoxOptions()
options.add_argument("--headless=new")

driver = webdriver.Firefox(options=options)
driver.get("https://www.ekoplaza.nl/")
#print(driver.page_source)
time.sleep(5)
login = driver.find_element(By.ID, "user-dropdown")
login.click()

time.sleep(10)
driver.quit()