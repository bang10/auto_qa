import html
import os
from config.config import Config
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage
from utils.video_recorder import BrowserVideoRecorder
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.config import Config

import platform
import time
from pytest_metadata.plugin import metadata_key
from utils.slack_notifier import SlackNotifier
from utils.jira_notifier import JiraNotifier

# 리포트 및 미디어 저장 경로 생성
REPORT_DIR = "reports"
SCREENSHOT_DIR = os.path.join(REPORT_DIR, "screenshots")
VIDEO_DIR = os.path.join(REPORT_DIR, "videos")
LOG_DIR = os.path.join(REPORT_DIR, "logs")
DOWNLOAD_DIR = os.path.abspath(os.path.join(REPORT_DIR, "downloads"))
_abort_reason = None

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Slack
slack_notifier = SlackNotifier()
jira_notifier = JiraNotifier()
_has_sent_start_alert = False
_has_sent_finish_alert = False
_test_start_time = None
_total_collected_tests = 0

for directory in [SCREENSHOT_DIR, VIDEO_DIR, LOG_DIR, DOWNLOAD_DIR]:
    os.makedirs(directory, exist_ok=True)

def pytest_addoption(parser):
    parser.addoption(
        "--slack",
        action="store_true",
        default=False,
        help="테스트 시작, 실패, 종료 시 Slack 알림을 전송합니다."
    )

    parser.addoption(
        "--jira",
        action="store_true",
        default=False,
        help="테스트 실패 시 Jira 티켓을 자동 생성합니다."
    )
    
    parser.addoption(
        "--platform",
        action="store",
        default="pc",
        choices=["pc", "mobile"],
        help="테스트 실행 플랫폼 선택 (pc 또는 mobile)"
    )

    parser.addoption(
        "-U", "--user-id",
        action="store",
        default=None,
        help="테스트에 사용할 계정 ID (미입력 시 STANDARD_USER 적용)"
    )
    parser.addoption(
        "-P", "--user-pw",
        action="store",
        default=None,
        help="테스트에 사용할 계정 비밀번호 (미입력 시 기본 PASSWORD 적용)"
    )

@pytest.fixture(scope="function")
def driver(request):
    platform_name = request.config.getoption("--platform").lower()
    options = Options()
    if platform_name == "mobile":
        # 모바일 웹 : iPhone 14 Pro 기준 뷰포트, 모바일 User-Agent, 터치 지원
        mobile_emulation = {
            "deviceMetrics": {"width": 393, "height": 852, "pixelRatio": 3.0},
            "userAgent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
            )
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
    else:
        options.add_argument("--window-size=1920,1080")

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-features=PasswordLeakDetection")
    options.add_argument("--guest")

    # Ubuntu > CLI 환경 대응
    if Config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    # 다운로드 저장 팝업 미노출 처리
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": DOWNLOAD_DIR
        }
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = request.node.name.replace("[", "_").replace("]", "_").replace("/", "_")
    video_filename = f"{platform_name}_{safe_name}_{timestamp}.mp4"
    video_path = os.path.join(VIDEO_DIR, video_filename)

    recorder = BrowserVideoRecorder(driver, video_path, fps=3)
    recorder.start()

    # item 객체에 recorder와 경로 저장 - 실패 훅에서 즉시 녹화 종료 후 첨부
    request.node.recorder = recorder
    request.node.video_filename = video_filename
    request.node.video_path = video_path

    # 브라우저 종료가 안되는 경우가 존재하여 finally 추가
    try:
        yield driver
    finally:
        # 녹화기가 아직 돌고 있다면 종료
        try:
            if getattr(recorder, "running", False):
                recorder.stop()
        except Exception as e:
            print(f"[녹화 종료 경고] {e}")

        # 테스트가 성공한 경우 영상 삭제
        try:
            rep_call = getattr(request.node, "rep_call", None)
            if rep_call and rep_call.passed and os.path.exists(video_path):
                os.remove(video_path)
        except Exception as e:
            print(f"[성공 영상 삭제 경고] {e}")

        # 어떤 상황이든 상관없이 브라우저 종료
        try:
            driver.quit()
        except Exception as e:
            print(f"[브라우저 종료 경고] {e}")

