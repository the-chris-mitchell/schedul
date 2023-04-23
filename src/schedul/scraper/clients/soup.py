import time
from datetime import timedelta

import requests_cache
from bs4 import BeautifulSoup
from requests import Response
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def get_cached_soup(
    url: str, cache_name: str, expiry: timedelta | int = -1
) -> BeautifulSoup:
    requests_session = requests_cache.CachedSession(
        f"../../.cache/{cache_name}", expire_after=expiry
    )
    print(f"Getting {url}: ", end="")
    response = requests_session.get(url)
    if response.from_cache:
        print("Cache Hit")
    else:
        print("Response Received")
    return BeautifulSoup(response.text, features="html.parser")


def get_rendered_soup(url: str) -> BeautifulSoup:
    session = HTMLSession()
    response = session.get(url)
    response.html.render(timeout=60)
    return BeautifulSoup(response.html.raw_html, features="html.parser")


def get_selenium_soup(url: str) -> BeautifulSoup:
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    driver.get(url)
    els = driver.find_elements(By.CLASS_NAME, "times-calendar__el")
    for el in els:
        time.sleep(1)
        el.click()
    return BeautifulSoup(driver.page_source, features="html.parser")
