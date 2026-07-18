import os
import json
import random
import datetime
import requests
import xmltodict
from dateutil.relativedelta import relativedelta

# `.env` 파일이 존재할 경우 자동 로드 헬퍼
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

# 🇰🇷 대한민국 17개 광역시·도 전역 (250여 개 전체 시/군/구) 법정동 5자리 코드 매핑
NATIONWIDE_REGIONS = {
    "서울특별시": {
        "11110": "종로구", "11140": "중구", "11170": "용산구", "11200": "성동구", "11215": "광진구",
        "11230": "동대문구", "11260": "중랑구", "11290": "성북구", "11305": "강북구", "11320": "도봉구",
        "11350": "노원구", "11380": "은평구", "11410": "서대문구", "11440": "마포구", "11470": "양천구",
        "11500": "강서구", "11530": "구로구", "11545": "금천구", "11560": "영등포구", "11590": "동작구",
        "11620": "관악구", "11650": "서초구", "11680": "강남구", "11710": "송파구", "11740": "강동구"
    },
    "부산광역시": {
        "26110": "중구", "26140": "서구", "26170": "동구", "26200": "영도구", "26230": "부산진구",
        "26260": "동래구", "26290": "남구", "26320": "북구", "26350": "해운대구", "26380": "사하구",
        "26410": "금정구", "26440": "강서구", "26470": "연제구", "26500": "수영구", "26530": "사상구", "26710": "기장군"
    },
    "대구광역시": {
        "27110": "중구", "27140": "동구", "27170": "서구", "27200": "남구", "27230": "북구",
        "27260": "수성구", "27290": "달서구", "27710": "달성군", "27720": "군위군"
    },
    "인천광역시": {
        "28110": "중구", "28140": "동구", "28177": "미추홀구", "28185": "연수구", "28200": "남동구",
        "28237": "부평구", "28245": "계양구", "28260": "서구", "28710": "강화군", "28720": "옹진군"
    },
    "광주광역시": {
        "29110": "동구", "29140": "서구", "29155": "남구", "29170": "북구", "29200": "광산구"
    },
    "대전광역시": {
        "30110": "동구", "30140": "중구", "30170": "서구", "30200": "유성구", "30230": "대덕구"
    },
    "울산광역시": {
        "31110": "중구", "31140": "남구", "31170": "동구", "31200": "북구", "31710": "울주군"
    },
    "세종특별자치시": {
        "36110": "세종시"
    },
    "경기도": {
        "41111": "수원시 장안구", "41113": "수원시 권선구", "41115": "수원시 팔달구", "41117": "수원시 영통구",
        "41131": "성남시 수정구", "41133": "성남시 중원구", "41135": "성남시 분당구", "41150": "의정부시",
        "41171": "안양시 만안구", "41173": "안양시 동안구", "41190": "부천시", "41210": "광명시",
        "41220": "평택시", "41250": "동두천시", "41271": "안산시 상록구", "41273": "안산시 단원구",
        "41281": "고양시 덕양구", "41285": "고양시 일산동구", "41287": "고양시 일산서구", "41290": "과천시",
        "41310": "구리시", "41360": "남양주시", "41370": "오산시", "41390": "시흥시", "41410": "군포시",
        "41430": "의왕시", "41450": "하남시", "41461": "용인시 처인구", "41463": "용인시 기흥구",
        "41465": "용인시 수지구", "41480": "파주시", "41500": "이천시", "41550": "안성시", "41570": "김포시",
        "41590": "화성시", "41610": "광주시", "41630": "양주시", "41650": "포천시", "41670": "여주시",
        "41800": "양평군", "41820": "가평군", "41830": "연천군"
    },
    "강원특별자치도": {
        "42110": "춘천시", "42130": "원주시", "42150": "강릉시", "42170": "동해시", "42190": "태백시",
        "42210": "속초시", "42230": "삼척시", "42720": "홍천군", "42730": "횡성군", "42750": "영월군",
        "42760": "평창군", "42770": "정선군", "42780": "철원군", "42790": "화천군", "42800": "양구군",
        "42810": "인제군", "42820": "고성군", "42830": "양양군"
    },
    "충청북도": {
        "43111": "청주시 상당구", "43112": "청주시 서원구", "43113": "청주시 흥덕구", "43114": "청주시 청원구",
        "43130": "충주시", "43150": "제천시", "43720": "보은군", "43730": "옥천군", "43740": "영동군",
        "43745": "증평군", "43750": "진천군", "43760": "괴산군", "43770": "음성군", "43800": "단양군"
    },
    "충청남도": {
        "44131": "천안시 동남구", "44133": "천안시 서북구", "44150": "공주시", "44180": "보령시",
        "44200": "아산시", "44210": "서산시", "44230": "논산시", "44250": "계룡시", "44270": "당진시",
        "44710": "금산군", "44760": "부여군", "44770": "서천군", "44790": "청양군", "44800": "홍성군",
        "44810": "예산군", "44825": "태안군"
    },
    "전북특별자치도": {
        "45111": "전주시 완산구", "45113": "전주시 덕진구", "45130": "군산시", "45140": "익산시",
        "45190": "정읍시", "45210": "남원시", "45230": "김제시", "45710": "완주군", "45720": "진안군",
        "45730": "무주군", "45740": "장수군", "45750": "임실군", "45770": "순창군", "45790": "고창군", "45800": "부안군"
    },
    "전라남도": {
        "46110": "목포시", "46130": "여수시", "46150": "순천시", "46160": "나주시", "46170": "광양시",
        "46710": "담양군", "46720": "곡성군", "46730": "구례군", "46770": "고흥군", "46780": "보성군",
        "46790": "화순군", "46800": "장흥군", "46810": "강진군", "46820": "해남군", "46830": "영암군",
        "46840": "무안군", "46860": "함평군", "46870": "영광군", "46880": "장성군", "46890": "완도군",
        "46900": "진도군", "46910": "신안군"
    },
    "경상북도": {
        "47111": "포항시 남구", "47113": "포항시 북구", "47130": "경주시", "47150": "김천시",
        "47170": "안동시", "47190": "구미시", "47210": "영주시", "47230": "영천시", "47250": "상주시",
        "47280": "문경시", "47290": "경산시", "47720": "군위군", "47730": "의성군", "47750": "청송군",
        "47760": "영양군", "47770": "영덕군", "47820": "청도군", "47830": "고령군", "47840": "성주군",
        "47850": "칠곡군", "47900": "예천군", "47920": "봉화군", "47930": "울진군", "47940": "울릉군"
    },
    "경상남도": {
        "48121": "창원시 의창구", "48123": "창원시 성산구", "48125": "창원시 마산합포구", "48127": "창원시 마산회원구",
        "48129": "창원시 진해구", "48170": "진주시", "48190": "통영시", "48220": "사천시", "48240": "김해시",
        "48270": "밀양시", "48310": "거제시", "48330": "양산시", "48720": "의령군", "48730": "함안군",
        "48740": "창녕군", "48840": "고성군", "48850": "남해군", "48860": "하동군", "48870": "산청군",
        "48880": "함양군", "48890": "거창군", "48950": "합천군"
    },
    "제주특별자치도": {
        "50110": "제주시", "50130": "서귀포시"
    }
}