@pytest.fixture(scope="function")
def logged_in_driver(driver, credentials):
    login_page = LoginPage(driver)
    login_page.load()
    
    login_page.login(credentials["username"], credentials["password"])
    return driver

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 실패 시, 영상 녹화 및 스크린 샷"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    doc = item.function.__doc__
    description = doc.strip() if doc else item.name
    rep.description = doc.strip() if doc else item.name

    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = item.name.replace("[", "_").replace("]", "_").replace("/", "_")
            
            # 로컬 폴더에 스크린샷 파일 저장
            screenshot_filename = f"{safe_name}_{timestamp}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
            driver.save_screenshot(screenshot_path)

            recorder = getattr(item, "recorder", None)
            if recorder and getattr(recorder, "running", False):
                recorder.stop()
            video_path = getattr(item, "video_path", None)

            # 예외 종류에 따라 실패 사유 메시지 정제
            if call.excinfo:
                exc_type = call.excinfo.type
                exc_val = str(call.excinfo.value).strip()

                if issubclass(exc_type, TimeoutException):
                    if "[요청 시간 초과" in exc_val:
                        error_msg = exc_val
                    else:
                        error_msg = (
                            f"[요청 시간 초과 ({Config.DEFAULT_TIMEOUT}초)] "
                            f"페이지 응답 또는 대상 요소 로딩이 지연되어 테스트가 중단되었습니다.\n"
                            f"현재 페이지 URL: {driver.current_url}"
                        )

                    if "[요소 미발견]" in exc_val:
                        error_msg = exc_val
                    else:
                        error_msg = (
                            f"[요소 미발견] 화면(DOM)에서 선택할 대상 요소를 찾을 수 없습니다.\n"
                            f"현재 페이지 URL: {driver.current_url}"
                        )
                else:
                    error_msg = exc_val if exc_val else rep.longreprtext
            else:
                error_msg = rep.longreprtext
            
            platform_label = item.config.getoption("--platform").upper()
            
            jira_enabled = item.config.getoption("--jira")
            jira_enabled = jira_enabled != False  # Jira 티켓 자동 생성 여부

            jira_issue = None

            # 실패 사유 추출 및 Jira 버그 이슈 자동 생성
            if jira_enabled:
                error_msg = str(call.excinfo.value) if call.excinfo else rep.longreprtext
                jira_issue = jira_notifier.create_bug_issue(
                    test_name=item.name,
                    scenario=description,
                    error_msg=error_msg,
                    screenshot_path=screenshot_path,
                    video_path=video_path,
                    platform_label=platform_label
                )

            slack_enabled = item.config.getoption("--slack")
            slack_enabled = slack_enabled != False  # Slack 알림 활성화 여부

            # 실패 사유 추출
            error_msg = str(call.excinfo.value) if call.excinfo else rep.longreprtext

            if slack_enabled:
                slack_notifier.send_failure_notification(
                    test_name=item.name,
                    description=description,
                    error_msg=error_msg,
                    screenshot_path=screenshot_path,
                    jira_issue=jira_issue,
                    platform_label=platform_label
                )

            # pytest-html 리포트 첨부
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

        # 로그인 실패 시 나머지 테스트 전체 중단
        if "critical_login" in item.keywords:
            creds = item.funcargs.get("credentials", {})
            target_user = creds.get("username", "알 수 없음")
            abort_msg = (
                f"로그인 실패(계정: `{target_user}`, 테스트: `{item.name}`)로 인해 "
                f"나머지 테스트를 모두 중단했습니다."
            )
            _abort_reason = abort_msg
            item.config._abort_reason = abort_msg
            item.session.shouldstop = abort_msg

