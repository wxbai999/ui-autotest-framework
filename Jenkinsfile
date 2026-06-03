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
                checkout scm
                echo "Branch: ${env.BRANCH_NAME}"
            }
        }

        // ----------------------------------------------------------
        // Stage 2: Install Dependencies
        // ----------------------------------------------------------
        // stage('Install Dependencies') {
        //     steps {
        //         bat '''
        //             python --version
        //             python -m pip install --upgrade pip
        //             python -m pip install -r requirements.txt
        //         '''
        //     }
        // }

        // ----------------------------------------------------------
        // Stage 3: Run Tests
        // ----------------------------------------------------------
        stage('Run Tests') {
            steps {
                script {
                    if (params.TEST_MARKER == 'smoke' || params.TEST_MARKER == 'all') {
                        bat """
                            python -m pytest tests/ -m smoke --browser=${BROWSER} --headless --workers=${WORKERS} --alluredir=${ALLURE_RESULTS_DIR} --reruns=2 --reruns-delay=3 --junitxml=junit-smoke.xml
                        """
                    }
                    if (params.TEST_MARKER == 'regression' || params.TEST_MARKER == 'all') {
                        bat """
                            python -m pytest tests/ -m regression --browser=${BROWSER} --headless --workers=${WORKERS} --alluredir=${ALLURE_RESULTS_DIR} --reruns=2 --reruns-delay=3 --junitxml=junit-regression.xml
                        """
                    }
                }
            }
            post {
                always {
                    junit 'junit-*.xml'
                }
            }
        }
    }

    // ============================================================
    // Post: 发布 Allure Report
    // ============================================================
    post {
        always {
            allure includeProperties: false,
                   results: [[path: "${ALLURE_RESULTS_DIR}"]]
        }


    }
}
