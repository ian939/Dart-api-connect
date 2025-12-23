import OpenDartReader
import requests
import os
from datetime import datetime

# 1. 환경 변수 설정
DART_TOKEN = os.environ.get('DART_TOKEN')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

dart = OpenDartReader(DART_TOKEN)

# 2. 감시 대상 기업 리스트
companies = {
    "⚡ 급속 충전": ["브라이트에너지파트너스", "채비", "이브이시스"],
    "🔌 완속 충전": ["플러그링크", "지에스차지비", "지에스커넥트", "에버온"]
}

def record_history(message):
    """실행 결과를 history.csv 파일에 누적 기록"""
    # 날짜 형식: 25.12.23
    today_str = datetime.now().strftime('%y.%m.%d')
    log_entry = f"{today_str} {message}"
    
    # 'a' 모드는 기존 내용 뒤에 이어서 씁니다. (파일이 없으면 새로 생성)
    # utf-8-sig는 엑셀에서 한글이 바로 보이게 해주는 인코딩입니다.
    with open('history.csv', 'a', encoding='utf-8-sig') as f:
        f.write(log_entry + '\n')
    print(f"📝 로그 기록 완료: {log_entry}")

def send_slack_msg(attachments):
    """슬랙 메시지 전송"""
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
    today = datetime.now().strftime('%Y%m%d')
    attachments = []
    
    print(f"🔍 {today} 공시 확인 시작...")

    for category, names in companies.items():
        for name in names:
            try:
                df = dart.list(name, start=today)
                if df is not None and not df.empty:
                    for i in range(len(df)):
                        title = df.iloc[i]['report_nm']
                        rcp_no = df.iloc[i]['rcept_no']
                        link = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"
                        
                        color = "#F27100" if "급속" in category else "#22AEEF"
                        attachment = {
                            "color": color,
                            "title": f"[{category}] {name}",
                            "text": f"📄 *{title}*\n🔗 <{link}|공시 상세 보기>",
                            "footer": "DART 자동 알림 서비스",
                            "ts": int(datetime.now().timestamp())
                        }
                        attachments.append(attachment)
                else:
                    print(f"  - {name}: 신규 공시 없음")
            except Exception as e:
                print(f"⚠️ {name} 조회 중 오류 발생: {e}")

    # 결과에 따른 슬랙 발송 및 로그 기록
    if attachments:
        send_slack_msg(attachments)
        record_history(f"신규공시 {len(attachments)}건 발견 및 알림 완료")
    else:
        # 요청하신 형식: 25.12.23 신규등록공시 없음
        record_history("신규등록공시 없음")
        print("📭 오늘은 새로 등록된 공시가 없습니다.")

if __name__ == "__main__":
    check_disclosures()
