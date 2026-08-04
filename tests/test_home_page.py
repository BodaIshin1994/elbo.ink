"""
Тесты одностраничного сайта elbo.ink (GitHub Pages, статика — без
Basic Auth, без backend).

Стенд: https://bodaishin1994.github.io/elbo.ink/ (пока не привязан
кастомный домен elbo.ink — DNS ещё не настроен, см. README.md репозитория).

Запуск:
    pytest tests/test_home_page.py -v
"""
import time

import pytest
from selenium.webdriver.common.by import By

from framework.helpers import open_home
from pages.home_page import (
    INSTAGRAM_HANDLE_URL,
    SECTION_IDS,
    copyright_year_text,
    favicon_link,
    gallery_images,
    has_reveal_class_active,
    instagram_links,
    is_nav_list_visible,
    mailto_link,
    meta_content,
    nav_links,
    placeholder_markers_in_body,
    reveal_elements,
    scroll_to,
    section_element,
)


# ── Базовая загрузка ──────────────────────────────────────────────────────────

def test_page_loads_with_expected_title(driver):
    open_home(driver)
    assert "ELBO.INK" in driver.title


def test_all_sections_present(driver):
    open_home(driver)
    for section_id in SECTION_IDS:
        assert section_element(driver, section_id) is not None, f"Секция #{section_id} не найдена"


def test_copyright_year_auto_fills_current_year(driver):
    """Год в подвале ('© <span id=yr></span> ELBO.INK') заполняется JS
    через new Date().getFullYear() — не хардкод."""
    open_home(driver)
    year_text = copyright_year_text(driver)
    assert year_text.isdigit() and len(year_text) == 4, f"Ожидался 4-значный год, получили {year_text!r}"


# ── Навигация ─────────────────────────────────────────────────────────────────

def test_desktop_nav_shows_all_section_links(driver):
    open_home(driver)
    assert is_nav_list_visible(driver), "Меню навигации должно быть видимым на desktop-ширине"

    links = nav_links(driver)
    hrefs = " ".join(a.get_attribute("href") for a in links)
    for section_id in ["studio", "work", "book"]:
        assert f"#{section_id}" in hrefs, f"В навигации не найдена ссылка на #{section_id}"


def test_nav_work_link_points_to_correct_section(driver):
    """Регрессионный guard: раньше пункт меню 'WORK' указывал на
    href='#services' вместо '#work' (клик скроллил на Services, а не на
    портфолио) — исправлено в index.html 2026-08-04."""
    open_home(driver)
    work_links = [a for a in nav_links(driver) if a.text.strip().upper() == "WORK"]
    assert work_links, "Пункт меню 'WORK' не найден"
    assert work_links[0].get_attribute("href").endswith("#work"), (
        f"Пункт меню 'WORK' должен вести на #work, а ведёт на {work_links[0].get_attribute('href')!r}"
    )


def test_mobile_viewport_hides_nav_with_no_alternative_toggle(mobile_driver):
    """Зафиксированное текущее поведение (не однозначный баг, но пробел
    UX): на ширине <640px meню навигации скрывается через CSS
    (@media(max-width:640px){nav ul{display:none}}), а гамбургер-кнопки
    или другого способа открыть его в JS нет — на мобильном ссылки навигации
    просто не существуют для пользователя (сайт одностраничный, скроллить
    можно вручную, но прямых переходов по разделам нет)."""
    open_home(mobile_driver)
    assert not is_nav_list_visible(mobile_driver)

    toggle_candidates = [
        b for b in mobile_driver.find_elements(By.CSS_SELECTOR, "button, [class*='toggle'], [class*='burger'], [class*='menu-btn']")
        if b.is_displayed()
    ]
    assert not toggle_candidates, (
        "Найдена кнопка, похожая на мобильное меню — если это и есть тот тоггл, "
        "тест выше нужно обновить, чтобы проверять открытие меню через неё"
    )


# ── Внешние ссылки (Instagram, email) ─────────────────────────────────────────

def test_all_instagram_links_point_to_correct_handle(driver):
    open_home(driver)
    links = instagram_links(driver)
    assert links, "Ссылки на Instagram не найдены на странице"
    for link in links:
        assert link.get_attribute("href").rstrip("/") == INSTAGRAM_HANDLE_URL.rstrip("/"), (
            f"Ссылка на Instagram ведёт не туда: {link.get_attribute('href')!r}"
        )
        assert link.get_attribute("target") == "_blank", "Внешняя ссылка на Instagram должна открываться в новой вкладке"
        assert "noopener" in (link.get_attribute("rel") or ""), (
            "Внешняя ссылка на Instagram должна иметь rel='noopener' (защита от reverse tabnabbing)"
        )


