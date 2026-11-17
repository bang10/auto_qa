import os
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage
from utils.video_recorder import BrowserVideoRecorder

import platform
import time
from pytest_metadata.plugin import metadata_key

# 리포트 및 미디어 저장 경로 생성
REPORT_DIR = "reports"
SCREENSHOT_DIR = os.path.join(REPORT_DIR, "screenshots")
VIDEO_DIR = os.path.join(REPORT_DIR, "videos")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

@pytest.fixture(scope="function")
def driver(request):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-features=PasswordLeakDetection")
    options.add_argument("--guest")

    driver = webdriver.Chrome(options=options)

    # 테스트 시작 시 동영상 녹화 시작
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = request.node.name.replace("[", "_").replace("]", "_").replace("/", "_")
    video_filename = f"{safe_name}_{timestamp}.mp4"
    video_path = os.path.join(VIDEO_DIR, video_filename)
    request.node.video_filename = video_filename

    recorder = BrowserVideoRecorder(driver, video_path, fps=5)
    recorder.start()

    yield driver

    # 테스트 종료 후 녹화 중지
    recorder.stop()
    driver.quit()

    # 테스트가 실패하지 않았다면(성공 시) 용량 관리를 위해 녹화 파일 삭제
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call is None or not rep_call.failed:
        if os.path.exists(video_path):
            os.remove(video_path)

@pytest.fixture(scope="function")
def logged_in_driver(driver):
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login("standard_user", "secret_sauce")
    return driver

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 실패 시, 영상 녹화 및 스크린 샷"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    doc = item.function.__doc__
    rep.description = doc.strip() if doc else item.name

    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = item.name.replace("[", "_").replace("]", "_").replace("/", "_")
            
            # 1. 로컬 폴더에 스크린샷 파일 저장 (보관용)
            screenshot_filename = f"{safe_name}_{timestamp}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
            driver.save_screenshot(screenshot_path)

            # 2. pytest-html 리포트 첨부 (--self-contained-html 완벽 호환)
            pytest_html = item.config.pluginmanager.getplugin("html")
            if pytest_html is not None:
                extras = getattr(rep, "extras", [])
                
                # 파일 경로 대신 Base64 문자열을 직접 전달해야 단일 HTML에서도 깨지지 않음
                screenshot_base64 = driver.get_screenshot_as_base64()
                extras.append(pytest_html.extras.image(screenshot_base64))

                video_filename = getattr(item, "video_filename", None)
                if video_filename:
                    rel_vid_path = f"videos/{video_filename}"
                    extras.append(pytest_html.extras.url(rel_vid_path, name="실패 실행 동영상 보기 (MP4)"))
                
                rep.extras = extras

def pytest_html_report_title(report):
    """리포트 제목"""
    report.title = "Swag Labs (SauceDemo) E2E 자동화 테스트 종합 결과 리포트"

def pytest_configure(config):
    """테이블 커스터마이징"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config.option.htmlpath = os.path.join(REPORT_DIR, f"report_{timestamp}.html")

    # 기본으로 들어가는 불필요한 시스템 환경 정보 정리
    config.stash[metadata_key].clear()
    
    # QA 리포트에 꼭 필요한 핵심 환경 정보만 추가
    config.stash[metadata_key]["프로젝트명"] = "SauceDemo E2E Web Automation"
    config.stash[metadata_key]["테스트 대상 URL"] = "https://www.saucedemo.com/"
    config.stash[metadata_key]["브라우저"] = "Google Chrome (Guest Mode)"
    config.stash[metadata_key]["OS / Python"] = f"{platform.system()} {platform.release()} / Python {platform.python_version()}"
    config.stash[metadata_key]["테스트 실행 일시"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def pytest_sessionstart(session):
    """전체 테스트 시작 시각 기록 (총 소요 시간 및 통계 계산용)"""
    session.start_time = time.time()
    session.results_summary = {"passed": 0, "failed": 0, "skipped": 0}

def pytest_html_results_table_header(cells):
    """테스트 테이블 헤더에 '테스트 시나리오 설명' 컬럼 추가"""
    cells.insert(2, "<th>테스트 시나리오 (Description)</th>")

def pytest_html_results_table_row(report, cells):
    """각 테스트 행(Row)에 함수의 Docstring 내용을 설명으로 자동 삽입"""
    description = getattr(report, "description", "-")
    cells.insert(2, f"<td>{description}</td>")

def pytest_html_results_summary(prefix, summary, postfix):
    """Summary(요약) 영역 상단에 통과율(Pass Rate) 및 소요 시간 요약 배너 추가"""
    # 실행 통계 집계는 terminalreporter에서 가져오거나 직접 계산 가능
    prefix.extend([
        "<div style='padding: 12px 16px; margin: 10px 0; background-color: #f4f6f9; border-left: 5px solid #2c7be5; border-radius: 4px; font-family: sans-serif;'>",
        "<strong>[QA 자동화 실행 요약]</strong> 본 리포트는 Selenium 4 + Pytest POM 프레임워크로 자동 수행된 회귀 테스트(Regression Test) 결과입니다.<br>",
        "<span style='font-size: 13px; color: #555;'>※ 실패(Failed) 항목을 클릭해 펼치면 실패 순간의 스크린샷과 전체 실행 동영상(MP4) 링크를 확인할 수 있습니다.</span>",
        "</div>"
    ])