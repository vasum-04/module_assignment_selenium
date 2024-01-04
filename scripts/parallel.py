from dotenv import load_dotenv
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from threading import Thread
import time

load_dotenv()
BROWSERSTACK_USERNAME = os.environ.get(
    "BROWSERSTACK_USERNAME") or "BROWSERSTACK_USERNAME"
BROWSERSTACK_ACCESS_KEY = os.environ.get(
    "BROWSERSTACK_ACCESS_KEY") or "BROWSERSTACK_ACCESS_KEY"
URL = os.environ.get("URL") or "https://hub.browserstack.com/wd/hub"

capabilities = [
    {
        "os": "OS X",
        "osVersion": "Monterey",
        "buildName": "module_assignment_selenium",
        "sessionName": "BStack parallel python",
        "browserName": "chrome",
        "browserVersion": "latest"
    },
    {
        "os": "Windows",
        "osVersion": "11",
        "buildName": "module_assignment_selenium",
        "sessionName": "BStack parallel python",
        "browserName": "firefox",
        "browserVersion": "latest"
    },
    {
        "osVersion": "10",
        "deviceName": "Samsung Galaxy S20",
        "buildName": "module_assignment_selenium",
        "sessionName": "BStack parallel python",
        "browserName": "chrome",
    },
]


def get_browser_option(browser):
    switcher = {
        "chrome": ChromeOptions(),
        "firefox": FirefoxOptions(),
        "edge": EdgeOptions(),
        "safari": SafariOptions(),
    }
    return switcher.get(browser, ChromeOptions())


def run_session(cap):
    bstack_options = {
        "osVersion": cap["osVersion"],
        "buildName": cap["buildName"],
        "sessionName": cap["sessionName"],
        "userName": BROWSERSTACK_USERNAME,
        "accessKey": BROWSERSTACK_ACCESS_KEY
    }
    if "os" in cap:
        bstack_options["os"] = cap["os"]
    if "deviceName" in cap:
        bstack_options['deviceName'] = cap["deviceName"]
    bstack_options["source"] = "python:sample-main:v1.1"
    if cap['browserName'] in ['ios']:
        cap['browserName'] = 'safari'
    options = get_browser_option(cap["browserName"].lower())
    if "browserVersion" in cap:
        options.browser_version = cap["browserVersion"]
    options.set_capability('bstack:options', bstack_options)
    if cap['browserName'].lower() == 'samsung':
        options.set_capability('browserName', 'samsung')
    driver = webdriver.Remote(
        command_executor=URL,
        options=options)
    try:
        driver.get("https://bstackdemo.com/")
        WebDriverWait(driver, 10).until(EC.title_contains("StackDemo"))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "signin")))
        driver.find_element(By.ID, "signin").click()
        driver.implicitly_wait(5)

        # Click the username dropdown
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "username"))
        ).click()

        # Select the 'demouser' option
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='username']//div[contains(text(), 'demouser')]"))
        ).click()
        time.sleep(2)
        # Click the password dropdown
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "password"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='password']//div[contains(text(), 'testingisfun99')]"))
        ).click()
        time.sleep(2)
        # Click the login button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "login-btn"))
        ).click()
        driver.implicitly_wait(10)
        
        # Get text of an product - iPhone 12
        item_on_page = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="1"]/p'))).text
        # Click the 'Add to cart' button if it is visible
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="1"]/div[4]'))).click()
        # Check if the Cart pane is visible
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "float-cart__content")))
        # Get text of product in cart
        item_in_cart = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div/div/div[2]/div[2]/div[2]/div/div[3]/p[1]'))).text
        # Verify whether the product (iPhone 12) is added to cart
        if item_on_page == item_in_cart:
            # Set the status of test as 'passed' or 'failed' based on the condition; if item is added to cart
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "iPhone 12 has been successfully added to the cart!"}}')

        # Click the 'Proceed to Checkout' button
        checkout_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'buy-btn')))
        checkout_button.click()

        # Fill in shipping address details
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "firstNameInput"))).send_keys("Vasudev")
        driver.find_element(By.ID, "lastNameInput").send_keys("Mishra")
        driver.find_element(By.ID, "addressLine1Input").send_keys("128/303 K Block Kidwai Nagar Kanpur")
        driver.find_element(By.ID, "provinceInput").send_keys("UttarPradesh")
        driver.find_element(By.ID, "postCodeInput").send_keys("208011")

        # Click the 'Submit' button for the shipping address
        submit_button = driver.find_element(By.ID, "checkout-shipping-continue")
        submit_button.click()

         # Find the confirmation message
        confirm_msg = driver.find_element(By.ID, "confirmation-message")

        # Check if confirmation message is displayed
        if confirm_msg.is_displayed() == True:
            # Set the status of test as 'passed' if confirmation message is displayed
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Your Order has been successfully placed."}}')
        else:
            # Set the status of test as 'failed' if confirmation message is not displayed
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Oops! Please try again after some time"}}')
    except NoSuchElementException as err:
        message = "Exception: " + str(err.__class__) + str(err.msg)
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": ' + json.dumps(message) + '}}')
    except Exception as err:
        message = "Exception: " + str(err.__class__) + str(err.msg)
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": ' + json.dumps(message) + '}}')
    # Stop the driver
    driver.quit()


for cap in capabilities:
    Thread(target=run_session, args=(cap,)).start()