@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    """세선 종료 직후 최종 통계 확정 및 config에 저장"""
    terminalreporter = session.config.pluginmanager.getplugin("terminalreporter")
    if not terminalreporter:
        return

    total = _total_collected_tests if _total_collected_tests > 0 else terminalreporter._numcollected
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    error = len(terminalreporter.stats.get("error", []))
    total_failed = failed + error
    not_run = max(0, total - (passed + total_failed))
    elapsed = time.time() - _test_start_time if _test_start_time else 0

    session.config._summary_stats = {
        "total": total,
        "passed": passed,
        "failed": total_failed,
        "not_run": not_run,
        "elapsed": elapsed,
        "report_path": getattr(session.config.option, "htmlpath", None),
        "abort_reason": getattr(session.config, "_abort_reason", None),
    }


def pytest_runtest_setup(item):
    global _has_sent_start_alert, _test_start_time, _total_collected_tests
    platform_name = item.config.getoption("--platform").lower()
    slack_enabled = item.config.getoption("--slack")
    slack_enabled = slack_enabled != False  # Slack 알림 활성화 여부
    
    # pytest.mark.mobile_only가 붙은 테스트는 PC 플랫폼에서 실행 시 스킵
    if "mobile_only" in item.keywords and platform_name != "mobile":
        pytest.skip("모바일 웹 전용 반응형 테스트이므로 PC 환경에서는 스킵됩니다.")
    
    if not _has_sent_start_alert:
        _test_start_time = time.time()
        _total_collected_tests = len(item.session.items)
    
        if slack_enabled:
            slack_notifier.send_start_notification(_total_collected_tests, platform_label=platform_name.upper())

    _has_sent_start_alert = True

def pytest_html_report_title(report):
    """리포트 제목"""
    report.title = "SauceDemo 자동화 테스트 종합 결과 리포트"

def pytest_configure(config):
    """테이블 커스터마이징"""
    Config.validate()
    platform_name = config.getoption("--platform").lower()
    platform_label = platform_name.upper()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 종합 보고서 세팅
    config.option.htmlpath = os.path.join(REPORT_DIR, f"report_{platform_name}_{timestamp}.html")
    config.option.log_file = os.path.join(LOG_DIR, f"test_{platform_name}_{timestamp}.log")

    # 로그 파일 세팅
    log_path = os.path.join(LOG_DIR, f"test_{timestamp}.log")
    config.option.log_file = log_path

    # 기본으로 들어가는 불필요한 시스템 환경 정보 정리
    config.stash[metadata_key].clear()
    
    # 리포트에 꼭 필요한 핵심 환경 정보만 추가
    config.stash[metadata_key]["프로젝트명"] = "SauceDemo Web Automation"
    config.stash[metadata_key]["테스트 대상 URL"] = Config.BASE_URL
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

