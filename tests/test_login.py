"""
运维平台登录测试 — 数据驱动（从 JSON 加载用例数据）。

expect_success = true  → 登录成功后验证首页标题
expect_success = false → 登录失败后验证错误提示
"""

import os

import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages import RobotserviceLoginPage
from utils.data_loader import load_test_data

# ------------------------------------------------------------
# 从 JSON 加载登录测试数据
# ------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
JSON_DATA = load_test_data(os.path.join(DATA_DIR, "user_data.json"))


@allure.feature("运维平台登录")
class TestRobotPlatformLogin:

    @allure.story("登录验证")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "case",
        JSON_DATA,
        ids=[c.get("case_name", c.get("username", "?")) for c in JSON_DATA],
    )
    def test_login(self, driver: WebDriver, case: dict):
        """使用 JSON 数据驱动验证登录功能（成功 / 失败两分支）"""
        username = case["username"]
        password = case["password"]
        cer_code = case["cer_code"]
        expected = case["result"]
        expect_success = case.get("expect_success", True)

        allure.dynamic.title(
            f"{'✅' if expect_success else '❌'} 登录「{username}」→ 期望{'成功' if expect_success else '失败'}"
        )
        allure.attach(
            str(case), name="测试数据", attachment_type=allure.attachment_type.JSON
        )

        # 打开登录页 → 执行登录
        login_page = RobotserviceLoginPage(driver).open()
        login_page.do_login(
            username=username,
            password=password,
            cer_code=cer_code,
        )

        if expect_success:
            # 登录成功 → 进入首页，验证标题
            assert login_page.is_login_successful(), (
                f"登录失败：预期成功，但首页元素未出现"
            )
            front_page = login_page.go_to_front_page()
            actual_title = front_page.get_result_stats()
            assert actual_title, "登录后页面标题为空"
            assert expected in actual_title, (
                f"首页标题不符 — 期望含「{expected}」，实际「{actual_title}」"
            )
        else:
            # 登录失败 → 验证错误提示
            error_msg = login_page.get_error_message()
            allure.attach(error_msg, name="错误提示", attachment_type=allure.attachment_type.TEXT)
            assert expected in error_msg, (
                f"错误提示不符 — 期望含「{expected}」，实际「{error_msg}」"
            )
