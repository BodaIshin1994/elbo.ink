import pytest
from selenium import webdriver


@pytest.fixture(scope="module")
def driver(request):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    d = webdriver.Chrome(options=options)
    yield d
    if not request.config.getoption("--keep-browser-open"):
        d.quit()


def pytest_addoption(parser):
    parser.addoption(
        "--keep-browser-open",
        action="store_true",
        default=False,
        help="Не закрывать браузер после прогона (для отладки).",
    )


@pytest.fixture(scope="module")
def mobile_driver(request):
    """Отдельный драйвер с мобильным viewport — нав-меню на десктопе и
    мобильном ведёт себя по-разному (см. CSS @media(max-width:640px))."""
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=375,812")
    d = webdriver.Chrome(options=options)
    yield d
    if not request.config.getoption("--keep-browser-open"):
        d.quit()
