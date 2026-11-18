import os
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

    def click_generate_pdf_order(self):
        self.click(self.GENERATE_PDF_ORDER_BUTTON)

    def wait_for_pdf_download(self, download_dir, before_files):
        def _is_downloaded(driver):
            current_files = set(os.listdir(download_dir))
            new_files = current_files - before_files
            pdf_files = [f for f in new_files if f.lower().endswith(".pdf")]
            return pdf_files[0] if pdf_files else False

        return self.wait.until(_is_downloaded)