"""
Page Object 基类 — 封装通用 Selenium 操作，自动附带 Allure 步骤和失败截图。
"""

from __future__ import annotations

from typing import Any, List, Optional

import allure
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings
from utils.logger import logger
from utils.allure_utils import attach_screenshot


class BasePage:
    """所有 Page Object 的父类"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.EXPLICIT_WAIT)
        self._timeout = settings.EXPLICIT_WAIT

    # ========== 元素定位 ==========

    def find(self, by: str, locator: str) -> WebElement:
        """查找单个元素（立即返回，不等待可见性）"""
        return self.driver.find_element(by, locator)

    def find_all(self, by: str, locator: str) -> list[WebElement]:
        """查找所有匹配元素"""
        return self.driver.find_elements(by, locator)

    def wait_visible(self, by: str, locator: str, timeout: Optional[int] = None) -> WebElement:
        """等待元素可见后返回"""
        t = timeout or self._timeout
        return WebDriverWait(self.driver, t).until(
            EC.visibility_of_element_located((by, locator))
        )

    def wait_clickable(self, by: str, locator: str, timeout: Optional[int] = None) -> WebElement:
        """等待元素可点击后返回"""
        t = timeout or self._timeout
        return WebDriverWait(self.driver, t).until(
            EC.element_to_be_clickable((by, locator))
        )

    def wait_present(self, by: str, locator: str, timeout: Optional[int] = None) -> WebElement:
        """等待元素出现在 DOM 中（不必可见）"""
        t = timeout or self._timeout
        return WebDriverWait(self.driver, t).until(
            EC.presence_of_element_located((by, locator))
        )

    def is_visible(self, by: str, locator: str, timeout: int = 1) -> bool:
        """判断元素是否可见"""
        try:
            self.wait_visible(by, locator, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    # ========== 常用操作（带 Allure 步骤） ==========

    @allure.step("点击元素: {locator}")
    def click(self, by: str, locator: str) -> None:
        self.wait_clickable(by, locator).click()

    @allure.step("输入文本到 {locator}: {text}")
    def type(self, by: str, locator: str, text: str) -> None:
        el = self.wait_visible(by, locator)
        el.clear()
        el.send_keys(text)

    @allure.step("获取 {locator} 文本")
    def get_text(self, by: str, locator: str) -> str:
        return self.wait_visible(by, locator).text

    @allure.step("获取 {locator} 属性 {attr}")
    def get_attr(self, by: str, locator: str, attr: str) -> Optional[str]:
        return self.wait_present(by, locator).get_attribute(attr)

    @allure.step("导航到: {url}")
    def navigate(self, url: str) -> None:
        self.driver.get(url)

    @allure.step("获取当前 URL")
    def current_url(self) -> str:
        return self.driver.current_url

    @allure.step("获取页面标题")
    def page_title(self) -> str:
        return self.driver.title

    @allure.step("执行 JS: {script}")
    def execute_js(self, script: str, *args: Any) -> Any:
        return self.driver.execute_script(script, *args)

    @allure.step("滚动到元素: {locator}")
    def scroll_to(self, by: str, locator: str) -> None:
        el = self.wait_present(by, locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)

    @allure.step("截图: {name}")
    def screenshot(self, name: str = "manual") -> None:
        attach_screenshot(self.driver, name)
