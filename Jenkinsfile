pipeline {
    agent any

    // ============================================================
    // 参数：手动触发时可选择浏览器
    // ============================================================
    parameters {
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'firefox', 'edge'],
            description: '浏览器类型'
        )
        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: '无头模式（CI 建议开启）'
        )
        choice(
            name: 'TEST_MARKER',
            choices: ['smoke', 'regression', 'all'],
            description: '要运行的测试标记'
        )
        string(
            name: 'WORKERS',
            defaultValue: 'auto',
            description: '并行 worker 数（auto = CPU 核数）'
        )
    }

    environment {
        // 被测系统地址
        BASE_URL = 'https://www.baidu.com'

        // Driver 路径 — 指向本地固定目录，需提前放入 chromedriver.exe
        // 首次运行前执行: mkdir C:\jenkins-drivers && copy chromedriver.exe C:\jenkins-drivers\
        CHROME_DRIVER_PATH = "C:\\jenkins-drivers\\chromedriver.exe"

        // Selenium Grid（如果使用）
        // GRID_ENABLED = 'true'
        // GRID_URL = 'http://selenium-grid:4444'

        // Allure 结果目录
        ALLURE_RESULTS_DIR = 'allure-results'
    }

    stages {

        // ----------------------------------------------------------
        // Stage 1: Checkout
        // ----------------------------------------------------------
        stage('Checkout') {
            steps {
                echo '========================================='
                echo '  [Stage 1/3] Checkout — 拉取代码'
                echo '========================================='
                checkout scm
                echo "当前分支: ${env.BRANCH_NAME}"
                echo "[Checkout] 完成"
            }
        }

        // ----------------------------------------------------------
        // Stage 2: Install Dependencies & Download Driver
        // ----------------------------------------------------------
        stage('Setup') {
            steps {
                echo '========================================='
                echo '  [Stage 2/3] Setup — 安装依赖'
                echo '========================================='
//                 bat 'echo [Setup] Python 版本: && python --version'
//                 bat 'echo [Setup] 升级 pip ... && python -m pip install --upgrade pip'
//                 bat 'echo [Setup] 安装项目依赖 ... && python -m pip install -r requirements.txt'
                echo '[Setup] 完成'
            }
        }

        // ----------------------------------------------------------
        // Stage 3: Run Tests
        // ----------------------------------------------------------
        stage('Run Tests') {
            steps {
                echo '========================================='
                echo "  [Stage 3/3] Run Tests — 浏览器=${params.BROWSER} | 标记=${params.TEST_MARKER} | Workers=${params.WORKERS}"
                echo '========================================='
                script {
                    if (params.TEST_MARKER == 'smoke' || params.TEST_MARKER == 'all') {
                        echo '[Run Tests] 开始执行冒烟测试 ...'
                        bat """
                            python -m pytest tests/ -m smoke --browser=${BROWSER} --headless --workers=${WORKERS} --alluredir=${ALLURE_RESULTS_DIR} --reruns=2 --reruns-delay=3 --junitxml=junit-smoke.xml
                        """
                        echo '[Run Tests] 冒烟测试 完成'
                    }
                    if (params.TEST_MARKER == 'regression' || params.TEST_MARKER == 'all') {
                        echo '[Run Tests] 开始执行回归测试 ...'
                        bat """
                            python -m pytest tests/ -m regression --browser=${BROWSER} --headless --workers=${WORKERS} --alluredir=${ALLURE_RESULTS_DIR} --reruns=2 --reruns-delay=3 --junitxml=junit-regression.xml
                        """
                        echo '[Run Tests] 回归测试 完成'
                    }
                }
            }
            post {
                always {
                    echo '[Run Tests] 生成 JUnit 报告 ...'
                    junit 'junit-*.xml'
                }
            }
        }
    }

    // ============================================================
    // Post
    // ============================================================
    post {
        always {
            echo '========================================='
            echo '  [Post] 生成 Allure Report'
            echo '========================================='
            allure includeProperties: false,
                   results: [[path: "${ALLURE_RESULTS_DIR}"]]
            echo '[Post] 构建流程结束'
        }
    }
}