def pytest_html_results_summary(prefix, summary, postfix, session):
    """Summary(요약) 영역 상단에 통과율(Pass Rate) 및 소요 시간 요약 배너 추가"""
    stats = getattr(session.config, "_summary_stats", None)
    if not stats or stats["total"] == 0:
        return

    # abort_reason 가져오기
    abort_reason = _abort_reason or getattr(session.config, "_abort_reason", None)

    # 조기 중단 사유가 존재할 경우 상단 카드 위에 붉은색 경고 배너 생성
    abort_banner_html = ""
    if abort_reason:
        # 슬랙 마크다운 백틱 제거 및 HTML 이스케이프 처리
        clean_reason = html.escape(abort_reason.replace("`", "'"))
        abort_banner_html = f"""
        <div style="
            background-color: #fef2f2;
            border: 1px solid #f87171;
            border-left: 6px solid #dc2626;
            color: #991b1b;
            padding: 14px 18px;
            border-radius: 8px;
            margin-bottom: 16px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 2px 4px rgba(220, 38, 38, 0.08);
        ">
            <div style="font-weight: 700; font-size: 15px; margin-bottom: 4px;">
                🚨 테스트 세션 조기 종료
            </div>
            <div style="font-size: 13.5px; line-height: 1.5;">
                {clean_reason}
            </div>
        </div>
        """

    total = stats["total"]
    passed = stats["passed"]
    failed = stats["failed"]
    not_run = stats["not_run"]
    duration_str = _format_duration(stats["elapsed"])

    # 성공률 계산 (전체 수집 건수 기준)
    pass_rate = (passed / total * 100) if total > 0 else 0.0

    dashboard_html = f"""
    <div style="margin: 16px 0 24px 0;">
        {abort_banner_html}
        <div style="
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 12px; color: #64748b; font-weight: 600;">전체 테스트 (Total)</div>
                <div style="font-size: 24px; font-weight: 700; color: #0f172a; margin-top: 4px;">{total}건</div>
            </div>
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 12px; color: #166534; font-weight: 600;">성공 (Pass)</div>
                <div style="font-size: 24px; font-weight: 700; color: #15803d; margin-top: 4px;">{passed}건</div>
            </div>
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 12px; color: #991b1b; font-weight: 600;">실패 (Fail)</div>
                <div style="font-size: 24px; font-weight: 700; color: #dc2626; margin-top: 4px;">{failed}건</div>
            </div>
            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 12px; color: #92400e; font-weight: 600;">미진행 (Not Run)</div>
                <div style="font-size: 24px; font-weight: 700; color: #d97706; margin-top: 4px;">{not_run}건</div>
            </div>
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 12px; color: #1e40af; font-weight: 600;">통과율 / 소요 시간</div>
                <div style="font-size: 18px; font-weight: 700; color: #1d4ed8; margin-top: 6px;">{pass_rate:.1f}% <span style="font-size: 13px; font-weight: 500;">({duration_str})</span></div>
            </div>
        </div>
    </div>
    """
    prefix.append(dashboard_html)

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """전체 테스트 종료 후, 최종 집계 및 알림 전송"""
    total = _total_collected_tests if _total_collected_tests > 0 else terminalreporter._numcollected

    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    error = len(terminalreporter.stats.get("error", []))
    total_failed = failed + error

    # 전체 건수에서 실제 완료된(pass + fail) 건수를 제외한 나머지를 모두 '미진행'으로 산출
    not_run = max(0, total - (passed + total_failed))

    if total > 0:
        config._summary_stats = {
            "total": total,
            "passed": passed,
            "failed": total_failed,
            "not_run": not_run,
            "elapsed": time.time() - _test_start_time if _test_start_time else 0,
            "report_path": getattr(config.option, "htmlpath", None)
        }

def pytest_unconfigure(config):
    summary_stats = getattr(config, "_summary_stats", None)
    slack_enabled = config.getoption("--slack")
    slack_enabled = slack_enabled != False  # Slack 알림 활성화 여부

    final_abort_reason = _abort_reason or getattr(config, "_abort_reason", None)
    
    if slack_enabled and summary_stats and summary_stats["total"] > 0:
        slack_notifier.send_finish_notification(
            total=summary_stats["total"],
            passed=summary_stats["passed"],
            failed=summary_stats["failed"],
            not_run=summary_stats["not_run"],
            elapsed_seconds=summary_stats["elapsed"],
            report_path=summary_stats["report_path"],
            platform_label=config.getoption("--platform").upper(),
            abort_reason=final_abort_reason,
        )

def _format_duration(elapsed_seconds):
    """초(float) 단위 시간을 hh:mm:ss 문자열로 변환"""
    total_sec = int(round(elapsed_seconds))
    hours, remainder = divmod(total_sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@pytest.fixture(scope="session")
def credentials(request):
    """--user-id, --user-pw이 있으면 우선 적용 / 없거나 빈 값이면 기본값 반환"""
    cli_id = request.config.getoption("--user-id")
    cli_pw = request.config.getoption("--user-pw")

    return {
        "username": cli_id.strip() if cli_id and cli_id.strip() else Config.STANDARD_USER,
        "password": cli_pw if cli_pw else Config.PASSWORD,
    }
