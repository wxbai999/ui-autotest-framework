"""
WebDriver 工厂 — 统一创建/销毁浏览器实例，支持本地和 Grid 两种模式。

Driver 查找优先级:
    1. 显式路径 (CHROME_DRIVER_PATH / FIREFOX_DRIVER_PATH / EDGE_DRIVER_PATH)
    2. 统一目录 + 默认文件名 (DRIVER_PATH + chromedriver.exe / geckodriver.exe / ...)
    3. webdriver-manager 在线下载
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from config import settings
from utils.logger import logger


# ---- 各浏览器默认 driver 文件名 ----
_DRIVER_NAMES = {
    "chrome": "chromedriver.exe" if sys.platform == "win32" else "chromedriver",
    "firefox": "geckodriver.exe" if sys.platform == "win32" else "geckodriver",
    "edge": "msedgedriver.exe" if sys.platform == "win32" else "msedgedriver",
}

# 显式路径配置 key 映射
_EXPLICIT_KEYS = {
    "chrome": "CHROME_DRIVER_PATH",
    "firefox": "FIREFOX_DRIVER_PATH",
    "edge": "EDGE_DRIVER_PATH",
}


def _resolve_driver_path(browser: str) -> Optional[str]:
    """
    按优先级查找本地 driver 可执行文件，找不到返回 None。

    优先级:
        1. 显式指定路径 (CHROME_DRIVER_PATH 等)
        2. settings.DRIVER_PATH + 默认文件名
    """
    b = browser.lower()

    # 1) 显式路径
    explicit_key = _EXPLICIT_KEYS.get(b)
    if explicit_key:
        explicit = getattr(settings, explicit_key, "")
        if explicit and os.path.isfile(explicit):
            return explicit

    # 2) 统一目录 + 默认文件名
    driver_dir = settings.DRIVER_PATH
    if driver_dir:
        candidate = os.path.join(driver_dir, _DRIVER_NAMES.get(b, ""))
        if os.path.isfile(candidate):
            return candidate

    return None


def _create_local_driver(browser: str, headless: bool) -> webdriver.Remote:
    """创建本地 WebDriver"""
    b = browser.lower()

    # 尝试找到本地 driver
    local_path = _resolve_driver_path(b)

    if b == "chrome":
        opts = ChromeOptions()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        if local_path:
            logger.info(f"Using local ChromeDriver: {local_path}")
            driver = webdriver.Chrome(service=ChromeService(local_path), options=opts)
        else:
            logger.info("Downloading ChromeDriver via webdriver-manager ...")
            from webdriver_manager.chrome import ChromeDriverManager
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=opts,
            )

    elif b == "firefox":
        opts = FirefoxOptions()
        if headless:
            opts.add_argument("--headless")
        opts.add_argument(f"--width={settings.WINDOW_WIDTH}")
        opts.add_argument(f"--height={settings.WINDOW_HEIGHT}")

        if local_path:
            logger.info(f"Using local GeckoDriver: {local_path}")
            driver = webdriver.Firefox(service=FirefoxService(local_path), options=opts)
        else:
            logger.info("Downloading GeckoDriver via webdriver-manager ...")
            from webdriver_manager.firefox import GeckoDriverManager
            driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=opts,
            )

    elif b == "edge":
        opts = EdgeOptions()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
        opts.add_argument("--no-sandbox")

        if local_path:
            logger.info(f"Using local EdgeDriver: {local_path}")
            driver = webdriver.Edge(service=EdgeService(local_path), options=opts)
        else:
            logger.info("Downloading EdgeDriver via webdriver-manager ...")
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            driver = webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=opts,
            )

    else:
        raise ValueError(f"Unsupported browser: {browser}. Use chrome / firefox / edge.")

    driver.implicitly_wait(settings.IMPLICIT_WAIT)
    driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
    return driver


def _create_remote_driver(browser: str, headless: bool) -> webdriver.Remote:
    """创建远程 WebDriver（连接 Selenium Grid）"""
    b = browser.lower()
    if b == "chrome":
        opts = ChromeOptions()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
    elif b == "firefox":
        opts = FirefoxOptions()
        if headless:
            opts.add_argument("--headless")
    elif b == "edge":
        opts = EdgeOptions()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    driver = webdriver.Remote(
        command_executor=settings.GRID_URL,
        options=opts,
    )
    driver.implicitly_wait(settings.IMPLICIT_WAIT)
    driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
    return driver


def create_driver(browser: Optional[str] = None,
                  headless: Optional[bool] = None) -> webdriver.Remote:
    """
    创建 WebDriver 实例。

    Args:
        browser:  浏览器类型，默认从 settings 读取
        headless: 是否无头，默认从 settings 读取

    Returns:
        WebDriver 实例
    """
    browser = browser or settings.BROWSER
    headless = headless if headless is not None else settings.HEADLESS

    if settings.GRID_ENABLED:
        return _create_remote_driver(browser, headless)
    return _create_local_driver(browser, headless)


def quit_driver(driver: webdriver.Remote) -> None:
    """安全退出 WebDriver"""
    if driver:
        try:
            driver.quit()
        except Exception:
            pass
