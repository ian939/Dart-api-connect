import OpenDartReader
import requests
import os
from datetime import datetime

# 1. 환경 변수 설정 (GitHub Secrets에 등록해야 함)
DART_TOKEN = os.environ.get('DART_TOKEN')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

dart = OpenDartReader(DART_TOKEN)

# 2. 확인된 법인명으로 그룹화
# '차지비'의 경우 지에스차지비와 지에스커넥트 두 곳 모두 확인하도록 설정했습니다.
companies = {
    "⚡ 급속 충전": ["브라이트에너지파트너스", "채비", "이브이시스"],
    "🔌 완속 충전": ["플러그링크", "지에스차지비", "지에스커넥트", "에버온"]
}

def send_slack_msg(attachments):
    """슬랙 메시지 전송 (Attachment 형식)"""
    payload = {
        "text": f"📢 *{datetime.now().strftime('%Y-%m-%d')} 신규 공시 알림*",
        "attachments": attachments
    }
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"슬랙 전송 실패: {e}")

def check_disclosures():
    # 오늘 날짜 (YYYYMMDD)
    today = datetime.now().strftime('%Y%m%d')
    attachments = []
    
    print(f"🔍 {today} 공시 확인 시작...")

    for category, names in companies.items():
        for name in names:
            try:
                # 공시 목록 가져오기
                df = dart.list(name, start=today)
                
                if df is not None and not df.empty:
                    for i in range(len(df)):
                        title = df.iloc[i]['report_nm']      # 공시 제목
                        rcp_no = df.iloc[i]['rcept_no']     # 접수 번호
                        link = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"
                        
                        # 슬랙 개별 항목 디자인
                        color = "#F27100" if "급속" in category else "#22AEEF"
                        attachment = {
                            "color": color,
                            "title": f"[{category}] {name}",
                            "text": f"📄 *{title}*\n🔗 <{link}|공시 상세 보기>",
                            "footer": "DART 자동 알림 서비스",
                            "ts": int(datetime.now().timestamp())
                        }
                        attachments.append(attachment)
                        print(f"✅ 발견: {name} - {title}")
                else:
                    print(f"  - {name}: 신규 공시 없음")
            except Exception as e:
                print(f"⚠️ {name} 조회 중 오류 발생: {e}")

    # 공시가 있을 경우에만 슬랙 전송
    if attachments:
        send_slack_msg(attachments)
        print(f"🚀 총 {len(attachments)}건의 알림을 슬랙으로 보냈습니다.")
    else:
        print("📭 오늘은 새로 등록된 공시가 없습니다.")

if __name__ == "__main__":
    check_disclosures()
