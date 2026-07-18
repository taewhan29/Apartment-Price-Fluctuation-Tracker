# 🏢 전국 아파트 실거래가 무인 자동 수집 & 핀테크 대시보드

> **🌐 Streamlit Cloud 배포 주소**: (https://apartment-price-fluctuation-tracker.streamlit.app/)
---

## 🌟 주요 특징

1. **무인 24시간 자동화 & 날짜별 데이터 누적 (Git-backed MLOps)**
   - 매일 KST 07:00 (UTC 22:00) GitHub Actions 무인 자동 실행
   - 수집된 매매/전월세 데이터가 `data/history/apt_trade_YYYY-MM-DD.json` 형태로 덮어쓰지 않고 날짜별로 계속 누적 저장
   - 대시보드는 누적된 일별 히스토리 전체를 통합 병합하여 트렌드를 시각화

2. **핀테크 / 리얼티 SaaS 스타일 미니멀 UI (Slate Monochrome)**
   - 과감하고 넉넉한 공간감(Whitespace) 및 모노톤/슬레이트 계열 무채색 위주의 세련된 폰트와 인터페이스
   - `● DAILY AUTO PIPELINE` 에메랄드 펄스 뱃지 및 사이드바 구석 실시간 릴리즈 피드 컴포넌트 탑재

3. **대한민국 17개 광역시·도 전역 (250개 시/군/구) 완벽 지원**
   - 서울 25개 자치구, 경기 31개 시/군, 인천, 5대 광역시, 세종, 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주 전역 지원
   - 시/도 ➔ 구/군 2단계 동적 지역 필터링

4. **API 키 미등록 시 자동 Fallback 시뮬레이션 데이터 구동**
   - 공공데이터 API 키를 입력하지 않아도 시뮬레이션 데모 데이터가 자동 생성되어 대시보드가 차질 없이 작동

---

## 🔐 1. GitHub Secrets 등록 가이드 (API 키 최초 1회 연동)

무인 자동화 스케줄러가 실제 국토교통부 실거래 데이터를 수집하게 하려면 깃허브 저장소에 API 키를 등록합니다:

1. [공공데이터 포털(data.go.kr)](https://www.data.go.kr) 접속 후 **`국토교통부_아파트매매 실거래가 상세 자료`** 및 **`국토교통부_아파트 전월세 자료`** API 신청
2. 내 GitHub 저장소 페이지 **`Settings`** ➔ **`Secrets and variables`** ➔ **`Actions`** 클릭
3. **`New repository secret`** 클릭:
   - **Name**: `DATA_GO_KR_SERVICE_KEY`
   - **Secret**: 발급받은 **일반 인증키 (Encoding/Decoding 키)** 복사 후 저장

---

## 🌐 2. Streamlit Cloud 무상 24시간 웹 배포 방법

내 PC가 꺼져 있어도 언제나 웹에서 접속하는 방법:

1. [Streamlit Community Cloud](https://share.streamlit.io/) 접속 로그인
2. **`New app`** 클릭:
   - **Repository**: `taewhan29/Apartment-Price-Fluctuation-Tracker`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. **`Deploy!`** 클릭 후 완성된 웹 주소를 README 및 저장소 상단 About 웹사이트 주소에 등록!

---

## 💻 3. 로컬 실행 방법 (Local Test)

```bash
# uv 가상환경 구축 및 패키지 설치
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt

# 데이터 수집 및 날짜별 히스토리 누적 실행
python collector.py

# Streamlit 대시보드 실행
streamlit run app.py
```

---

## 📁 프로젝트 구조

```
Apartment-Price-Fluctuation-Tracker/
├── .agents/                    # 안티그래비티 에이전트 커스텀 규칙 및 스킬
├── .github/workflows/          # GitHub Actions 무인 자동화 워크플로우
│   └── daily_update.yml
├── data/                       # 자동 수집/갱신 데이터 스토어 (Git-backed)
│   ├── history/                # 📌 날짜별 누적 실거래가 히스토리 JSON 파일 디렉터리
│   │   ├── apt_trade_YYYY-MM-DD.json
│   │   └── apt_rent_YYYY-MM-DD.json
│   ├── apt_trade.json          # 최신 캐시 파일
│   ├── apt_rent.json
│   └── update_feed.json        # 라이브 피드 로그
├── collector.py                # 국토교통부 API 수집 & 날짜별 누적 파일 생성 모듈
├── app.py                      # 핀테크 미니멀 Streamlit 대시보드 웹 앱
├── requirements.txt            # 파이썬 의존성 패키지 명세
└── README.md                   # 프로젝트 사용 설명서 (Streamlit 웹 주소 안내)
```
