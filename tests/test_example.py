"""
示例测试用例 — 演示 Allure 装饰器和 Page Object 基本用法。
"""

import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages import BaiduHomePage


@allure.feature("百度搜索")
@pytest.mark.skip(reason="不需要")
class TestBaiduSearch:

    @allure.story("首页加载")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.skip(reason="不需要")
    def test_home_page_title(self, driver: WebDriver):
        """验证百度首页标题"""
        page = BaiduHomePage(driver).open()
        assert "百度" in page.page_title(), f"Unexpected title: {page.page_title()}"

    @allure.story("关键词搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.skip(reason="不需要")
    def test_search_keyword(self, driver: WebDriver):
        """搜索关键词并验证结果页出现"""
        page = BaiduHomePage(driver).open()
        result_page = page.search("Selenium")

        stats = result_page.get_result_stats()
        allure.attach(stats, name="搜索结果统计", attachment_type=allure.attachment_type.TEXT)

        assert result_page.result_count() > 0, "搜索结果为空"

    @allure.story("搜索框可见性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.p2
    @pytest.mark.skip(reason="不需要")
    def test_search_input_visible(self, driver: WebDriver):
        """验证搜索框在首页可见"""
        page = BaiduHomePage(driver).open()
        assert page.is_visible(*page.SEARCH_INPUT), "搜索框不可见"


@allure.feature("演示 — 失败场景")
class TestFailureDemo:
    @pytest.mark.skip(reason="不需要")
    @allure.story("故意失败以演示截图")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_intentional_fail(self, driver: WebDriver):
        """此用例会失败，用于演示 Allure 自动截图功能"""
        page = BaiduHomePage(driver).open()
        # 故意断言一个不可能的值 — 只是为了演示失败截图
        assert "PAGE_TITLE_NEVER_MATCHES" in page.page_title(), \
            "Demo: 此失败用于验证 Allure 截图附加"
