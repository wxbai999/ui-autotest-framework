"""
配置中心 — 通过环境变量 + 默认值统一管理所有配置项。

优先级: 环境变量 > .env 文件 > 默认值
"""

import os
from dotenv import load_dotenv

load_dotenv()  # 尝试加载项目根目录下的 .env


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except (TypeError, ValueError):
        return default


def _env_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")


class Settings:
    """全局配置单例"""

    # ---------- 被测系统 ----------
    # BASE_URL: str = _env("BASE_URL", "https://www.baidu.com")
    BASE_URL: str = _env("BASE_URL", "https://tester-op-ui.uditech.com.cn/#/login?redirect=/portal")
    # ---------- 浏览器 ----------
    BROWSER: str = _env("BROWSER", "chrome")          # chrome | firefox | edge
    HEADLESS: bool = _env_bool("HEADLESS", False)     # 无头模式
    WINDOW_WIDTH: int = _env_int("WINDOW_WIDTH", 1920)
    WINDOW_HEIGHT: int = _env_int("WINDOW_HEIGHT", 1080)

    # ---------- Driver 本地路径 ----------
    # 设置后优先使用本地 driver，跳过 webdriver-manager 在线下载
    # 例如: DRIVER_PATH=drivers  → 自动找 drivers/chromedriver.exe
    #       CHROME_DRIVER_PATH=C:\tools\chromedriver.exe → 直接指定
    DRIVER_PATH: str = _env("DRIVER_PATH", "drivers")
    CHROME_DRIVER_PATH: str = _env("CHROME_DRIVER_PATH", "")
    FIREFOX_DRIVER_PATH: str = _env("FIREFOX_DRIVER_PATH", "")
    EDGE_DRIVER_PATH: str = _env("EDGE_DRIVER_PATH", "")

    # ---------- Selenium Grid ----------
    GRID_ENABLED: bool = _env_bool("GRID_ENABLED", False)
    GRID_URL: str = _env("GRID_URL", "http://localhost:4444")

    # ---------- 超时 ----------
    IMPLICIT_WAIT: int = _env_int("IMPLICIT_WAIT", 5)
    EXPLICIT_WAIT: int = _env_int("EXPLICIT_WAIT", 10)
    PAGE_LOAD_TIMEOUT: int = _env_int("PAGE_LOAD_TIMEOUT", 30)

    # ---------- 重跑 ----------
    RERUNS: int = _env_int("RERUNS", 2)               # 失败重跑次数
    RERUNS_DELAY: int = _env_int("RERUNS_DELAY", 3)   # 重跑间隔（秒）

    # ---------- 并行 ----------
    WORKERS: str = _env("WORKERS", "auto")            # auto = CPU 核数, 或数字

    # ---------- 报告 ----------
    ALLURE_RESULTS_DIR: str = _env("ALLURE_RESULTS_DIR", "allure-results")

    # ---------- 截图 ----------
    SCREENSHOT_ON_FAILURE: bool = _env_bool("SCREENSHOT_ON_FAILURE", True)
    SCREENSHOT_DIR: str = _env("SCREENSHOT_DIR", "screenshots")


settings = Settings()
