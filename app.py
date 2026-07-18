import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. 페이지 초기 설정 및 커스텀 미니멀 CSS
st.set_page_config(
    page_title="아파트 실거래가 모니터링",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 단색 미니멀 커스텀 CSS 스타일링 (Slate Monochrome)
MINIMAL_CSS = """
<style>
    /* 전체 메인 배경 및 폰트 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    /* 타이틀 및 헤더 스타일 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 1.8rem;
    }
    
    /* KPI 메트릭 카드 단색 스타일 */
    .kpi-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: left;
        margin-bottom: 1rem;
    }
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748b;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.02em;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 0.4rem;
    }

    /* 피드 뉴스 카드 스타일 */
    .feed-card {
        background-color: #0f172a;
        color: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        font-size: 0.82rem;
        margin-top: 1rem;
    }
    .feed-header {
        font-weight: 600;
        font-size: 0.9rem;
        color: #38bdf8;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .feed-item {
        border-bottom: 1px solid #334155;
        padding: 0.5rem 0;
    }
    .feed-item:last-child {
        border-bottom: none;
    }
    .feed-time {
        font-size: 0.72rem;
        color: #94a3b8;
    }
    
    /* 스트림릿 기본 탭/버튼 미니멀 패칭 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        font-weight: 600;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #0f172a !important;
        border-bottom-color: #0f172a !important;
    }
</style>
"""
st.markdown(MINIMAL_CSS, unsafe_allow_html=True)


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@st.cache_data(ttl=300)
def load_data():
    trade_path = os.path.join(DATA_DIR, "apt_trade.json")
    rent_path = os.path.join(DATA_DIR, "apt_rent.json")
    feed_path = os.path.join(DATA_DIR, "update_feed.json")
    
    trade_df = pd.DataFrame()
    rent_df = pd.DataFrame()
    feed_info = {}
    
    if os.path.exists(trade_path):
        with open(trade_path, "r", encoding="utf-8") as f:
            trade_data = json.load(f)
            trade_df = pd.DataFrame(trade_data)
            
    if os.path.exists(rent_path):
        with open(rent_path, "r", encoding="utf-8") as f:
            rent_data = json.load(f)
            rent_df = pd.DataFrame(rent_data)
            
    if os.path.exists(feed_path):
        with open(feed_path, "r", encoding="utf-8") as f:
            feed_info = json.load(f)
            
    return trade_df, rent_df, feed_info


trade_df, rent_df, feed_info = load_data()

# 2. 헤더 및 서브타이틀
st.markdown('<div class="main-title">아파트 실거래가 변동 모니터링</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">국토교통부 실거래 데이터 기반 자동 갱신 분석 대시보드</div>', unsafe_allow_html=True)


# 3. 사이드바 구성 & 필터 & 최근 업데이트 피드
with st.sidebar:
    st.markdown("### 🔍 데이터 필터")
    
    # 지역 선택
    all_regions = ["전체"]
    if not trade_df.empty and "지역명" in trade_df.columns:
        all_regions += sorted(trade_df["지역명"].unique().tolist())
    selected_region = st.selectbox("지역 선택", all_regions)
    
    # 아파트 검색
    search_apt = st.text_input("아파트명 검색", "", placeholder="예: 자이, 래미안")
    
    # 면적 선택
    area_options = ["전체", "59㎡ 이하", "59㎡ ~ 84㎡", "84㎡ ~ 114㎡", "114㎡ 초과"]
    selected_area = st.selectbox("전용면적 범위", area_options)
    
    st.markdown("---")
    
    # 📌 구석 릴리즈/업데이트 피드 컴포넌트 (Live Update Feed)
    st.markdown("### 📡 실시간 업데이트 피드")
    
    last_updated = feed_info.get("last_updated", "수집 정보 없음")
    mode = feed_info.get("mode", "대기 중")
    t_cnt = feed_info.get("trade_count", 0)
    r_cnt = feed_info.get("rent_count", 0)
    
    st.markdown(f"""
    <div class="feed-card">
        <div class="feed-header">⚡ Live Feed Update</div>
        <div style="margin-bottom: 0.5rem;">
            <strong>마지막 갱신:</strong> {last_updated}<br/>
            <strong>수집 상태:</strong> {mode}
        </div>
        <div class="feed-item">
            <div class="feed-time">자동화 결과</div>
            <div>매매 <strong>{t_cnt:,}건</strong> / 전월세 <strong>{r_cnt:,}건</strong> 수집 갱신 완료</div>
        </div>
        <div class="feed-item">
            <div class="feed-time">시스템 안내</div>
            <div>GitHub Actions 매일 07:00 KST 자동 실행 중</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# 면적 필터 함수
def filter_area(df, area_opt):
    if df.empty or area_opt == "전체":
        return df
    if area_opt == "59㎡ 이하":
        return df[df["전용면적"] <= 59.9]
    elif area_opt == "59㎡ ~ 84㎡":
        return df[(df["전용면적"] > 59.9) & (df["전용면적"] <= 84.99)]
    elif area_opt == "84㎡ ~ 114㎡":
        return df[(df["전용면적"] > 84.99) & (df["전용면적"] <= 114.99)]
    elif area_opt == "114㎡ 초과":
        return df[df["전용면적"] > 114.99]
    return df


# 4. 데이터 필터링 적용
filtered_trade = trade_df.copy()
filtered_rent = rent_df.copy()

if not filtered_trade.empty:
    if selected_region != "전체":
        filtered_trade = filtered_trade[filtered_trade["지역명"] == selected_region]
    if search_apt:
        filtered_trade = filtered_trade[filtered_trade["아파트"].str.contains(search_apt, case=False, na=False)]
    filtered_trade = filter_area(filtered_trade, selected_area)

if not filtered_rent.empty:
    if selected_region != "전체":
        filtered_rent = filtered_rent[filtered_rent["지역명"] == selected_region]
    if search_apt:
        filtered_rent = filtered_rent[filtered_rent["아파트"].str.contains(search_apt, case=False, na=False)]
    filtered_rent = filter_area(filtered_rent, selected_area)


# 5. 메인 대시보드 탭 구성
tab1, tab2 = st.tabs(["🏢 아파트 매매 실거래", "🔑 전·월세 실거래"])

# ================= TAB 1: 아파트 매매 =================
with tab1:
    if filtered_trade.empty:
        st.info("조건에 일치하는 매매 실거래가 데이터가 없습니다.")
    else:
        avg_price = filtered_trade["거래금액_숫자"].mean()
        max_price = filtered_trade["거래금액_숫자"].max()
        min_price = filtered_trade["거래금액_숫자"].min()
        total_count = len(filtered_trade)
        
        # KPI 카드를 단색 미니멀 스타일로 4열 배치
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">평균 매매가</div>
                <div class="kpi-value">{avg_price/10000:.2f} 억</div>
                <div class="kpi-sub">{avg_price:,.0f} 만원</div>
            </div>
            """, unsafe_allow_html=True)
            
        with k2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">최고 거래가</div>
                <div class="kpi-value">{max_price/10000:.2f} 억</div>
                <div class="kpi-sub">{max_price:,.0f} 만원</div>
            </div>
            """, unsafe_allow_html=True)
            
        with k3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">최저 거래가</div>
                <div class="kpi-value">{min_price/10000:.2f} 억</div>
                <div class="kpi-sub">{min_price:,.0f} 만원</div>
            </div>
            """, unsafe_allow_html=True)
            
        with k4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">총 수집 거래량</div>
                <div class="kpi-value">{total_count:,} 건</div>
                <div class="kpi-sub">최근 3개월 실거래 건수</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # 시세 추이 단색 차트 (Monochrome Slate Theme)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("일자별 매매가 변동 추이")
            daily_trade = filtered_trade.groupby("계약일자")["거래금액_숫자"].mean().reset_index()
            daily_trade["거래금액_억원"] = daily_trade["거래금액_숫자"] / 10000
            
            fig_line = px.line(
                daily_trade,
                x="계약일자",
                y="거래금액_억원",
                markers=True,
                template="plotly_white",
                color_discrete_sequence=["#0f172a"]  # Dark Slate monochrome
            )
            fig_line.update_layout(
                xaxis_title="계약일자",
                yaxis_title="평균 매매가 (억원)",
                hovermode="x unified",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
        with c2:
            st.subheader("단지별 평균 매매가 Top 7")
            apt_top = filtered_trade.groupby("아파트")["거래금액_숫자"].mean().reset_index()
            apt_top["거래금액_억원"] = apt_top["거래금액_숫자"] / 10000
            apt_top = apt_top.sort_values(by="거래금액_억원", ascending=True).tail(7)
            
            fig_bar = px.bar(
                apt_top,
                x="거래금액_억원",
                y="아파트",
                orientation="h",
                template="plotly_white",
                color_discrete_sequence=["#475569"]  # Slate grey
            )
            fig_bar.update_layout(
                xaxis_title="평균가 (억원)",
                yaxis_title="",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # 상세 거래 내역
        st.subheader("매매 실거래 상세 내역")
        show_cols = ["계약일자", "지역명", "법정동", "아파트", "전용면적", "층", "건축년도", "거래금액"]
        st.dataframe(
            filtered_trade[show_cols],
            use_container_width=True,
            hide_index=True
        )


# ================= TAB 2: 전/월세 실거래 =================
with tab2:
    if filtered_rent.empty:
        st.info("조건에 일치하는 전·월세 실거래가 데이터가 없습니다.")
    else:
        rent_type_filter = st.radio("거래 유형 구분", ["전체", "전세", "월세"], horizontal=True)
        
        display_rent = filtered_rent.copy()
        if rent_type_filter != "전체":
            display_rent = display_rent[display_rent["구분"] == rent_type_filter]
            
        avg_dep = display_rent["보증금액_숫자"].mean()
        avg_monthly = display_rent[display_rent["구분"] == "월세"]["월세금액_숫자"].mean() if not display_rent[display_rent["구분"] == "월세"].empty else 0
        total_rent_cnt = len(display_rent)
        
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">평균 보증금</div>
                <div class="kpi-value">{avg_dep/10000:.2f} 억</div>
                <div class="kpi-sub">{avg_dep:,.0f} 만원</div>
            </div>
            """, unsafe_allow_html=True)
            
        with r2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">평균 월세금 (월세 계약)</div>
                <div class="kpi-value">{avg_monthly:,.0f} 만원</div>
                <div class="kpi-sub">월세 계약 대상 평균</div>
            </div>
            """, unsafe_allow_html=True)
            
        with r3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">전·월세 거래량</div>
                <div class="kpi-value">{total_rent_cnt:,} 건</div>
                <div class="kpi-sub">선택 유형 실거래 건수</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        st.subheader("전·월세 실거래 상세 내역")
        rent_show_cols = ["계약일자", "구분", "지역명", "법정동", "아파트", "전용면적", "층", "보증금액", "월세금액"]
        st.dataframe(
            display_rent[rent_show_cols],
            use_container_width=True,
            hide_index=True
        )
