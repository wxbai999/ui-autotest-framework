"""
跨平台测试运行器 — Windows / Linux / macOS 通用。

用法:
    python scripts/run_tests.py [模式]

模式:
    smoke        冒烟测试 (Chrome 无头, 串行, 重跑2次)
    regression   回归测试 (Chrome 无头, 4并行, 重跑2次)
    parallel     全量并行 (Chrome 无头, auto workers)
    headed       有界面调试 (Chrome, 不重跑)
    firefox      Firefox 无头
    custom       交互式自定义参数
"""

import os
import sys
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLURE_DIR = "allure-results"

PRESETS = {
    "smoke": [
        "tests/", "-m", "smoke",
        "--browser=chrome", "--headless",
        f"--alluredir={ALLURE_DIR}",
        "--reruns=2", "--reruns-delay=3",
    ],
    "regression": [
        "tests/", "-m", "smoke or regression",
        "--browser=chrome", "--headless",
        "--workers=4",
        f"--alluredir={ALLURE_DIR}",
        "--reruns=2", "--reruns-delay=3",
    ],
    "parallel": [
        "tests/",
        "--browser=chrome", "--headless",
        "--workers=auto",
        f"--alluredir={ALLURE_DIR}",
        "--reruns=2", "--reruns-delay=3",
    ],
    "headed": [
        "tests/",
        "--browser=chrome",
        f"--alluredir={ALLURE_DIR}",
        "--reruns=0",
    ],
    "firefox": [
        "tests/", "-m", "smoke",
        "--browser=firefox", "--headless",
        f"--alluredir={ALLURE_DIR}",
        "--reruns=2", "--reruns-delay=3",
    ],
}


def custom_mode():
    """交互式自定义参数"""
    print("[模式] 自定义")
    browser = input("浏览器 [chrome]: ").strip() or "chrome"
    headless = input("无头模式? [y/N]: ").strip().lower()
    marker = input("Markers [smoke]: ").strip() or "smoke"
    workers = input("Workers [auto]: ").strip() or "auto"

    args = [
        "tests/", "-m", marker,
        f"--browser={browser}",
    ]
    if headless in ("y", "yes"):
        args.append("--headless")
    args += [
        f"--workers={workers}",
        f"--alluredir={ALLURE_DIR}",
        "--reruns=2", "--reruns-delay=3",
    ]
    return args


def generate_allure_report():
    """尝试生成并打开 Allure 报告"""
    results_dir = os.path.join(ROOT_DIR, ALLURE_DIR)
    if not os.path.isdir(results_dir):
        print(f"\n[WARN] Allure 结果目录不存在: {results_dir}")
        return

    allure_bin = "allure"
    # Windows 下 allure 可能在 PATH 中或通过 scoop/choco 安装
    try:
        result = subprocess.run(
            [allure_bin, "--version"],
            capture_output=True, text=True, shell=(os.name == "nt"),
        )
        if result.returncode != 0:
            raise FileNotFoundError()
    except (FileNotFoundError, OSError):
        print("\n⚠️  未安装 Allure CLI，请手动查看:")
        print(f"   allure serve {results_dir}")
        print("   安装: scoop install allure  (Windows)")
        print("         brew install allure   (macOS)")
        print("         或下载: https://github.com/allure-framework/allure2/releases")
        return

    report_dir = os.path.join(ROOT_DIR, "allure-report")
    print("\n" + "=" * 50)
    print("  生成 Allure Report ...")
    print("=" * 50)
    subprocess.run(
        [allure_bin, "generate", results_dir, "-o", report_dir, "--clean"],
        shell=(os.name == "nt"),
    )
    print(f"\n✅ 报告已生成: file:///{report_dir.replace(os.sep, '/')}/index.html")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"

    if mode not in PRESETS and mode != "custom":
        print(f"未知模式: {mode}")
        print(f"可用: {', '.join(PRESETS)} | custom")
        sys.exit(1)

    print("=" * 50)
    print("  UI Autotest Runner")
    print("=" * 50)

    # 切换工作目录
    os.chdir(ROOT_DIR)

    # 清空旧报告
    import shutil
    allure_path = os.path.join(ROOT_DIR, ALLURE_DIR)
    if os.path.exists(allure_path):
        shutil.rmtree(allure_path)

    # 构建参数
    if mode == "custom":
        args = custom_mode()
    else:
        args = PRESETS[mode]
        print(f"[模式] {mode}")

    # 运行 pytest
    cmd = [sys.executable, "-m", "pytest"] + args
    print(f"\n[RUN] {' '.join(cmd)}\n")
    exit_code = subprocess.call(cmd, shell=False)

    # 生成报告
    generate_allure_report()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
