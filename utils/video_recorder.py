from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import HTTPError
import cv2
import numpy as np
import threading
import time
from io import BytesIO
from PIL import Image

class BrowserVideoRecorder:
    def __init__(self, driver, output_path, fps=5):
        self.driver = driver
        self.output_path = output_path
        self.fps = fps
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def _record_loop(self):
        writer = None
        interval = 1.0 / self.fps
        try:
            while not self._stop_event.is_set():
                start_time = time.time()
                try:
                    png_bytes = self.driver.get_screenshot_as_png()
                    img = Image.open(BytesIO(png_bytes)).convert("RGB")
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

                    if writer is None:
                        height, width, _ = frame.shape
                        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                        writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, (width, height))

                    writer.write(frame)
                except (WebDriverException, HTTPError, OSError):
                    # 브라우저 종료 시점의 일시적 예외 무시
                    break

                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)
        finally:
            if writer is not None:
                writer.release()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=3)
