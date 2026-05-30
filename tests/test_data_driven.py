"""
数据驱动测试 — 使用 pytest.mark.parametrize 从 YAML/JSON/Excel 加载数据。
"""

import os

import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages import BaiduHomePage
from utils.data_loader import load_test_data

# ------------------------------------------------------------
# 从 YAML 文件加载测试数据
# ------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
YAML_DATA = load_test_data(os.path.join(DATA_DIR, "test_data.yaml"))


@allure.feature("百度搜索 — 数据驱动")
class TestBaiduSearchDataDriven:

    @allure.story("多关键词搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "case",
        YAML_DATA,
        ids=[c.get("case_name", c.get("keyword", "unknown")) for c in YAML_DATA],
    )
    @pytest.mark.skip(reason="不需要")
    def test_search_multiple_keywords(self, driver: WebDriver, case: dict):
        """使用 YAML 数据驱动 — 多关键词搜索验证"""
        keyword = case["keyword"]
        expected_in_title = case.get("expected_in_title", keyword)

        allure.dynamic.title(f"搜索「{keyword}」— 期望标题含「{expected_in_title}」")
        allure.attach(
            str(case), name="测试数据", attachment_type=allure.attachment_type.JSON
        )

        page = BaiduHomePage(driver).open()
        result_page = page.search(keyword)

        stats_text = result_page.get_result_stats()
        assert stats_text, "搜索结果统计文本为空"
        assert result_page.result_count() > 0, f"搜索「{keyword}」无结果"


# ------------------------------------------------------------
# 直接硬编码参数化 — 不依赖外部文件
# ------------------------------------------------------------
@allure.feature("参数化示例")
class TestParametrizeInline:

    @pytest.mark.skip(reason="不需要")
    @allure.story("内联参数化")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "keyword,expected_min_results",
        [
            ("Python", 5),
            ("Pytest", 3),
            ("Selenium WebDriver", 3),
        ],
        ids=["Python", "Pytest", "Selenium"],
    )
    def test_inline_params(self, driver: WebDriver, keyword: str, expected_min_results: int):
        """演示 pytest 原生参数化（不依赖外部文件）"""
        page = BaiduHomePage(driver).open()
        result_page = page.search(keyword)

        count = result_page.result_count()
        allure.attach(
            f"关键词: {keyword}, 结果数: {count}",
            name="搜索摘要",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert count >= expected_min_results, \
            f"搜索「{keyword}」结果数 {count} < 期望 {expected_min_results}"
