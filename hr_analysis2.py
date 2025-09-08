import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')


# Streamlit 페이지 설정
st.set_page_config(
    page_title="퇴직율 대시보드", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일 설정
sns.set_theme(style="whitegrid", palette="husl",font="Malgun Gothic")

# CSS 스타일 적용
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-left: 5px solid #1f77b4;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 1) 데이터 로드 함수
@st.cache_data
def load_df(path: str = "HR Data.csv") -> pd.DataFrame:
    """HR 데이터를 로드하고 전처리하는 함수"""
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except FileNotFoundError:
        st.error("HR Data.csv 파일을 찾을 수 없습니다.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()
    
    # 데이터 전처리
    if "퇴직여부" in df.columns:
        df["퇴직"] = df["퇴직여부"].map({"Yes": 1, "No": 0}).astype("int8")
    
    # 불필요한 컬럼 제거
    drop_cols = ['직원수', '18세이상'] if all(col in df.columns for col in ['직원수', '18세이상']) else []
    if drop_cols:
        df.drop(drop_cols, axis=1, inplace=True)
    
    return df

# 데이터 로드
df = load_df()

if df.empty:
    st.error("데이터가 없습니다. 'HR Data.csv' 파일을 확인하세요.")
    st.stop()

# 메인 헤더
st.markdown('<h1 class="main-header">📊 퇴직율 분석 대시보드</h1>', unsafe_allow_html=True)
st.markdown("---")

# KPI 섹션
if "퇴직" in df.columns:
    n = len(df)
    quit_n = int(df["퇴직"].sum())
    quit_rate = df["퇴직"].mean() * 100
    stay_rate = 100 - quit_rate
    
    st.markdown('<h2 class="sub-header">📈 핵심 지표</h2>', unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.metric(
            label="👥 전체 직원 수",
            value=f"{n:,}명",
            delta=f"기준: {pd.Timestamp.now().strftime('%Y-%m')}"
        )
    
    with k2:
        st.metric(
            label="🚪 퇴직자 수",
            value=f"{quit_n:,}명",
            delta=f"{quit_rate:.1f}% 비율"
        )
    
    with k3:
        st.metric(
            label="✅ 유지율",
            value=f"{stay_rate:.1f}%",
            delta="높을수록 좋음" if stay_rate > 80 else "개선 필요",
            delta_color="normal" if stay_rate > 80 else "inverse"
        )
    
    with k4:
        st.metric(
            label="❌ 퇴직율",
            value=f"{quit_rate:.1f}%",
            delta="낮을수록 좋음" if quit_rate < 20 else "주의 필요",
            delta_color="inverse" if quit_rate < 20 else "normal"
        )

st.markdown("---")

# 인사이트 박스
if "퇴직" in df.columns:
    insight_text = f"""
    **💡 주요 인사이트**
    - 전체 직원 중 **{quit_rate:.1f}%**가 퇴직했습니다.
    - 유지율이 **{stay_rate:.1f}%**로 {'양호한' if stay_rate > 80 else '개선이 필요한'} 수준입니다.
    - {'퇴직율이 적정 수준을 유지하고 있습니다.' if quit_rate < 15 else '퇴직율 감소를 위한 대책이 필요합니다.'}
    """
    st.markdown(f'<div class="insight-box" style="color : black">{insight_text}</div>', unsafe_allow_html=True)

# 그래프 섹션
st.markdown('<h2 class="sub-header">📊 상세 분석</h2>', unsafe_allow_html=True)

# 1) 부서별 퇴직율
if "부서" in df.columns and "퇴직" in df.columns:
    dept_quit = (df.groupby("부서")["퇴직"].agg(['mean', 'count']) * 100).round(1)
    dept_quit.columns = ['퇴직율', '직원수_pct']
    dept_quit = dept_quit.sort_values('퇴직율', ascending=False)
    
    st.subheader("🏢 부서별 퇴직율 분석")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        bars = sns.barplot(
            x=dept_quit.index, 
            y=dept_quit['퇴직율'], 
            ax=ax1,
            palette="viridis"
        )
        
        ax1.set_title("부서별 퇴직율", fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel("퇴직율 (%)", fontsize=12)
        ax1.set_xlabel("부서", fontsize=12)
        
        # 바 위에 값 표시
        for i, bar in enumerate(bars.patches):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig1)
    
    with col2:
        st.markdown("**부서별 통계**")
        for dept, data in dept_quit.iterrows():
            st.write(f"**{dept}**: {data['퇴직율']:.1f}%")

# 2) 급여인상율과 퇴직율 관계 & 야근정도별 퇴직율 (나란히 배치)
c1, c2 = st.columns(2)

# 급여인상율과 퇴직율
if "급여증가분백분율" in df.columns and "퇴직" in df.columns:
    tmp = df[["급여증가분백분율", "퇴직"]].dropna().copy()
    tmp["인상률(%)"] = tmp["급여증가분백분율"].round().astype(int)
    sal_quit = tmp.groupby("인상률(%)")["퇴직"].mean() * 100
    
    with c1:
        st.subheader("💰 급여인상율 vs 퇴직율")
        
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        line = sns.lineplot(
            x=sal_quit.index, 
            y=sal_quit.values, 
            marker="o", 
            ax=ax2,
            linewidth=3,
            markersize=8,
            color='#ff6b6b'
        )
        
        ax2.set_title("급여인상율에 따른 퇴직율 변화", fontweight='bold', pad=15)
        ax2.set_xlabel("급여인상율 (%)", fontsize=11)
        ax2.set_ylabel("퇴직율 (%)", fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        # 데이터 포인트에 값 표시
        for x, y in zip(sal_quit.index, sal_quit.values):
            ax2.annotate(f'{y:.1f}%', (x, y), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig2)

# 야근정도별 퇴직율
if "야근정도" in df.columns and "퇴직" in df.columns:
    overtime_quit = df.groupby("야근정도")["퇴직"].mean() * 100
    
    with c2:
        st.subheader("⏰ 야근정도별 퇴직율")
        
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        bars = sns.barplot(
            x=overtime_quit.index, 
            y=overtime_quit.values, 
            ax=ax3,
            palette="Set2"
        )
        
        ax3.set_title("야근 여부에 따른 퇴직율", fontweight='bold', pad=15)
        ax3.set_ylabel("퇴직율 (%)", fontsize=11)
        ax3.set_xlabel("야근 정도", fontsize=11)
        
        # 바 위에 값 표시
        for i, bar in enumerate(bars.patches):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig3)

# 추가 분석 섹션
st.markdown("---")
st.markdown('<h2 class="sub-header">🔍 추가 인사이트</h2>', unsafe_allow_html=True)

# 상관관계 분석 (숫자형 변수가 있는 경우)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if len(numeric_cols) > 1 and "퇴직" in numeric_cols:
    corr_matrix = df[numeric_cols].corr()
    
    fig4, ax4 = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    sns.heatmap(
        corr_matrix, 
        mask=mask,
        annot=True, 
        cmap='RdBu_r',
        center=0,
        square=True,
        ax=ax4,
        cbar_kws={"shrink": 0.8}
    )
    
    ax4.set_title("변수 간 상관관계 분석", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    st.pyplot(fig4)

# 데이터 요약 정보
with st.expander("📋 데이터 요약 정보"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**데이터 기본 정보**")
        st.write(f"- 총 레코드 수: {len(df):,}개")
        st.write(f"- 총 컬럼 수: {len(df.columns)}개")
        st.write(f"- 결측값: {df.isnull().sum().sum()}개")
    
    with col2:
        st.write("**컬럼 목록**")
        for col in df.columns:
            st.write(f"- {col}")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    📊 HR Analytics Dashboard | 데이터 기반 인사관리 의사결정 지원
    </div>
    """, 
    unsafe_allow_html=True
)