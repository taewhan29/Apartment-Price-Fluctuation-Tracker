# 🏢 아파트 실거래가 자동 수집 & 미니멀 대시보드 (Apartment Price Fluctuation Tracker)

> **컴퓨터가 꺼져 있어도 무인 자동 작동하는 24시간 실거래가 자동 수집 및 모니터링 시스템**  
> GitHub Actions 스케줄러가 매일 오전 7시(KST) 공공데이터 포털 API를 통해 최신 아파트 매매 및 전/월세 실거래 데이터를 수집하고, 단색 위주의 미니멀 Streamlit 대시보드로 시각화합니다.

---

## 🌟 핵심 특징

1. **무인 24시간 자동화 (GitHub Actions)**
   - 매일 KST 07:00 (UTC 22:00) 자동으로 데이터 수집 스크립트 실행
   - 수집된 매매/전월세 데이터 및 최근 업데이트 피드가 GitHub 저장소에 자동 커밋 & 푸시

2. **단색 미니멀 디자인 (Monochrome Slate UI)**
   - 자극적인 가공 색상을 배제하고 모노톤/슬레이트 계열 무채색 위주의 세련되고 깔끔한 폰트와 데이터 시각화 제공
   - KPI 통계 카드, 시세 추이 그래프, 아파트별 가격 분포 및 실거래 내역 검색 지원

3. **실시간 업데이트 피드 (Live Update Feed)**
   - 사이드바 구석에 데이터 수집 시각, 수집 건수, 갱신 상태 로그를 한눈에 볼 수 있는 타임스탬프 피드 탑재

4. **API 키 미등록 시 자동 Fallback 데모 모드**
   - 공공데이터 API 키를 입력하지 않아도 시뮬레이션 데모 데이터가 자동 생성되어 대시보드가 차질 없이 구동

---

## 🔐 1. GitHub Secrets 등록 가이드 (API 연동 방법)

실제 공공데이터 포털의 실거래가 데이터를 수집하려면 GitHub Secrets에 API 키를 등록해야 합니다:

1. [공공데이터 포털(data.go.kr)](https://www.data.go.kr)에 접속 후 **`국토교통부_아파트매매 실거래가 상세 자료`** 및 **`국토교통부_아파트 전월세 자료`** API 신청 (즉시 승인)
2. 내 깃허브 저장소 페이지의 **`Settings`** ➔ **`Secrets and variables`** ➔ **`Actions`** 메뉴 이동
3. **`New repository secret`** 버튼 클릭 후 아래 항목 추가:
   - **Name**: `DATA_GO_KR_SERVICE_KEY`
   - **Secret**: 공공데이터 포털에서 발급받은 **인코딩/디코딩 일반 인증키**

---

## 🚀 2. Streamlit Cloud 무상 24시간 웹 배포 가이드

내 PC가 꺼져 있어도 항상 접속 가능한 대시보드로 배포하는 방법입니다:

1. [Streamlit Community Cloud](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인
2. **`New app`** 클릭
3. 저장소 정보 입력:
   - **Repository**: `taewhan29/Apartment-Price-Fluctuation-Tracker`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. **`Deploy!`** 버튼 클릭 후 배포 완료!

---

## 💻 3. 로컬 실행 방법 (Local Test)

```bash
# 가상환경 생성 및 의존성 설치 (uv 전용)
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt

# 데이터 수집 스크립트 실행
python collector.py

# Streamlit 대시보드 실행
streamlit run app.py
```

---

## 🛠️ 프로젝트 구조

```
Apartment-Price-Fluctuation-Tracker/
├── .agents/                    # 안티그래비티 에이전트 커스텀 규칙 및 스킬
├── .github/workflows/          # GitHub Actions 무인 자동화 워크플로우
│   └── daily_update.yml
├── data/                       # 자동 수집/갱신 데이터 스토어 (Git-backed)
│   ├── apt_trade.json
│   ├── apt_rent.json
│   └── update_feed.json
├── collector.py                # 공공데이터 API 수집 & 데모 데이터 생성 모듈
├── app.py                      # 미니멀 Streamlit 대시보드 애플리케이션
├── requirements.txt            # 파이썬 의존성 패키지 명세
└── README.md                   # 프로젝트 사용 설명서
```