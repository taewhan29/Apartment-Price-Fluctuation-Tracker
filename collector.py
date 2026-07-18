import os
import json
import datetime
import requests
import xmltodict
from dateutil.relativedelta import relativedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_DIR = os.path.join(DATA_DIR, "history")
LAWD_JSON_PATH = os.path.join(DATA_DIR, "lawd_code.json")

# `.env` 파일 로드 헬퍼
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip("'\"")

load_env_file()

# 법정동 코드 로드
def load_nationwide_regions():
    if os.path.exists(LAWD_JSON_PATH):
        with open(LAWD_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

NATIONWIDE_REGIONS = load_nationwide_regions()

# API 엔드포인트
TRADE_API_URL = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"
RENT_API_URL = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRentDev"


def ensure_dirs():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR, exist_ok=True)


def get_recent_months(count=2):
    """최근 N개월 YYYYMM 리스트 반환"""
    months = []
    now = datetime.datetime.now()
    for i in range(count):
        target = now - relativedelta(months=i)
        months.append(target.strftime("%Y%m"))
    return months


def fetch_from_api(url, service_key, lawd_cd, deal_ymd):
    """국토교통부 공공데이터 포털 API 실제 호출"""
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


def run_collection():
    ensure_dirs()
    service_key = os.getenv("DATA_GO_KR_SERVICE_KEY", "").strip()
    
    trade_results = []
    rent_results = []
    
    if not service_key:
        print("[WARN] DATA_GO_KR_SERVICE_KEY가 설정되지 않았습니다. 실제 수집을 위해 API 키를 설정해주세요.")
    else:
        print("[INFO] 공공데이터 포털 API 키가 확인되었습니다. 국토교통부 실시간 수집을 시작합니다.")
        recent_months = get_recent_months(2)
        
        for sido, gu_dict in NATIONWIDE_REGIONS.items():
            for lawd_cd, gu_name in gu_dict.items():
                region_full_name = f"{sido} {gu_name}"
                for ym in recent_months:
                    t_items = fetch_from_api(TRADE_API_URL, service_key, lawd_cd, ym)
                    r_items = fetch_from_api(RENT_API_URL, service_key, lawd_cd, ym)
                    
                    if t_items:
                        for item in t_items:
                            price_str = str(item.get("거래금액", "0")).replace(",", "").strip()
                            price_num = int(price_str) if price_str.isdigit() else 0
                            
                            trade_results.append({
                                "시도": sido,
                                "구군": gu_name,
                                "지역명": region_full_name,
                                "법정동": str(item.get("법정동", "")).strip(),
                                "아파트": str(item.get("아파트", "")).strip(),
                                "전용면적": float(item.get("전용면적", 0)),
                                "층": int(item.get("층", 0)),
                                "건축년도": int(item.get("건축년도", 0)),
                                "거래금액": str(item.get("거래금액", "")).strip(),
                                "거래금액_숫자": price_num,
                                "년": int(item.get("년", 0)),
                                "월": int(item.get("월", 0)),
                                "일": int(item.get("일", 0)),
                                "계약일자": f"{item.get('년')}-{int(item.get('월', 0)):02d}-{int(item.get('일', 0)):02d}"
                            })
                            
                    if r_items:
                        for item in r_items:
                            dep_str = str(item.get("보증금액", "0")).replace(",", "").strip()
                            dep_num = int(dep_str) if dep_str.isdigit() else 0
                            m_str = str(item.get("월세금액", "0")).replace(",", "").strip()
                            m_num = int(m_str) if m_str.isdigit() else 0
                            
                            rent_type = "월세" if m_num > 0 else "전세"
                            
                            rent_results.append({
                                "시도": sido,
                                "구군": gu_name,
                                "지역명": region_full_name,
                                "법정동": str(item.get("법정동", "")).strip(),
                                "아파트": str(item.get("아파트", "")).strip(),
                                "전용면적": float(item.get("전용면적", 0)),
                                "층": int(item.get("층", 0)),
                                "건축년도": int(item.get("건축년도", 0)),
                                "보증금액": str(item.get("보증금액", "")).strip(),
                                "보증금액_숫자": dep_num,
                                "월세금액": str(item.get("월세금액", "")).strip(),
                                "월세금액_숫자": m_num,
                                "구분": rent_type,
                                "년": int(item.get("년", 0)),
                                "월": int(item.get("월", 0)),
                                "일": int(item.get("일", 0)),
                                "계약일자": f"{item.get('년')}-{int(item.get('월', 0)):02d}-{int(item.get('일', 0)):02d}"
                            })

    # 파일 저장 (진짜 수집 데이터만 기록)
    trade_path = os.path.join(DATA_DIR, "apt_trade.json")
    rent_path = os.path.join(DATA_DIR, "apt_rent.json")
    feed_path = os.path.join(DATA_DIR, "update_feed.json")
    
    with open(trade_path, "w", encoding="utf-8") as f:
        json.dump(trade_results, f, ensure_ascii=False, indent=2)
        
    with open(rent_path, "w", encoding="utf-8") as f:
        json.dump(rent_results, f, ensure_ascii=False, indent=2)
        
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    hist_trade_path = os.path.join(HISTORY_DIR, f"apt_trade_{today_str}.json")
    hist_rent_path = os.path.join(HISTORY_DIR, f"apt_rent_{today_str}.json")
    
    with open(hist_trade_path, "w", encoding="utf-8") as f:
        json.dump(trade_results, f, ensure_ascii=False, indent=2)
        
    with open(hist_rent_path, "w", encoding="utf-8") as f:
        json.dump(rent_results, f, ensure_ascii=False, indent=2)
        
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    feed_data = {
        "last_updated": now_str,
        "mode": "국토교통부 OpenAPI 실시간 실거래 데이터 전용",
        "is_demo": False,
        "trade_count": len(trade_results),
        "rent_count": len(rent_results),
        "history_file": f"apt_trade_{today_str}.json",
        "recent_logs": [
            {
                "timestamp": now_str,
                "title": f"실제 데이터 수집 완료 ({today_str})",
                "message": f"국토교통부 API 수집 결과: 매매 {len(trade_results):,}건, 전월세 {len(rent_results):,}건 저장 완료."
            }
        ]
    }
    
    with open(feed_path, "w", encoding="utf-8") as f:
        json.dump(feed_data, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] 국토교통부 실거래 데이터 수집 기록 완료: 매매 {len(trade_results)}건 / 전월세 {len(rent_results)}건")


if __name__ == "__main__":
    run_collection()
