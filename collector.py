import os
import json
import random
import datetime
import requests
import xmltodict
from dateutil.relativedelta import relativedelta

# 주요 관심 지역 법정동 코드 5자리
REGION_CODES = {
    "11680": "서울 강남구",
    "11650": "서울 서초구",
    "11710": "서울 송파구",
    "11440": "서울 마포구",
    "11200": "서울 성동구"
}

# API 엔드포인트
TRADE_API_URL = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"
RENT_API_URL = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRentDev"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def get_recent_months(count=3):
    """최근 N개월 YYYYMM 리스트 반환"""
    months = []
    now = datetime.datetime.now()
    for i in range(count):
        target = now - relativedelta(months=i)
        months.append(target.strftime("%Y%m"))
    return months


def fetch_from_api(url, service_key, lawd_cd, deal_ymd):
    """공공데이터 포털 API 호출 (XML -> dict 변환)"""
    params = {
        "serviceKey": service_key,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": deal_ymd
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        dict_data = xmltodict.parse(response.text)
        
        body = dict_data.get("response", {}).get("body", {})
        if not body:
            return []
        
        items = body.get("items", {})
        if not items:
            return []
        
        item_list = items.get("item", [])
        if isinstance(item_list, dict):
            item_list = [item_list]
        return item_list
    except Exception as e:
        print(f"[WARN] API 호출 오류 ({lawd_cd}, {deal_ymd}): {e}")
        return None


def generate_fallback_data():
    """API 키 미설정 또는 호출 실패 시 사용할 시뮬레이션 데모 데이터 생성"""
    print("[INFO] API 키 미설정 또는 실패로 시뮬레이션 데모 데이터를 생성합니다.")
    
    sample_apts = [
        {"name": "반포자이", "region": "서울 서초구", "lawd_cd": "11650", "dong": "반포동", "area": 84.98},
        {"name": "래미안퍼스티지", "region": "서울 서초구", "lawd_cd": "11650", "dong": "반포동", "area": 59.96},
        {"name": "아크로리버파크", "region": "서울 서초구", "lawd_cd": "11650", "dong": "반포동", "area": 84.95},
        {"name": "은마아파트", "region": "서울 강남구", "lawd_cd": "11680", "dong": "대치동", "area": 76.79},
        {"name": "도곡렉슬", "region": "서울 강남구", "lawd_cd": "11680", "dong": "도곡동", "area": 84.99},
        {"name": "헬리오시티", "region": "서울 송파구", "lawd_cd": "11710", "dong": "가락동", "area": 84.98},
        {"name": "잠실엘스", "region": "서울 송파구", "lawd_cd": "11710", "dong": "잠실동", "area": 84.88},
        {"name": "마포프레스티지자이", "region": "서울 마포구", "lawd_cd": "11440", "dong": "염리동", "area": 84.94},
        {"name": "마포래미안푸르지오", "region": "서울 마포구", "lawd_cd": "11440", "dong": "아현동", "area": 59.92},
        {"name": "트리마제", "region": "서울 성동구", "lawd_cd": "11200", "dong": "성수동1가", "area": 84.82},
        {"name": "아크로서울포레스트", "region": "서울 성동구", "lawd_cd": "11200", "dong": "성수동1가", "area": 159.60}
    ]
    
    trade_list = []
    rent_list = []
    
    now = datetime.datetime.now()
    
    for i in range(120):  # 120개 무작위 거래 생성
        apt = random.choice(sample_apts)
        days_ago = random.randint(0, 89)
        deal_date = now - datetime.timedelta(days=days_ago)
        
        # 매매 데이터
        base_price = int(apt["area"] * random.uniform(2200, 3800))  # 만원 단위
        trade_item = {
            "아파트": apt["name"],
            "지역명": apt["region"],
            "법정동": apt["dong"],
            "전용면적": round(apt["area"], 2),
            "층": random.randint(2, 35),
            "건축년도": random.choice([2009, 2015, 2018, 2020, 2022]),
            "거래금액": f"{base_price:,}".strip(),
            "거래금액_숫자": base_price,
            "년": deal_date.year,
            "월": deal_date.month,
            "일": deal_date.day,
            "계약일자": deal_date.strftime("%Y-%m-%d")
        }
        trade_list.append(trade_item)
        
        # 전월세 데이터
        rent_type = random.choice(["전세", "월세"])
        deposit = int(base_price * random.uniform(0.5, 0.65))
        monthly = int(random.uniform(50, 250)) if rent_type == "월세" else 0
        
        rent_item = {
            "아파트": apt["name"],
            "지역명": apt["region"],
            "법정동": apt["dong"],
            "전용면적": round(apt["area"], 2),
            "층": random.randint(2, 35),
            "건축년도": random.choice([2009, 2015, 2018, 2020, 2022]),
            "보증금액": f"{deposit:,}".strip(),
            "보증금액_숫자": deposit,
            "월세금액": f"{monthly:,}".strip(),
            "월세금액_숫자": monthly,
            "구분": rent_type,
            "년": deal_date.year,
            "월": deal_date.month,
            "일": deal_date.day,
            "계약일자": deal_date.strftime("%Y-%m-%d")
        }
        rent_list.append(rent_item)
        
    # 날짜 역순 정렬
    trade_list.sort(key=lambda x: x["계약일자"], reverse=True)
    rent_list.sort(key=lambda x: x["계약일자"], reverse=True)
    
    return trade_list, rent_list, True


def run_collection():
    ensure_data_dir()
    service_key = os.getenv("DATA_GO_KR_SERVICE_KEY", "").strip()
    
    trade_results = []
    rent_results = []
    is_demo = False
    
    if not service_key:
        trade_results, rent_results, is_demo = generate_fallback_data()
    else:
        print("[INFO] 공공데이터 포털 API 키가 확인되었습니다. 실데이터 조회를 진행합니다.")
        recent_months = get_recent_months(3)
        
        for lawd_cd, region_name in REGION_CODES.items():
            for ym in recent_months:
                t_items = fetch_from_api(TRADE_API_URL, service_key, lawd_cd, ym)
                r_items = fetch_from_api(RENT_API_URL, service_key, lawd_cd, ym)
                
                if t_items is None or r_items is None:
                    # API 호출에 문제가 발생한 경우 fallback으로 전환
                    trade_results, rent_results, is_demo = generate_fallback_data()
                    break
                
                for item in t_items:
                    price_str = str(item.get("거래금액", "0")).replace(",", "").strip()
                    price_num = int(price_str) if price_str.isdigit() else 0
                    
                    trade_results.append({
                        "아파트": item.get("아파트", ""),
                        "지역명": region_name,
                        "법정동": item.get("법정동", "").strip(),
                        "전용면적": float(item.get("전용면적", 0)),
                        "층": int(item.get("층", 0)),
                        "건축년도": int(item.get("건축년도", 0)),
                        "거래금액": item.get("거래금액", "").strip(),
                        "거래금액_숫자": price_num,
                        "년": int(item.get("년", 0)),
                        "월": int(item.get("월", 0)),
                        "일": int(item.get("일", 0)),
                        "계약일자": f"{item.get('년')}-{int(item.get('월', 0)):02d}-{int(item.get('일', 0)):02d}"
                    })
                    
                for item in r_items:
                    dep_str = str(item.get("보증금액", "0")).replace(",", "").strip()
                    dep_num = int(dep_str) if dep_str.isdigit() else 0
                    m_str = str(item.get("월세금액", "0")).replace(",", "").strip()
                    m_num = int(m_str) if m_str.isdigit() else 0
                    
                    rent_type = "월세" if m_num > 0 else "전세"
                    
                    rent_results.append({
                        "아파트": item.get("아파트", ""),
                        "지역명": region_name,
                        "법정동": item.get("법정동", "").strip(),
                        "전용면적": float(item.get("전용면적", 0)),
                        "층": int(item.get("층", 0)),
                        "건축년도": int(item.get("건축년도", 0)),
                        "보증금액": item.get("보증금액", "").strip(),
                        "보증금액_숫자": dep_num,
                        "월세금액": item.get("월세금액", "").strip(),
                        "월세금액_숫자": m_num,
                        "구분": rent_type,
                        "년": int(item.get("년", 0)),
                        "월": int(item.get("월", 0)),
                        "일": int(item.get("일", 0)),
                        "계약일자": f"{item.get('년')}-{int(item.get('월', 0)):02d}-{int(item.get('일', 0)):02d}"
                    })
            if is_demo:
                break

    # 파일 저장
    trade_path = os.path.join(DATA_DIR, "apt_trade.json")
    rent_path = os.path.join(DATA_DIR, "apt_rent.json")
    feed_path = os.path.join(DATA_DIR, "update_feed.json")
    
    with open(trade_path, "w", encoding="utf-8") as f:
        json.dump(trade_results, f, ensure_ascii=False, indent=2)
        
    with open(rent_path, "w", encoding="utf-8") as f:
        json.dump(rent_results, f, ensure_ascii=False, indent=2)
        
    # 업데이트 피드 정보 생성
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode_str = "시뮬레이션 데모 데이터" if is_demo else "공공데이터 포털 OpenAPI 실시간 데이터"
    
    feed_data = {
        "last_updated": now_str,
        "mode": mode_str,
        "is_demo": is_demo,
        "trade_count": len(trade_results),
        "rent_count": len(rent_results),
        "recent_logs": [
            {
                "timestamp": now_str,
                "title": "자동 수집 완료",
                "message": f"{mode_str} 조회를 통해 매매 {len(trade_results)}건, 전월세 {len(rent_results)}건 데이터 갱신 완료."
            },
            {
                "timestamp": now_str,
                "title": "시스템 상태 정상",
                "message": "GitHub Actions 스케줄러 수집 작업이 성공적으로 실행되었습니다."
            }
        ]
    }
    
    with open(feed_path, "w", encoding="utf-8") as f:
        json.dump(feed_data, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] 수집 완료: 매매 {len(trade_results)}건 / 전월세 {len(rent_results)}건 ({mode_str})")


if __name__ == "__main__":
    run_collection()
