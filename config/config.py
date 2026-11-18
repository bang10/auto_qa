import os
from dotenv import load_dotenv

load_dotenv(override=False)

class Config:
    BASE_URL = os.getenv("BASE_URL")
    INVENTORY_URL = os.getenv("INVENTORY_URL")
    PASSWORD = os.getenv("SAUCE_PASSWORD")

    # 계정 페르소나별 ID 매핑
    STANDARD_USER = os.getenv("STANDARD_USER")
    LOCKED_OUT_USER = os.getenv("LOCKED_OUT_USER")
    PROBLEM_USER = os.getenv("PROBLEM_USER")
    PERFORMANCE_GLITCH_USER = os.getenv("PERFORMANCE_GLITCH_USER")
    ERROR_USER = os.getenv("ERROR_USER")
    VISUAL_USER = os.getenv("VISUAL_USER")

    # 실행 환경 설정
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "10"))

    @classmethod
    def validate(cls):
        if not cls.BASE_URL:
            raise ValueError("환경 변수 'BASE_URL'가 설정되지 않았습니다.")
        if not cls.PASSWORD:
            raise ValueError("환경 변수 'PASSWORD'가 설정되지 않았습니다.")
        if not cls.STANDARD_USER:
            raise ValueError("환경 변수 'STANDARD_USER'가 설정되지 않았습니다.")
        if not cls.LOCKED_OUT_USER:
            raise ValueError("환경 변수 'LOCKED_OUT_USER'가 설정되지 않았습니다.")
        if not cls.PROBLEM_USER:
            raise ValueError("환경 변수 'PROBLEM_USER'가 설정되지 않았습니다.")
        if not cls.PERFORMANCE_GLITCH_USER:
            raise ValueError("환경 변수 'PERFORMANCE_GLITCH_USER'가 설정되지 않았습니다.")
        if not cls.ERROR_USER:
            raise ValueError("환경 변수 'ERROR_USER'가 설정되지 않았습니다.")
        if not cls.VISUAL_USER:
            raise ValueError("환경 변수 'VISUAL_USER'가 설정되지 않았습니다.")
        
    