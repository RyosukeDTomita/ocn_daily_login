# coding: utf-8
"""
Name: ocn_daily_login.py

Description:

Usage: python3 ocn_daily_login.py --userid <userid> --pasword <password>

Author: Ryosuke Tomita
Date: 5/1
"""
import argparse
from selenium import webdriver
from selenium.webdriver import chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pickle
import time
import requests
#from bs4 import BeautifulSoup
import os
from os.path import join, dirname, abspath


def parse_args():
    """parse_args.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--userid", help="docomo userID", type=str)
    parser.add_argument("-p", "--password", help="docomo user password", type=str)
    p = parser.parse_args()
    args = {"userid": p.userid, "password": p.password}
    return args


def fetch_driver():
    """fetch_driver.
    """
    #driver = webdriver.Chrome(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    res = requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE')
    driver = webdriver.Chrome(
            service=Service(ChromeDriverManager(res.text).install()),
            options=chrome_options)
    return driver


def session_is_empty(driver, cookies_file):
    return os.stat(cookies_file).st_size == 0


def login(driver, user_id, password):
    """login.

    Args:
        driver:
        user_id:
        password:
    """
    login_button1 = driver.find_element(By.XPATH, '//*[@id="va14-vin-2d"]')

    login_button1.click()
    time.sleep(3)

    # input ID
    id_textbox = driver.find_element(By.XPATH, '//*[@id="Di_Uid"]')
    id_textbox.send_keys(user_id)
    next_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[1]/div[4]/div[1]/form/input[4]')
    next_button.click()

    # input password and security_code
    password_textbox = driver.find_element(By.XPATH, '//*[@id="Di_Pass"]')
    password_textbox.send_keys(password)
    security_code = input("Type security code: ")
    security_code_textbox = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[6]/form/dl[2]/dd[2]/input')
    security_code_textbox.send_keys(security_code)
    time.sleep(3)

    # login
    login_button2 = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[6]/form/input[4]')
    login_button2.click()
    time.sleep(5)


def get_daily_point(driver):
    """get_daily_point.

    Args:
        driver:
    """
    # selenium can only click viewing element, so scroll it.
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)

    point_button = driver.find_element(By.XPATH, '//*[@id="normalget"]/img')
    point_button.click()
    time.sleep(3)


def set_cookies(driver, cookies_file):
    cookies = pickle.load(open(cookies_file, 'rb'))
    for c in cookies:
        driver.add_cookie(c)


def save_cookies(driver, cookies_file):
    cookies = driver.get_cookies()
    pickle.dump(cookies, open(cookies_file, 'wb'))


def main():
    """
    1. get arguments and initialsettings.
    2. fetch driver.
    3. use selenium to access ocn top page.
    4. login.
    5. push 訪問ポイント
    6. tear down.
    """
    # get arguments and initialsettings
    args = parse_args()
    user_id = args['userid']
    password = args['password']
    url = "https://www.ocn.ne.jp/"
    cookies_file = abspath(join(dirname(__file__), 'cookies.pkl'))
    # fetch driver
    driver = fetch_driver()

    # access the ocn top page and login
    driver.get(url)
    if  session_is_empty(driver, cookies_file):
        print("Session not exist.")
        login(driver, user_id, password)
        save_cookies(driver, cookies_file)
    else:
        print("Session exist.")
        login(driver, user_id, password)
        set_cookies(driver, cookies_file)
        driver.get(url) # reload page

    # push daily point button.
    get_daily_point(driver)

    # renew session and save new one.
    driver.get(url)
    save_cookies(driver, cookies_file)
    driver.quit()


if __name__ == "__main__":
    main()
