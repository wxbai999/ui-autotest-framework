import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from config import settings
from utils.logger import logger
from .base_page import BasePage


class RobotserviceLoginPage(BasePage):
    """登录页"""

    URL = "https://tester-op-ui.uditech.com.cn/#/login?redirect=/portal"

    # 用户名输入框
    USERNAME_INPUT = (By.XPATH, '//*[@id="app"]//input[@type="text"][1]')

    # 密码输入框
    PASSWORD_INPUT = (By.XPATH, '//*[@id="app"]//input[@type="password"]')

    # 验证码输入框
    CERCODE_INPUT = (By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[2]/div/form/div[4]/div/div[1]/input')

    # 登录按钮
    LOGIN_BUTTON = (By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[2]/div/form/button/span')

    # Toast 错误提示
    TOAST = (By.XPATH, '//*[contains(@class,"el-message")]//p | //*[@id="message_2"]/p')

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    # ========== 操作 ==========

    @allure.step("打开登录页")
    def open(self) -> "RobotserviceLoginPage":
        self.navigate(self.URL)
        return self

    @allure.step("登录: {username}")
    def do_login(self, username: str, password: str, cer_code: str) -> "RobotserviceLoginPage":
        """执行登录操作，停留在当前页（不假设成功或失败）"""
        self.type(*self.USERNAME_INPUT, username)
        self.type(*self.PASSWORD_INPUT, password)
        self.type(*self.CERCODE_INPUT, cer_code)
        self.click(*self.LOGIN_BUTTON)
        return self

    # ========== 结果判断 ==========

    @allure.step("检查是否登录成功")
    def is_login_successful(self, timeout: int = 5) -> bool:
        """登录成功 → URL 跳出了 /login 或首页元素出现"""
        try:
            self.wait_present(*RobotServiceFrontPage.RESULT_STATS, timeout=timeout)
            logger.info("登录成功：首页元素已出现")
            return True
        except Exception:
            logger.info("登录可能失败：首页元素未出现")
            return False

    @allure.step("获取 Toast 错误提示")
    def get_error_message(self) -> str:
        return self.wait_visible(*self.TOAST, timeout=8).text

    @allure.step("进入首页")
    def go_to_front_page(self) -> "RobotServiceFrontPage":
        """登录成功后切换到首页 Page Object"""
        return RobotServiceFrontPage(self.driver)


class RobotServiceFrontPage(BasePage):
    """首页"""

    RESULT_STATS = (By.XPATH, '//*[@id="app"]//a/span[contains(text(),"运维")] | //*[@id="app"]//span[contains(@class,"title")]')

    @allure.step("获取首页标题")
    def get_result_stats(self) -> str:
        return self.wait_visible(*self.RESULT_STATS).text
