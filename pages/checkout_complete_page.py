from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CheckoutCompletePage(BasePage):
    PAGE_TITLE = (By.CLASS_NAME, "title")
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    BACK_HOME_BUTTON = (By.ID, "back-to-products")
    GENERATE_PDF_ORDER_BUTTON = (By.ID, "generate-pdf-order")

    def get_title(self):
        return self.get_text(self.PAGE_TITLE)

    def get_complete_message(self):
        return self.get_text(self.COMPLETE_HEADER)

    def click_back_home(self):
        self.click(self.BACK_HOME_BUTTON)

    # TODO 영수증 다운로드
    def click_generate_pdf_order(self):
        self.click(self.GENERATE_PDF_ORDER_BUTTON)