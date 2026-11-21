from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CheckoutStepOnePage(BasePage):
    """결제 1단계"""
    
    PAGE_TITLE = (By.CLASS_NAME, "title")
    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT = (By.ID, "last-name")
    POSTAL_CODE_INPUT = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    CALNCEL_BUTTON = (By.ID, "cancel")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def get_title(self):
        return self.get_text(self.PAGE_TITLE)

    def enter_shipping_info(self, first_name, last_name, postal_code):
        """기본 정보 입력"""
        self.type_text(self.FIRST_NAME_INPUT, first_name)
        self.type_text(self.LAST_NAME_INPUT, last_name)
        self.type_text(self.POSTAL_CODE_INPUT, postal_code)

    def click_continue(self):
        self.click(self.CONTINUE_BUTTON)

    def click_calcel(self):
        self.click(self.CALNCEL_BUTTON)

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)

    
    def get_entered_shipping_info(self):
        """입력 필드에 실제로 채워진 값 조회"""
        return {
            "first_name": self.find(self.FIRST_NAME_INPUT).get_attribute("value"),
            "last_name": self.find(self.LAST_NAME_INPUT).get_attribute("value"),
            "postal_code": self.find(self.POSTAL_CODE_INPUT).get_attribute("value"),
        }