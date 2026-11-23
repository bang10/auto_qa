import os
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config.config import Config

class SlackNotifier:
    WEEKDAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]

    def __init__(self):
        self.enabled = Config.SLACK_ENABLED and bool(Config.SLACK_BOT_TOKEN) and bool(Config.SLACK_CHANNEL_ID)
        self.channel = Config.SLACK_CHANNEL_ID
        self.client = WebClient(token=Config.SLACK_BOT_TOKEN) if self.enabled else None

    def _get_formatted_date(self):
        now = datetime.now()
        weekday = self.WEEKDAYS_KR[now.weekday()]
        return f"{now.strftime('%Y. %m. %d')} ({weekday})"

    def _format_duration(self, elapsed_seconds):
        """초 단위 시간을 hh:mm:ss 문자열로 변환"""
        total_sec = int(round(elapsed_seconds))
        hours, remainder = divmod(total_sec, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def send_start_notification(self, total_count, platform_label="PC"):
        """테스트 시작 알림"""
        if not self.enabled:
            return
        date_str = self._get_formatted_date()
        text = f"*[{platform_label}] {date_str} {total_count}건 자동화 테스트 시작 알림*"
        try:
            self.client.chat_postMessage(channel=self.channel, text=text)
        except SlackApiError as e:
            print(f"[Slack 알림 오류 - 시작] {e.response['error']}")

    def send_failure_notification(self, test_name, description, error_msg, screenshot_path, jira_issue=None, platform_label="PC"):
        """테스트 Fail 시, 스크린샷 이미지 및 내용 전송"""
        if not self.enabled:
            return

        # 에러 로그가 너무 길면 슬랙 가독성을 위해 최대 600자로 제한
        short_error = error_msg[:600] + "..." if len(error_msg) > 600 else error_msg

        comment_lines = [
            f"❌ [{platform_label}]테스트 실패 발생",
            f"테스트명: `{test_name}`",
            f"시나리오: {description}",
        ]

        # Jira 티켓이 생성된 경우 슬랙 mrkdwn 링크(<URL|티켓키>) 삽입
        if jira_issue and jira_issue.get("url"):
            comment_lines.append(f"• *Jira 이슈 티켓:* <{jira_issue['url']}|{jira_issue['key']}>")

        comment_lines.append(f"• *실패 사유:*\n```{short_error}```")
        initial_comment = "\n".join(comment_lines)

        try:
            self.client.files_upload_v2(
                channel=self.channel,
                file=screenshot_path,
                title=f"실패 캡처 - {test_name}",
                initial_comment=initial_comment
            )
        except SlackApiError as e:
            print(f"[Slack 알림 오류 - 실패 첨부] {e.response['error']}")

    # 3. 테스트 종료 요약 알림
    def send_finish_notification(self, total, passed, failed, not_run, elapsed_seconds, report_path=None, platform_label="PC", abort_reason=None):
        if not self.enabled:
            return
        date_str = self._get_formatted_date()
        duration_str = self._format_duration(elapsed_seconds)
        if abort_reason:
            # 필수 로그인 실패 등으로 세션이 조기 종료된 경우
            header = f"🚨 *[{platform_label}] {date_str} 자동화 테스트 조기 종료 알림 (로그인 실패)*"
            reason_line = f"*중단 사유:* {abort_reason}\n"
        elif failed == 0 and not_run == 0:
            header = f"✅ *[{platform_label}] {date_str} {total}건 자동화 테스트 종료 알림*"
            reason_line = ""
        else:
            header = f"⚠️ *[{platform_label}] {date_str} {total}건 자동화 테스트 종료 알림*"
            reason_line = ""

        summary_text = (
        f"{header}\n"
        f"{reason_line}"
        f"*실행 결과:* 총 *{total}건*, pass *{passed}건*, fail *{failed}건*, 미진행 *{not_run}건*, 성공률 *{round((passed/total)*100, 2) if total > 0 else 0}%*\n"
        f"*소요 시간:* {duration_str}"
        )
        try:
            # 최종 HTML 보고서 파일이 존재하면 메시지와 함께 파일 업로드
            if report_path and os.path.exists(report_path):
                self.client.files_upload_v2(
                    channel=self.channel,
                    file=report_path,
                    title=f"[{platform_label}]자동화 테스트 종합 보고서 ({date_str})",
                    initial_comment=summary_text
                )
            else:
                self.client.chat_postMessage(channel=self.channel, text=summary_text)
        except SlackApiError as e:
            print(f"[Slack 알림 오류 - 종료] {e.response['error']}")