def test_mailto_link_present_and_well_formed(driver):
    open_home(driver)
    link = mailto_link(driver)
    assert link is not None, "Ссылка mailto: не найдена"
    assert link.get_attribute("href").startswith("mailto:")


def test_mailto_href_and_visible_placeholder_are_consistent(driver):
    """Пограничный случай, важный именно для этого пре-лонча: видимый
    текст ссылки email сейчас '[EMAIL]' (плейсхолдер), а href уже указывает
    на настоящий на вид адрес 'mailto:hello@example.com'. Если при
    заполнении контента поменять только видимый текст (что и предлагает
    README: 'search the code for those markers'), а не href — письма
    будут уходить на чужой домен, а не туда, куда ожидает автор."""
    open_home(driver)
    link = mailto_link(driver)
    href = link.get_attribute("href")
    visible_text = link.text.strip()

    if "[EMAIL]" in visible_text:
        assert "example.com" not in href, (
            "href='mailto:...' уже указывает на правдоподобный, но чужой домен "
            f"({href!r}), при этом видимый текст ещё плейсхолдер {visible_text!r} — "
            "высокий риск, что при заполнении контента поменяют только текст, "
            "и реальные письма будут уходить в пустоту"
        )


# ── Контент пре-лонча ──────────────────────────────────────────────────────────

def test_placeholder_markers_still_present_before_launch(driver):
    """Намеренно фиксирует ТЕКУЩЕЕ состояние (сайт не готов к запуску):
    [LOCATION] и [EMAIL] ещё не заменены реальным контентом (адрес
    студии сознательно отложен на будущее, реальный booking email пока
    не предоставлен). [BIO] и [PHOTO] уже заполнены реальным контентом
    2026-08-04 — их отсутствие здесь ожидаемо, не баг.

    Когда [LOCATION]/[EMAIL] тоже заполнят, этот тест должен начать
    падать — это сигнал убрать/инвертировать его, а не 'фиксить'."""
    open_home(driver)
    found = placeholder_markers_in_body(driver)
    assert set(found) == {"[LOCATION]", "[EMAIL]"}, (
        f"Ожидались только [LOCATION] и [EMAIL] как оставшиеся плейсхолдеры, найдено: {found}"
    )


def test_bio_and_photo_placeholders_are_filled(driver):
    """Симметричный тест к предыдущему: [BIO] и [PHOTO] должны БЫТЬ
    заполнены — если кто-то откатит контент обратно на плейсхолдер,
    здесь это будет видно."""
    open_home(driver)
    found = placeholder_markers_in_body(driver)
    assert "[BIO]" not in found
    assert "[PHOTO]" not in found


# ── Favicon / соцсети (Open Graph, Twitter Card) ──────────────────────────────

def test_favicon_present(driver):
    open_home(driver)
    link = favicon_link(driver)
    assert link is not None, "Тег <link rel='icon'> не найден"
    assert link.get_attribute("href"), "Favicon есть в разметке, но href пустой"


def test_open_graph_tags_present_and_consistent(driver):
    open_home(driver)
    assert meta_content(driver, "property", "og:title")
    assert meta_content(driver, "property", "og:description")
    og_image = meta_content(driver, "property", "og:image")
    assert og_image and og_image.startswith("https://"), (
        f"og:image должен быть абсолютным HTTPS URL (соцсети не подтягивают относительные), получено: {og_image!r}"
    )


def test_twitter_card_tags_present(driver):
    open_home(driver)
    assert meta_content(driver, "name", "twitter:card") == "summary_large_image"
    assert meta_content(driver, "name", "twitter:title")
    assert meta_content(driver, "name", "twitter:image")


# ── Галерея (реальные фото) ────────────────────────────────────────────────────

def test_gallery_shows_eight_real_photos_without_broken_images(driver):
    open_home(driver)
    images = gallery_images(driver)
    assert len(images) == 8, f"Ожидалось 8 фото в галерее, найдено {len(images)}"

    for img in images:
        natural_width = driver.execute_script("return arguments[0].naturalWidth", img)
        assert natural_width > 0, f"Изображение не загрузилось (broken): {img.get_attribute('src')!r}"
        assert img.get_attribute("alt"), f"У изображения нет alt-текста: {img.get_attribute('src')!r}"


# ── Скролл-reveal анимация ─────────────────────────────────────────────────────

def test_scroll_reveal_elements_become_visible_on_scroll(driver):
    open_home(driver)
    reveals = reveal_elements(driver)
    assert reveals, "Элементы с классом .reveal не найдены"

    target = reveals[-1]
    assert not has_reveal_class_active(target), (
        "Элемент .reveal в самом низу страницы не должен быть виден ('in') до скролла"
    )

    scroll_to(driver, target)
    time.sleep(1)
    assert has_reveal_class_active(target), (
        "После скролла к элементу .reveal должен добавиться класс 'in' (IntersectionObserver)"
    )