# API 엔드포인트
TRADE_API_URL = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"
RENT_API_URL = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRentDev"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def get_recent_months(count=2):
    """최근 N개월 YYYYMM 리스트 반환"""
    months = []
    now = datetime.datetime.now()
    for i in range(count):
        target = now - relativedelta(months=i)
        months.append(target.strftime("%Y%m"))
    return months


def fetch_from_api(url, service_key, lawd_cd, deal_ymd):
    """공공데이터 포털 API 호출"""
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
    """API 키 미설정 시 전국 17개 시/도 전체를 아우르는 풍부한 시뮬레이션 데모 데이터 생성"""
    print("[INFO] API 인증키 미설정으로 대한민국 17개 시/도 전역 샘플 데이터를 생성합니다.")
    
    trade_list = []
    rent_list = []
    now = datetime.datetime.now()
    
    # 17개 시/도의 모든 구/군에서 샘플 생성
    for sido, gu_dict in NATIONWIDE_REGIONS.items():
        for lawd_cd, gu_name in gu_dict.items():
            # 구별로 2~4개 거래 생성
            for idx in range(random.randint(2, 4)):
                days_ago = random.randint(0, 59)
                deal_date = now - datetime.timedelta(days=days_ago)
                
                # 시도별 시세 반영
                base_mult = 1.0
                if "서울" in sido: base_mult = 2.5
                elif "경기" in sido or "인천" in sido: base_mult = 1.6
                elif "부산" in sido or "대구" in sido or "대전" in sido or "세종" in sido: base_mult = 1.4
                
                area = random.choice([59.95, 84.98, 114.90])
                base_price = int(area * random.uniform(1500, 3200) * base_mult)
                apt_name = f"{gu_name} 푸르지오 자이 {idx+1}단지"
                dong_name = f"{gu_name}동"
                
                trade_item = {
                    "시도": sido,
                    "구군": gu_name,
                    "지역명": f"{sido} {gu_name}",
                    "법정동": dong_name,
                    "아파트": apt_name,
                    "전용면적": round(area, 2),
                    "층": random.randint(2, 28),
                    "건축년도": random.choice([2010, 2016, 2020, 2023]),
                    "거래금액": f"{base_price:,}".strip(),
                    "거래금액_숫자": base_price,
                    "년": deal_date.year,
                    "월": deal_date.month,
                    "일": deal_date.day,
                    "계약일자": deal_date.strftime("%Y-%m-%d")
                }
                trade_list.append(trade_item)
                
                # 전월세
                rent_type = random.choice(["전세", "전세", "월세"])
                deposit = int(base_price * random.uniform(0.5, 0.65))
                monthly = int(random.uniform(50, 180)) if rent_type == "월세" else 0
                
                rent_item = {
                    "시도": sido,
                    "구군": gu_name,
                    "지역명": f"{sido} {gu_name}",
                    "법정동": dong_name,
                    "아파트": apt_name,
                    "전용면적": round(area, 2),
                    "층": random.randint(2, 28),
                    "건축년도": random.choice([2010, 2016, 2020, 2023]),
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
        print("[INFO] 공공데이터 포털 API 키가 확인되었습니다. 대한민국 17개 시/도 전체 조회를 시작합니다.")
        recent_months = get_recent_months(2)
        
        fetched_success = False
        for sido, gu_dict in NATIONWIDE_REGIONS.items():
            for lawd_cd, gu_name in gu_dict.items():
                region_full_name = f"{sido} {gu_name}"
                for ym in recent_months:
                    t_items = fetch_from_api(TRADE_API_URL, service_key, lawd_cd, ym)
                    r_items = fetch_from_api(RENT_API_URL, service_key, lawd_cd, ym)
                    
                    if t_items is None or r_items is None:
                        continue
                    
                    fetched_success = True
                    for item in t_items:
                        price_str = str(item.get("거래금액", "0")).replace(",", "").strip()
                        price_num = int(price_str) if price_str.isdigit() else 0
                        
                        trade_results.append({
                            "시도": sido,
                            "구군": gu_name,
                            "지역명": region_full_name,
                            "법정동": item.get("법정동", "").strip(),
                            "아파트": item.get("아파트", ""),
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
                            "시도": sido,
                            "구군": gu_name,
                            "지역명": region_full_name,
                            "법정동": item.get("법정동", "").strip(),
                            "아파트": item.get("아파트", ""),
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

        if not fetched_success or (len(trade_results) == 0 and len(rent_results) == 0):
            print("[WARN] API 호출 응답이 없어 시뮬레이션 샘플 데이터로 전환합니다.")
            trade_results, rent_results, is_demo = generate_fallback_data()

    # 파일 저장
    trade_path = os.path.join(DATA_DIR, "apt_trade.json")
    rent_path = os.path.join(DATA_DIR, "apt_rent.json")
    feed_path = os.path.join(DATA_DIR, "update_feed.json")
    
    with open(trade_path, "w", encoding="utf-8") as f:
        json.dump(trade_results, f, ensure_ascii=False, indent=2)
        
    with open(rent_path, "w", encoding="utf-8") as f:
        json.dump(rent_results, f, ensure_ascii=False, indent=2)
        
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode_str = "전국 17개 시/도 시뮬레이션 데이터" if is_demo else "국토교통부 OpenAPI 17개 시/도 실시간 데이터"
    
    feed_data = {
        "last_updated": now_str,
        "mode": mode_str,
        "is_demo": is_demo,
        "trade_count": len(trade_results),
        "rent_count": len(rent_results),
        "recent_logs": [
            {
                "timestamp": now_str,
                "title": "대한민국 전역 수집 성공",
                "message": f"현재 시각({now_str}) 기준 17개 시/도 전역 매매 {len(trade_results):,}건, 전월세 {len(rent_results):,}건 수집 완료."
            },
            {
                "timestamp": now_str,
                "title": "전국 커버리지",
                "message": "서울 25개 구, 경기 31개 시군, 인천, 5대 광역시, 강원, 충청, 전라, 경상, 제주 전역 포함."
            }
        ]
    }
    
    with open(feed_path, "w", encoding="utf-8") as f:
        json.dump(feed_data, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] 현재 시각 전국 데이터 수집 완료: 매매 {len(trade_results)}건 / 전월세 {len(rent_results)}건 ({mode_str})")


if __name__ == "__main__":
    run_collection()
