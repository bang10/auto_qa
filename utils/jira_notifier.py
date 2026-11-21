import os
import platform
import requests
from requests.auth import HTTPBasicAuth
from config.config import Config

class JiraNotifier:
    def __init__(self):
        self.enabled = (
            Config.JIRA_ENABLED
            and bool(Config.JIRA_URL)
            and bool(Config.JIRA_EMAIL)
            and bool(Config.JIRA_API_TOKEN)
        )
        self.base_url = Config.JIRA_URL
        self.auth = HTTPBasicAuth(Config.JIRA_EMAIL, Config.JIRA_API_TOKEN) if self.enabled else None
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _build_adf_description(self, scenario, error_msg, screenshot_name, video_name):
        """Jira Cloud REST API v3용 본문 생성"""
        short_error = error_msg[:2500] + "\n..." if len(error_msg) > 2500 else error_msg
        attachment_info = f"{screenshot_name}"
        if video_name:
            attachment_info += f"{video_name}"

        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "1. 테스트 시나리오"}]
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": scenario}]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "2. 실행 환경 및 첨부 "}]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [{
                                "type": "paragraph",
                                "content": [{"type": "text", "text": f"확인 URL: {Config.BASE_URL}"}]
                            }]
                        },
                        {
                            "type": "listItem",
                            "content": [{
                                "type": "paragraph",
                                "content": [{"type": "text", "text": f"실행 환경: {platform.system()} {platform.release()} / Chrome"}]
                            }]
                        },
                        {
                            "type": "listItem",
                            "content": [{
                                "type": "paragraph",
                                "content": [{"type": "text", "text": f"첨부 파일: {attachment_info}"}]
                            }]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "3. 실패 사유 "}]
                },
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [{"type": "text", "text": short_error}]
                }
            ]
        }

    def create_bug_issue(self, test_name, scenario, error_msg, screenshot_path=None, video_path=None, platform_label="PC"):
        """
        Jira 버그 티켓 생성 후 스크린샷 및 동영상 첨부
        """
        if not self.enabled:
            return None

        screenshot_name = os.path.basename(screenshot_path) if screenshot_path and os.path.exists(screenshot_path) else "없음"
        video_name = os.path.basename(video_path) if video_path and os.path.exists(video_path) else None

        payload = {
            "fields": {
                "project": {"key": Config.JIRA_PROJECT_KEY},
                "summary": f"[{platform_label}][테스트 실패] {test_name}", 
                "issuetype": {"name": Config.JIRA_ISSUE_TYPE},
                "description": self._build_adf_description(
                    scenario=scenario,
                    error_msg=error_msg,
                    screenshot_name=screenshot_name,
                    video_name=video_name
                ),
                "labels": ["automation", "e2e", "pytest"]
            }
        }

        try:
            # 이슈 생성 API 호출
            res = requests.post(
                f"{self.base_url}/rest/api/3/issue",
                json=payload,
                headers=self.headers,
                auth=self.auth,
                timeout=15
            )
            if res.status_code not in (200, 201):
                print(f"[Jira 이슈 생성 실패] Status={res.status_code}, Response={res.text}")
                return None

            issue_key = res.json().get("key")
            issue_url = f"{self.base_url}/browse/{issue_key}"

            # 스크린샷, 녹화 영상 첨부
            files_to_attach = []
            if screenshot_path and os.path.exists(screenshot_path):
                files_to_attach.append(screenshot_path)
            if video_path and os.path.exists(video_path):
                files_to_attach.append(video_path)

            if files_to_attach:
                self._attach_files(issue_key, files_to_attach)

            return {"key": issue_key, "url": issue_url}

        except Exception as e:
            print(f"[Jira 연동 오류] {e}")
            return None

    def _attach_files(self, issue_key, file_paths):
        """생성된 Jira 이슈에 이미지 및 MP4 파일 업로드 """
        attach_url = f"{self.base_url}/rest/api/3/issue/{issue_key}/attachments"
        attach_headers = {"X-Atlassian-Token": "no-check"}

        for path in file_paths:
            try:
                with open(path, "rb") as f:
                    files = {"file": (os.path.basename(path), f)}
                    res = requests.post(
                        attach_url,
                        headers=attach_headers,
                        files=files,
                        auth=self.auth,
                        timeout=30
                    )
                    if res.status_code not in (200, 201):
                        print(f"[Jira 파일 첨부 실패: {os.path.basename(path)}] {res.status_code} - {res.text}")
            except Exception as e:
                print(f"[Jira 파일 첨부 예외: {os.path.basename(path)}] {e}")