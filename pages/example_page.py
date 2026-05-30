"""
百度首页 Page Object — 演示定位和操作。

元素定位参考（实测 2024-2025 百度首页）:
    搜索框:   input#kw  (name="wd", class="s_ipt")
    搜索按钮: input#su  (type="submit", class="bg s_btn")
    结果统计: span.nums_text, 或 .nums
    结果条目: div.result h3 a
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from .base_page import BasePage


class BaiduHomePage(BasePage):
    """百度首页"""

    URL = "https://www.baidu.com"

    # 搜索输入框 — id="kw" 至今未变
    SEARCH_INPUT = (By.ID, "chat-textarea")

    # 搜索按钮 — id="su"
    SEARCH_BUTTON = (By.ID, "chat-submit-button")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @allure.step("打开百度首页")
    def open(self) -> "BaiduHomePage":
        self.navigate(self.URL)
        return self

    @allure.step("搜索关键词: {keyword}")
    def search(self, keyword: str) -> "BaiduSearchResultPage":
        self.type(*self.SEARCH_INPUT, keyword)
        self.click(*self.SEARCH_BUTTON)
        return BaiduSearchResultPage(self.driver)


class BaiduSearchResultPage(BasePage):
    """百度搜索结果页"""

    # 结果统计 — 页面可能有两种形式
    RESULT_STATS = (By.CSS_SELECTOR, ".nums, .nums_text, span.nums")

    # 搜索结果链接
    RESULTS = (By.CSS_SELECTOR, ".result h3 a, .c-container h3 a")

    @allure.step("获取搜索结果统计文本")
    def get_result_stats(self) -> str:
        return self.wait_visible(*self.RESULT_STATS).text

    @allure.step("获取结果数量")
    def result_count(self) -> int:
        return len(self.find_all(*self.RESULTS))
