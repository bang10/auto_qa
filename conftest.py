import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage

@pytest.fixture(scope="function")
def driver():
    """웹 드라이버"""
    options = Options()
    # 헤드리스 실행이 필요할 경우 아래 주석 해제
    # options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    
    # 크롬 비밀번호 유출 경고 팝업 방지
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False 
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-features=PasswordLeakDetection")
    options.add_argument("--guest")

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """로그인된 웹 드라이버"""
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login("standard_user", "secret_sauce")
    return driver
