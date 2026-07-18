import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. 페이지 초기 설정 및 커스텀 미니멀 CSS
st.set_page_config(
    page_title="Apartment Price Tracker | 실거래가 대시보드",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 상용 핀테크 / 리얼티 SaaS 스타일 커스텀 CSS (토스/호갱노노 톤앤매너)
PREMIUM_SAAS_CSS = """
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* 글로벌 폰트 및 여백 */
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
        background-color: #ffffff;
        color: #0f172a;
    }

    /* 메인 컨테이너 과감한 넉넉한 padding */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 5rem !important;
        max-width: 1280px;
    }
    
    /* 라이브 상단 헤더 & 에메랄드 펄스 뱃지 */
    .header-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .brand-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #0f172a;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: 1.05rem;
        color: #64748b;
        margin-top: 0.4rem;
        font-weight: 400;
    }
    
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background-color: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        padding: 0.4rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
    
    /* 럭셔리 KPI 메트릭 카드 */
    .kpi-card-premium {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.6rem 1.4rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card-premium:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
    }
    .kpi-tag {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .kpi-val {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .kpi-sub-text {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* 실시간 뉴스 & 피드 컴포넌트 */
    .feed-drawer {
        background-color: #0f172a;
        color: #f8fafc;
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        margin-top: 1.5rem;
    }
    .feed-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #38bdf8;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-bottom: 0.8rem;
    }
    .feed-body {
        font-size: 0.84rem;
        color: #cbd5e1;
        line-height: 1.5;
    }
    .feed-chip {
        display: inline-block;
        background: #1e293b;
        color: #94a3b8;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        margin-top: 0.4rem;
    }
    
    /* stTab 스타일 업그레이드 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #f1f5f9;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 700;
        padding: 0.8rem 0;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #0f172a !important;
        border-bottom-color: #0f172a !important;
    }
    
    /* 테이블 둥근 스타일링 */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #f1f5f9;
    }
</style>
"""
st.markdown(PREMIUM_SAAS_CSS, unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@st.cache_data(ttl=60)
def load_data():
    trade_path = os.path.join(DATA_DIR, "apt_trade.json")
    rent_path = os.path.join(DATA_DIR, "apt_rent.json")
    feed_path = os.path.join(DATA_DIR, "update_feed.json")
    
    trade_df = pd.DataFrame()
    rent_df = pd.DataFrame()
    feed_info = {}
    
    if os.path.exists(trade_path):
        with open(trade_path, "r", encoding="utf-8") as f:
            trade_df = pd.DataFrame(json.load(f))
            
    if os.path.exists(rent_path):
        with open(rent_path, "r", encoding="utf-8") as f:
            rent_df = pd.DataFrame(json.load(f))
            
    if os.path.exists(feed_path):
        with open(feed_path, "r", encoding="utf-8") as f:
            feed_info = json.load(f)
            
    return trade_df, rent_df, feed_info


trade_df, rent_df, feed_info = load_data()

# 2. 브랜드 헤더 레인
last_updated = feed_info.get("last_updated", "실시간 수집 완료")
mode_title = feed_info.get("mode", "전국 시뮬레이션 실거래 데이터")

st.markdown(f"""
<div class="header-wrapper">
    <div>
        <div class="brand-title">전국 아파트 실거래가 모니터링</div>
        <div class="brand-subtitle">국토교통부 실시간 데이터를 기반으로 분석된 핀테크 모니터링 대시보드</div>
    </div>
    <div class="live-badge">
        <div class="pulse-dot"></div>
        <span>LIVE AUTO PIPELINE</span>
    </div>
</div>
""", unsafe_allow_html=True)


# 3. 사이드바 - 전국 2단계 스마트 지역 필터 & 컨트롤
with st.sidebar:
    st.markdown("### 🎛️ 전국 지역 검색 필터")
    
    # 1단계: 시/도 선택
    sido_list = ["전체"]
    if not trade_df.empty and "시도" in trade_df.columns:
        sido_list += sorted(trade_df["시도"].unique().tolist())
    selected_sido = st.selectbox("시 / 도 선택", sido_list)
    
    # 2단계: 구/군 선택 (가변)
    gu_list = ["전체"]
    if selected_sido != "전체" and not trade_df.empty and "구군" in trade_df.columns:
        filtered_gu = trade_df[trade_df["시도"] == selected_sido]["구군"].unique().tolist()
        gu_list += sorted(filtered_gu)
    selected_gu = st.selectbox("구 / 군 선택", gu_list)
    
    st.markdown("---")
    
    # 아파트 검색
    search_apt = st.text_input("아파트 단지명 검색", "", placeholder="예: 자이, 래미안, 엘스")
    
    # 전용면적 선택
    area_options = ["전체", "59㎡ 이하 (소형)", "59㎡ ~ 84㎡ (중형)", "84㎡ ~ 114㎡ (중대형)", "114㎡ 초과 (대형)"]
    selected_area = st.selectbox("전용면적 그룹", area_options)
    
    # 📌 최근 업데이트 피드 Drawer (구석 실시간 피드)
    st.markdown("""
    <div class="feed-drawer">
        <div class="feed-title">⚡ Live Activity Feed</div>
        <div class="feed-body">
            <strong>최근 수집:</strong> {time}<br/>
            <strong>데이터 상태:</strong> {mode}<br/>
            <div class="feed-chip">매매 {t_cnt:,}건</div>
            <div class="feed-chip">전월세 {r_cnt:,}건</div>
        </div>
    </div>
    """.format(
        time=last_updated,
        mode=mode_title,
        t_cnt=feed_info.get("trade_count", 0),
        r_cnt=feed_info.get("rent_count", 0)
    ), unsafe_allow_html=True)


# 면적 필터 함수
def filter_area(df, area_opt):
    if df.empty or area_opt == "전체":
        return df
    if "59㎡ 이하" in area_opt:
        return df[df["전용면적"] <= 59.9]
    elif "59㎡ ~ 84㎡" in area_opt:
        return df[(df["전용면적"] > 59.9) & (df["전용면적"] <= 84.99)]
    elif "84㎡ ~ 114㎡" in area_opt:
        return df[(df["전용면적"] > 84.99) & (df["전용면적"] <= 114.99)]
    elif "114㎡ 초과" in area_opt:
        return df[df["전용면적"] > 114.99]
    return df


# 4. 데이터 필터링 수행
f_trade = trade_df.copy()
f_rent = rent_df.copy()

if not f_trade.empty:
    if selected_sido != "전체" and "시도" in f_trade.columns:
        f_trade = f_trade[f_trade["시도"] == selected_sido]
    if selected_gu != "전체" and "구군" in f_trade.columns:
        f_trade = f_trade[f_trade["구군"] == selected_gu]
    if search_apt:
        f_trade = f_trade[f_trade["아파트"].str.contains(search_apt, case=False, na=False)]
    f_trade = filter_area(f_trade, selected_area)

if not f_rent.empty:
    if selected_sido != "전체" and "시도" in f_rent.columns:
        f_rent = f_rent[f_rent["시도"] == selected_sido]
    if selected_gu != "전체" and "구군" in f_rent.columns:
        f_rent = f_rent[f_rent["구군"] == selected_gu]
    if search_apt:
        f_rent = f_rent[f_rent["아파트"].str.contains(search_apt, case=False, na=False)]
    f_rent = filter_area(f_rent, selected_area)


# 5. 메인 대시보드 탭
tab_trade, tab_rent = st.tabs(["🏢 아파트 매매 실거래", "🔑 전·월세 실거래"])

# ==================== TAB 1: 아파트 매매 ====================
with tab_trade:
    if f_trade.empty:
        st.warning("선택하신 위치 및 검색 조건에 맞는 매매 거래 데이터가 없습니다.")
    else:
        avg_p = f_trade["거래금액_숫자"].mean()
        max_p = f_trade["거래금액_숫자"].max()
        min_p = f_trade["거래금액_숫자"].min()
        total_c = len(f_trade)
        
        # 4개의 상용 메트릭 카드 넉넉한 여백배치
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-tag">평균 매매 실거래가</div>
                <div class="kpi-val">{avg_p/10000:.2f} 억</div>
                <div class="kpi-sub-text">{avg_p:,.0f} 만원</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-tag">최고 거래 기록</div>
                <div class="kpi-val">{max_p/10000:.2f} 억</div>
                <div class="kpi-sub-text">{max_p:,.0f} 만원</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-tag">최저 거래 기록</div>
                <div class="kpi-val">{min_p/10000:.2f} 억</div>
                <div class="kpi-sub-text">{min_p:,.0f} 만원</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-tag">조회 거래 건수</div>
                <div class="kpi-val">{total_c:,} 건</div>
                <div class="kpi-sub-text">실시간 수집 실거래 내역</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br/><br/>", unsafe_allow_html=True)
        
        # 시세 추이 & 단지별 시세 고급 Plotly 차트
        graph_col1, graph_col2 = st.columns([1.6, 1])
        with graph_col1:
            st.markdown("### 📈 일자별 시세 변동 트렌드")
            daily = f_trade.groupby("계약일자")["거래금액_숫자"].mean().reset_index()
            daily["거래금액_억원"] = daily["거래금액_숫자"] / 10000
            
            fig_line = px.line(
                daily,
                x="계약일자",
                y="거래금액_억원",
                markers=True,
                template="plotly_white",
                color_discrete_sequence=["#0f172a"]
            )
            fig_line.update_traces(line_width=3, marker_size=6)
            fig_line.update_layout(
                xaxis=dict(showgrid=False, title="계약일자"),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="평균 매매가 (억원)"),
                hovermode="x unified",
                margin=dict(l=10, r=10, t=20, b=20),
                height=380
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
        with graph_col2:
            st.markdown("### 🏆 최고 시세 단지 Top 7")
            apt_grp = f_trade.groupby("아파트")["거래금액_숫자"].mean().reset_index()
            apt_grp["거래금액_억원"] = apt_grp["거래금액_숫자"] / 10000
            apt_top7 = apt_grp.sort_values(by="거래금액_억원", ascending=True).tail(7)
            
            fig_bar = px.bar(
                apt_top7,
                x="거래금액_억원",
                y="아파트",
                orientation="h",
                template="plotly_white",
                color_discrete_sequence=["#334155"]
            )
            fig_bar.update_layout(
                xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="평균가 (억원)"),
                yaxis=dict(showgrid=False, title=""),
                margin=dict(l=10, r=10, t=20, b=20),
                height=380
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("### 📋 실거래 내역 상세 리스트")
        show_cols = ["계약일자", "시도", "구군", "법정동", "아파트", "전용면적", "층", "건축년도", "거래금액"]
        available_cols = [c for c in show_cols if c in f_trade.columns]
        st.dataframe(
            f_trade[available_cols],
            use_container_width=True,
            hide_index=True
        )


# ==================== TAB 2: 전·월세 실거래 ====================
with tab_rent:
    if f_rent.empty:
        st.warning("선택하신 위치 및 검색 조건에 맞는 전·월세 데이터가 없습니다.")
    else:
        st.markdown("### 🔍 거래 임대 유형")
        rent_filter = st.radio("", ["전체", "전세", "월세"], horizontal=True)
        
        display_r = f_rent.copy()
        if rent_filter != "전체":
            display_r = display_r[display_r["구분"] == rent_filter]
            
        avg_dep = display_r["보증금액_숫자"].mean() if not display_r.empty else 0
        monthly_df = display_r[display_r["구분"] == "월세"]
        avg_monthly = monthly_df["월세금액_숫자"].mean() if not monthly_df.empty else 0
        total_r = len(display_r)
        
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-tag">평균 보증금</div>
                <div class="kpi-val">{avg_dep/10000:.2f} 억</div>
                <div class="kpi-sub-text">{avg_dep:,.0f} 만원</div>
            </div>
            """, unsafe_allow_html=True)
            
        with rc2:
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-tag">평균 월세금</div>
                <div class="kpi-val">{avg_monthly:,.0f} 만원</div>
                <div class="kpi-sub-text">월세 계약 건 대상</div>
            </div>
            """, unsafe_allow_html=True)
            
        with rc3:
            st.markdown(f"""
            <div class="kpi-card-premium">
                <div class="kpi-tag">전·월세 거래량</div>
                <div class="kpi-val">{total_r:,} 건</div>
                <div class="kpi-sub-text">선택 조건 거래 건수</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br/><br/>", unsafe_allow_html=True)
        st.markdown("### 📋 전·월세 실거래 내역 리스트")
        r_cols = ["계약일자", "구분", "시도", "구군", "법정동", "아파트", "전용면적", "층", "보증금액", "월세금액"]
        available_r_cols = [c for c in r_cols if c in display_r.columns]
        st.dataframe(
            display_r[available_r_cols],
            use_container_width=True,
            hide_index=True
        )
