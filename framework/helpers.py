"""Общие хелперы для тестов elbo.ink — статический одностраничный сайт,
без Basic Auth и без backend (GitHub Pages).

SITE_URL переопределяется через переменную окружения ELBO_SITE_URL — так
можно прогнать этот же набор тестов против /dev/ или /staging/ превью
перед мёржем в main, без правки кода."""
import os

from selenium.webdriver.support.ui import WebDriverWait

SITE_URL = os.environ.get("ELBO_SITE_URL", "https://bodaishin1994.github.io/elbo.ink/")
TIMEOUT = 15


def open_home(driver):
    driver.get(SITE_URL)
    WebDriverWait(driver, TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
