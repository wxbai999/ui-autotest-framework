"""
ChromeDriver 国内镜像下载工具
=============================
从 npmmirror.com（阿里镜像）下载与当前 Chrome 版本匹配的 ChromeDriver，
保存到 drivers/ 目录（框架自带 DRIVER_PATH 默认值）。

用法:
    python scripts/download_driver.py               # 下载 ChromeDriver
    python scripts/download_driver.py --browser firefox  # 下载 GeckoDriver
    python scripts/download_driver.py --mirror huawei     # 使用华为镜像
"""

import os
import sys
import zipfile
import tempfile
import shutil

# Python 3.7 兼容
try:
    from urllib.request import urlopen, urlretrieve
except ImportError:
    from urllib import urlopen, urlretrieve

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER_DIR = os.path.join(ROOT_DIR, "drivers")

# ---- 镜像源 ----
MIRRORS = {
    "npmmirror": {
        "chrome": "https://registry.npmmirror.com/-/binary/chromedriver/",
        "firefox": "https://registry.npmmirror.com/-/binary/geckodriver/",
    },
    "huawei": {
        "chrome": "https://mirrors.huaweicloud.com/chromedriver/",
        "firefox": "https://mirrors.huaweicloud.com/geckodriver/",
    },
}

# 各 Chrome 版本对应的 ChromeDriver 版本（常用映射，按需补充）
# 完整列表见: https://registry.npmmirror.com/-/binary/chromedriver/
CHROME_TO_DRIVER = {
    "148": "148.0.7778.181",
    "128": "128.0.6613.137",
    "127": "127.0.6533.119",
    "126": "126.0.6478.182",
    "125": "125.0.6422.141",
    "124": "124.0.6367.207",
    "123": "123.0.6312.122",
    "122": "122.0.6261.128",
    "121": "121.0.6167.184",
    "120": "120.0.6099.109",
    "119": "119.0.6045.105",
    "118": "118.0.5993.70",
    "117": "117.0.5938.149",
    "116": "116.0.5845.96",
    "115": "115.0.5790.170",
    "114": "114.0.5735.90",
    "113": "113.0.5672.63",
    "112": "112.0.5615.49",
    "111": "111.0.5563.64",
    "110": "110.0.5481.77",
    "109": "109.0.5414.74",
}


def get_chrome_version() -> str:
    """探测本机 Chrome 主版本号"""
    import subprocess

    # Windows: 读注册表
    if sys.platform == "win64":
        paths = [
            r"reg query HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon /v version",
            r"reg query HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome /v Version",
            r"reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome /v Version",
        ]
        for cmd in paths:
            try:
                out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
                out = out.decode(errors="ignore")
                for token in out.split():
                    if token.count(".") >= 2 and token[0].isdigit():
                        major = token.split(".")[0]
                        print(f"[INFO] 检测到 Chrome 版本: {token} → 主版本 {major}")
                        return major
            except Exception:
                continue

    # macOS
    if sys.platform == "darwin":
        try:
            out = subprocess.check_output(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                stderr=subprocess.DEVNULL,
            ).decode()
            major = out.strip().split()[-1].split(".")[0]
            print(f"[INFO] 检测到 Chrome 版本: {out.strip()} → 主版本 {major}")
            return major
        except Exception:
            pass

    # Linux
    try:
        out = subprocess.check_output(["google-chrome", "--version"], stderr=subprocess.DEVNULL).decode()
        major = out.strip().split()[-1].split(".")[0]
        print(f"[INFO] 检测到 Chrome 版本: {out.strip()} → 主版本 {major}")
        return major
    except Exception:
        pass

    print("[WARN] 无法自动检测 Chrome 版本")
    return ""


def download_driver(browser: str = "chrome", mirror: str = "npmmirror") -> str:
    """
    从镜像下载 driver。

    Args:
        browser: chrome | firefox
        mirror:  npmmirror | huawei

    Returns:
        下载后的可执行文件路径
    """
    if sys.platform != "win64":
        print("[ERROR] 此下载脚本仅支持 Windows。其他平台请手动下载。")
        print("  macOS: brew install chromedriver")
        print("  Linux: apt install chromium-chromedriver")
        sys.exit(1)

    mirror_url = MIRRORS.get(mirror, MIRRORS["npmmirror"])
    base_url = mirror_url.get(browser)
    if not base_url:
        print(f"[ERROR] 镜像 {mirror} 不支持浏览器 {browser}")
        sys.exit(1)

    driver_name = {
        "chrome": "chromedriver",
        "firefox": "geckodriver",
    }.get(browser, browser)

    # 确定版本
    if browser == "chrome":
        chrome_ver = get_chrome_version()
        if chrome_ver not in CHROME_TO_DRIVER:
            print(f"[ERROR] Chrome {chrome_ver}.x 未在映射表中，请手动指定版本:")
            print(f"  查看可用版本: {base_url}")
            print(f"  或手动下载后放到 {DRIVER_DIR}")
            sys.exit(1)
        driver_ver = CHROME_TO_DRIVER[chrome_ver]
        url = f"{base_url}{driver_ver}/chromedriver_win64.zip"
    else:
        # Firefox: 直接用最新
        url = f"{base_url}latest/geckodriver-win64.zip"
        driver_ver = "latest"

    print(f"[INFO] 下载 {browser} driver 版本: {driver_ver}")
    print(f"[INFO] URL: {url}")

    os.makedirs(DRIVER_DIR, exist_ok=True)

    # 下载 zip
    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, "driver.zip")

    try:
        print("[INFO] 下载中 ...")
        urlretrieve(url, zip_path)
        print("[INFO] 下载完成，解压中 ...")

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)

        # 找到 driver 可执行文件
        src = None
        for root, _, files in os.walk(tmp_dir):
            for f in files:
                if f.lower().startswith(driver_name) and f.endswith(".exe"):
                    src = os.path.join(root, f)
                    break
            if src:
                break

        if not src:
            print("[ERROR] 解压后未找到 driver 可执行文件")
            print(f"  目录内容: {os.listdir(tmp_dir)}")
            sys.exit(1)

        dst = os.path.join(DRIVER_DIR, f"{driver_name}.exe")
        shutil.move(src, dst)
        print(f"[OK] Driver 已保存: {dst}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return dst


def main():
    import argparse

    parser = argparse.ArgumentParser(description="从国内镜像下载 WebDriver")
    parser.add_argument("--browser", default="chrome", choices=["chrome", "firefox"],
                        help="浏览器类型 (默认 chrome)")
    parser.add_argument("--mirror", default="npmmirror", choices=["npmmirror", "huawei"],
                        help="镜像源 (默认 npmmirror)")
    args = parser.parse_args()

    download_driver(args.browser, args.mirror)
    print(f"\n[INFO] 现在可以直接运行测试了:")
    print(f"       python scripts/run_tests.py smoke")


if __name__ == "__main__":
    main()
