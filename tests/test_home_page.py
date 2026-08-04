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
from selenium.webdriver.support.ui import WebDriverWait

from framework.helpers import open_home
from pages.home_page import (
    INSTAGRAM_HANDLE_URL,
    SECTION_IDS,
    copyright_year_text,
    favicon_link,
    gallery_images,
    has_horizontal_overflow,
    has_reveal_class_active,
    html_lang_attribute,
    i18n_text,
    instagram_links,
    is_nav_list_visible,
    lang_toggle_button,
    mailto_link,
    meta_content,
    nav_links,
    placeholder_markers_in_body,
    reserve_button,
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


def test_nav_no_longer_has_direct_instagram_link(driver):
    """Прямая ссылка на Instagram в nav убрана в пользу кнопки 'Reserve'
    (см. test_reserve_button_scrolls_to_book_section) — Instagram остаётся
    доступен через CTA/footer/work-секцию, просто не в самом nav."""
    open_home(driver)
    nav_instagram = [
        a for a in driver.find_elements(By.CSS_SELECTOR, "nav a[href*='instagram.com']") if a.is_displayed()
    ]
    assert not nav_instagram, "В nav не должно быть прямой ссылки на Instagram"


def test_reserve_button_present_with_correct_label(driver):
    open_home(driver)
    btn = reserve_button(driver)
    assert btn.is_displayed()
    assert driver.execute_script("return arguments[0].textContent", btn).strip() == "Reserve"


def test_reserve_button_scrolls_to_book_section(driver):
    """Порог 400px, а не 0/малое число: scrollIntoView с fixed-nav сверху
    и smooth-скроллом останавливается не точно у верхнего края (~240px в
    ручной проверке) — важно, что секция реально попала в область
    видимости, а не точный пиксель остановки."""
    open_home(driver)
    book_top_before = driver.execute_script(
        "return document.getElementById('book').getBoundingClientRect().top"
    )
    reserve_button(driver).click()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(
            "return document.getElementById('book').getBoundingClientRect().top"
        ) < min(book_top_before, 400)
    )


def test_reserve_button_stays_visible_on_mobile(mobile_driver):
    """Как и #langToggle, кнопка резервации лежит вне <ul> и должна
    оставаться доступной на мобильном, где сам список пунктов меню
    скрыт."""
    open_home(mobile_driver)
    assert not is_nav_list_visible(mobile_driver)
    assert reserve_button(mobile_driver).is_displayed()


def test_no_horizontal_overflow_at_narrow_widths_in_either_language(mobile_driver):
    """Регрессионный guard: на 320px в турецкой локали был найден реальный
    баг — .cta ('Instagram'dan Randevu Al ↗') не помещался в ширину экрана
    из-за white-space:nowrap, и из-за этого 'раздувался' также nav
    (position:fixed;left:0;right:0;width:100% резолвится против containing
    block, который сам увеличивается при переполнении другого элемента).
    Исправлено 2026-08-04 медиа-запросом для .cta на <420px.

    mobile_driver.set_window_size здесь недостаточно (см. историю
    отладки — Chrome desktop не сужается ниже ~485px через обычный
    resize), поэтому используем настоящую эмуляцию через CDP."""
    mobile_driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "width": 320, "height": 800, "deviceScaleFactor": 2, "mobile": True,
    })
    open_home(mobile_driver)
    assert not has_horizontal_overflow(mobile_driver), "Горизонтальное переполнение на 320px (EN)"

    lang_toggle_button(mobile_driver).click()
    time.sleep(0.5)
    assert not has_horizontal_overflow(mobile_driver), "Горизонтальное переполнение на 320px (TR)"

    # уборка: сбрасываем на английский и снимаем эмуляцию устройства
    lang_toggle_button(mobile_driver).click()
    mobile_driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})


