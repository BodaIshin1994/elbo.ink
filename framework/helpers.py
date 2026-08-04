"""Общие хелперы для тестов elbo.ink — статический одностраничный сайт,
без Basic Auth и без backend (GitHub Pages)."""
from selenium.webdriver.support.ui import WebDriverWait

SITE_URL = "https://bodaishin1994.github.io/elbo.ink/"
TIMEOUT = 15


def open_home(driver):
    driver.get(SITE_URL)
    WebDriverWait(driver, TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
