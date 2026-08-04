"""Логика единственной страницы elbo.ink (одностраничный сайт)."""
import re

from selenium.webdriver.common.by import By

PLACEHOLDER_MARKERS = ["[LOCATION]", "[EMAIL]", "[BIO]", "[PHOTO]"]
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
INSTAGRAM_HANDLE_URL = "https://www.instagram.com/elbo.inkk"
SECTION_IDS = ["studio", "services", "work", "book"]


def page_title(driver):
    return driver.title


def nav_links(driver):
    return [a for a in driver.find_elements(By.CSS_SELECTOR, "nav ul a") if a.get_attribute("href")]


def is_nav_list_visible(driver):
    nav_ul = driver.find_element(By.CSS_SELECTOR, "nav ul")
    return nav_ul.value_of_css_property("display") != "none"


def instagram_links(driver):
    return [
        a for a in driver.find_elements(By.CSS_SELECTOR, "a[href*='instagram.com']")
    ]


def mailto_link(driver):
    links = driver.find_elements(By.CSS_SELECTOR, "a[href^='mailto:']")
    return links[0] if links else None


def placeholder_markers_in_body(driver):
    """Ищем в page_source, а не в рендеренном .text: часть контента лежит
    в .reveal-блоках, скрытых (opacity/visibility) до срабатывания
    IntersectionObserver — Selenium .text не отдаёт их текст до скролла,
    хотя маркеры реально присутствуют в разметке.

    HTML-комментарии вырезаем перед поиском: в начале файла есть
    легенда маркеров ('[BIO] -> replace...') внутри <!-- --> — она
    навсегда содержит буквальный текст '[BIO]'/'[PHOTO]', даже когда
    реальный видимый контент уже заполнен."""
    source = _COMMENT_RE.sub("", driver.page_source)
    return [m for m in PLACEHOLDER_MARKERS if m in source]


def has_reveal_class_active(element):
    return "in" in (element.get_attribute("class") or "").split()


def copyright_year_text(driver):
    return driver.find_element(By.CSS_SELECTOR, "#yr").text.strip()


def section_element(driver, section_id):
    return driver.find_element(By.CSS_SELECTOR, f"#{section_id}")


def reveal_elements(driver):
    return driver.find_elements(By.CSS_SELECTOR, ".reveal")


def scroll_to(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)


def favicon_link(driver):
    links = driver.find_elements(By.CSS_SELECTOR, "link[rel='icon']")
    return links[0] if links else None


def meta_content(driver, attr, value):
    els = driver.find_elements(By.CSS_SELECTOR, f"meta[{attr}='{value}']")
    return els[0].get_attribute("content") if els else None


def gallery_images(driver):
    return driver.find_elements(By.CSS_SELECTOR, ".grid .tile img")


def lang_toggle_button(driver):
    return driver.find_element(By.CSS_SELECTOR, "#langToggle")


def html_lang_attribute(driver):
    return driver.find_element(By.TAG_NAME, "html").get_attribute("lang")


def i18n_text(driver, key):
    return driver.find_element(By.CSS_SELECTOR, f"[data-i18n='{key}']").text.strip()
