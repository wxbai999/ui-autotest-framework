"""
Allure 辅助工具 — 步骤包装、截图附加。
"""

from __future__ import annotations

from typing import Dict, List, Union

import allure
from selenium.webdriver.remote.webdriver import WebDriver


def attach_screenshot(driver: WebDriver, name: str = "screenshot") -> None:
    """截取当前页面并附加到 Allure 报告"""
    png = driver.get_screenshot_as_png()
    allure.attach(png, name=name, attachment_type=allure.attachment_type.PNG)


def attach_text(content: str, name: str = "info") -> None:
    """附加文本到 Allure 报告（如请求/响应数据）"""
    allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_json(data: Union[Dict, List], name: str = "data") -> None:
    """附加 JSON 到 Allure 报告"""
    import json
    allure.attach(
        json.dumps(data, ensure_ascii=False, indent=2),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )
