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
        stage('Install Dependencies') {
            steps {
                sh '''
                    python --version
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        // ----------------------------------------------------------
        // Stage 3: Run Tests（并行分组）
        // ----------------------------------------------------------
        stage('Run Tests') {
            parallel {
                // --- 冒烟测试 ---
                stage('Smoke Tests') {
                    when {
                        expression { params.TEST_MARKER in ['smoke', 'all'] }
                    }
                    steps {
                        sh '''
                            pytest tests/ \
                                -m "smoke" \
                                --browser=${BROWSER} \
                                --headless \
                                --workers=${WORKERS} \
                                --alluredir=${ALLURE_RESULTS_DIR}/smoke \
                                --reruns=2 \
                                --reruns-delay=3 \
                                --junitxml=junit-smoke.xml
                        '''
                    }
                    post {
                        always {
                            junit 'junit-smoke.xml'
                        }
                    }
                }

                // --- 回归测试 ---
                stage('Regression Tests') {
                    when {
                        expression { params.TEST_MARKER in ['regression', 'all'] }
                    }
                    steps {
                        sh '''
                            pytest tests/ \
                                -m "regression" \
                                --browser=${BROWSER} \
                                --headless \
                                --workers=${WORKERS} \
                                --alluredir=${ALLURE_RESULTS_DIR}/regression \
                                --reruns=2 \
                                --reruns-delay=3 \
                                --junitxml=junit-regression.xml
                        '''
                    }
                    post {
                        always {
                            junit 'junit-regression.xml'
                        }
                    }
                }
            }
        }
    }

    // ============================================================
    // Post: 发布 Allure Report
    // ============================================================
    post {
        always {
            script {
                // 合并所有 Allure 结果目录为一个
                sh '''
                    mkdir -p ${ALLURE_RESULTS_DIR}
                    if [ -d ${ALLURE_RESULTS_DIR}/smoke ]; then
                        cp -r ${ALLURE_RESULTS_DIR}/smoke/* ${ALLURE_RESULTS_DIR}/
                    fi
                    if [ -d ${ALLURE_RESULTS_DIR}/regression ]; then
                        cp -r ${ALLURE_RESULTS_DIR}/regression/* ${ALLURE_RESULTS_DIR}/
                    fi
                '''
            }
            allure includeProperties: false,
                   results: [[path: "${ALLURE_RESULTS_DIR}"]]
        }

        // 清理工作空间
        cleanup {
            cleanWs()
        }
    }
}
