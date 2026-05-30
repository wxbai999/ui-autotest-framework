"""
Pytest 全局配置 — WebDriver fixture、命令行参数、失败截图 Hook。
"""

import pytest
import allure
from selenium.webdriver.remote.webdriver import WebDriver

from config import settings
from utils.driver_factory import create_driver, quit_driver
from utils.logger import logger
from utils.allure_utils import attach_screenshot


# ============================================================
# 命令行参数
# ============================================================

def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="浏览器类型: chrome / firefox / edge",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=None,
        help="启用无头模式",
    )



# ============================================================
# 全局 Fixture
# ============================================================

@pytest.fixture(scope="function")
def driver(request: pytest.FixtureRequest) -> WebDriver:
    """
    WebDriver fixture — function 级别（并行安全）。

    使用:
        def test_foo(driver):
            driver.get("https://example.com")
            assert "Example" in driver.title
    """
    browser = request.config.getoption("--browser") or settings.BROWSER
    headless = request.config.getoption("--headless")
    if headless is None:
        headless = settings.HEADLESS

    logger.info(f"Creating WebDriver: browser={browser}, headless={headless}")
    driver = create_driver(browser=browser, headless=headless)

    yield driver

    logger.info("Tearing down WebDriver")
    quit_driver(driver)


@pytest.fixture(scope="session")
def base_url() -> str:
    """被测系统 BASE_URL"""
    return settings.BASE_URL


# ============================================================
# 失败自动截图 Hook
# ============================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """测试失败时自动截图并附加到 Allure"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        if settings.SCREENSHOT_ON_FAILURE:
            driver = item.funcargs.get("driver", None)
            if driver:
                try:
                    name = f"失败截图_{item.name}"
                    attach_screenshot(driver, name)
                except Exception as e:
                    logger.warning(f"截图失败: {e}")