def test_mobile_viewport_hides_nav_with_no_alternative_toggle(mobile_driver):
    """Зафиксированное текущее поведение (не однозначный баг, но пробел
    UX): на ширине <640px meню навигации скрывается через CSS
    (@media(max-width:640px){nav ul{display:none}}), а гамбургер-кнопки
    или другого способа открыть его в JS нет — на мобильном ссылки навигации
    просто не существуют для пользователя (сайт одностраничный, скроллить
    можно вручную, но прямых переходов по разделам нет).

    #langToggle и #reserveBtn — реальные, отдельные фичи (переключатель
    языка, кнопка резервации, см. test_lang_toggle_button_stays_visible_on_mobile
    и test_reserve_button_stays_visible_on_mobile), намеренно исключены
    из проверки ниже — это не тоггл мобильного меню."""
    open_home(mobile_driver)
    assert not is_nav_list_visible(mobile_driver)

    excluded_ids = {"langToggle", "reserveBtn"}
    toggle_candidates = [
        b for b in mobile_driver.find_elements(By.CSS_SELECTOR, "button, [class*='toggle'], [class*='burger'], [class*='menu-btn']")
        if b.is_displayed() and b.get_attribute("id") not in excluded_ids
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


REAL_BOOKING_EMAIL = "Elbo.inkk@gmail.com"


def test_mailto_href_and_visible_text_match_real_email(driver):
    """Раньше здесь был пограничный случай пре-лонча: видимый текст был
    плейсхолдером '[EMAIL]', а href уже указывал на чужой домен
    example.com — риск, что при заполнении контента поменяют только
    текст, а не href. Реальный email добавлен 2026-08-04.

    Ссылка лежит внутри .contact-lines.reveal — элемент невидим для
    Selenium .text до срабатывания scroll-reveal (та же особенность, что
    и у .cta/галереи), поэтому текст берём через textContent, а не .text."""
    open_home(driver)
    link = mailto_link(driver)
    href = link.get_attribute("href")
    visible_text = driver.execute_script("return arguments[0].textContent", link).strip()

    assert href == f"mailto:{REAL_BOOKING_EMAIL}"
    assert visible_text.lower() == REAL_BOOKING_EMAIL.lower(), (
        f"Видимый текст ({visible_text!r}) должен совпадать с реальным email в href"
    )


# ── Контент пре-лонча ──────────────────────────────────────────────────────────

def test_only_location_placeholder_remains_before_launch(driver):
    """[BIO]/[PHOTO]/[EMAIL] уже заполнены реальным контентом. [LOCATION]
    заполнен текстом 'Istanbul'/'İstanbul' — это НЕ плейсхолдер-маркер
    (нет квадратных скобок), поэтому фактически на сайте сейчас не
    осталось ни одного незаполненного [MARKER]. Тест зафиксирован как
    'на будущее': если кто-то добавит новый [MARKER]-плейсхолдер и забудет
    его заполнить перед деплоем, это будет здесь замечено."""
    open_home(driver)
    found = placeholder_markers_in_body(driver)
    assert found == [], f"Остались незаполненные плейсхолдеры перед запуском: {found}"


def test_location_filled_with_istanbul(driver):
    open_home(driver)
    assert i18n_text(driver, "hero.meta.location").strip().endswith("Istanbul")
    assert i18n_text(driver, "studio.facts.location").strip().endswith("Istanbul")


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
    """Изображения галереи — loading='lazy', браузер не начинает их
    грузить, пока они не окажутся у видимой области, поэтому перед
    проверкой naturalWidth обязательно scrollIntoView + ожидание."""
    open_home(driver)
    images = gallery_images(driver)
    assert len(images) == 8, f"Ожидалось 8 фото в галерее, найдено {len(images)}"

    for img in images:
        scroll_to(driver, img)
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return arguments[0].complete && arguments[0].naturalWidth > 0", img)
        )
        assert img.get_attribute("alt"), f"У изображения нет alt-текста: {img.get_attribute('src')!r}"


# ── Скролл-reveal анимация ─────────────────────────────────────────────────────

# ── Переключатель языка (EN/TR) ────────────────────────────────────────────────
# Кнопка вынесена ИЗ <ul> в nav намеренно — иначе она пропадала бы вместе со
# всем меню на мобильном (см. test_mobile_viewport_hides_nav_with_no_alternative_toggle).
# Порядок важен: эти тесты идут последними в файле и переключают язык на
# живом сайте — более ранние тесты, чувствительные к видимому тексту
# (например test_nav_work_link_points_to_correct_section), должны запускаться
# раньше, чтобы не зависеть от того, на каком языке останавливается toggle.

def test_lang_toggle_defaults_to_english(driver):
    """nav a{text-transform:uppercase} — сравниваем в верхнем регистре,
    как и в test_nav_work_link_points_to_correct_section."""
    open_home(driver)
    assert html_lang_attribute(driver) == "en"
    assert lang_toggle_button(driver).text.strip() == "TR"
    assert i18n_text(driver, "nav.studio").upper() == "STUDIO"


def test_lang_toggle_switches_to_turkish_and_back(driver):
    open_home(driver)
    lang_toggle_button(driver).click()

    assert html_lang_attribute(driver) == "tr"
    assert lang_toggle_button(driver).text.strip() == "EN"
    assert i18n_text(driver, "nav.studio").upper() == "STÜDYO"
    assert i18n_text(driver, "nav.work").upper() == "İŞLER"

    lang_toggle_button(driver).click()
    assert html_lang_attribute(driver) == "en"
    assert i18n_text(driver, "nav.studio").upper() == "STUDIO"


def test_lang_toggle_choice_persists_across_reload(driver):
    open_home(driver)
    lang_toggle_button(driver).click()
    assert html_lang_attribute(driver) == "tr"

    open_home(driver)
    assert html_lang_attribute(driver) == "tr", (
        "Выбор языка должен сохраняться через localStorage между перезагрузками"
    )

    # уборка: возвращаем на английский, чтобы не влиять на порядок запусков
    lang_toggle_button(driver).click()
    assert html_lang_attribute(driver) == "en"


def test_lang_toggle_button_stays_visible_on_mobile(mobile_driver):
    """В отличие от остальных пунктов меню, переключатель языка находится
    вне <ul> и не должен пропадать на мобильной ширине."""
    open_home(mobile_driver)
    assert not is_nav_list_visible(mobile_driver)
    assert lang_toggle_button(mobile_driver).is_displayed(), (
        "Переключатель языка должен оставаться видимым на мобильном, даже когда сам список меню скрыт"
    )


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
