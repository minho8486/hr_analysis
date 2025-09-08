import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings("ignore")
import os

st.set_page_config(page_title="퇴직율 대시보드", layout="wide")
sns.set(style="whitegrid", palette="Set2")

# 폰트 설정
font_dir = "./font"
font_path = os.path.join(font_dir, "NotoSansKR-Regular.ttf")
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams["font.family"] = fontprop.get_name()
plt.rcParams["axes.unicode_minus"] = False

# 데이터 로드
@st.cache_data
def load_df(path="HR Data.csv"):
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except:
        return pd.DataFrame()
    df["퇴직"] = df["퇴직여부"].map({"Yes":1, "No":0}).astype("int8")
    df.drop(['직원수', '18세이상'], axis=1, inplace=True)
    return df

df = load_df()
if df.empty:
    st.error("데이터가 없습니다. 'HR Data.csv' 파일을 확인하세요.")
    st.stop()

# ===== KPI =====
st.title("📊 퇴직율 분석 및 인사이트")
n, quit_n = len(df), int(df["퇴직"].sum())
quit_rate = df["퇴직"].mean()*100
stay_rate = 100 - quit_rate

k1, k2, k3, k4 = st.columns(4)
k1.metric("전체 직원 수", f"{n:,}명")
k2.metric("퇴직자 수", f"{quit_n:,}명")
k3.metric("유지율", f"{stay_rate:.1f}%", delta_color="normal")
k4.metric("퇴직율", f"{quit_rate:.1f}%", delta_color="inverse")

# ===== 부서별 퇴직율 =====
if "부서" in df.columns:
    dept = (df.groupby("부서")["퇴직"].mean().sort_values(ascending=False)*100)
    st.subheader("🏢 부서별 퇴직율")
    fig1, ax1 = plt.subplots(figsize=(8,4))
    sns.barplot(x=dept.index, y=dept.values, ax=ax1, palette="coolwarm")
    ax1.set_xlabel("부서", fontproperties=fontprop)
    ax1.set_ylabel("퇴직율(%)", fontproperties=fontprop)
    ax1.bar_label(ax1.containers[0], fmt="%.1f", fontsize=10)
    plt.xticks(rotation=20)
    st.pyplot(fig1)

# ===== 급여인상률 & 야근별 퇴직율 =====
c1, c2 = st.columns(2)

# 급여인상률
if "급여증가분백분율" in df.columns:
    tmp = df[["급여증가분백분율","퇴직"]].dropna().copy()
    tmp["인상률(%)"] = tmp["급여증가분백분율"].round().astype(int)
    sal = tmp.groupby("인상률(%)")["퇴직"].mean()*100
    with c1:
        st.subheader("💰 급여인상율과 퇴직율")
        fig2, ax2 = plt.subplots(figsize=(7,3.5))
        sns.lineplot(x=sal.index, y=sal.values, marker="o", ax=ax2, color="#FF6B6B")
        for x, y in zip(sal.index, sal.values):
            ax2.text(x, y+0.5, f"{y:.1f}", ha='center', fontsize=9)
        ax2.set_xlabel("급여인상율(%)", fontproperties=fontprop)
        ax2.set_ylabel("퇴직율(%)", fontproperties=fontprop)
        ax2.set_ylim(0, max(sal.values)+10)
        st.pyplot(fig2)

# 야근 여부
col_name = "야근정도"
if col_name in df.columns:
    ot = (df.groupby(col_name)["퇴직"].mean()*100)
#    ot.index = ot.index.map({"No":"없음","Yes":"있음"}).astype(str)
    with c2:
        st.subheader("⏰ 야근정도별 퇴직율")
        fig3, ax3 = plt.subplots(figsize=(7,3.5))
        sns.barplot(x=ot.index, y=ot.values, ax=ax3, palette="viridis")
        ax3.set_xlabel("야근 여부", fontproperties=fontprop)
        ax3.set_ylabel("퇴직율(%)", fontproperties=fontprop)
        ax3.bar_label(ax3.containers[0], fmt="%.1f", fontsize=10)
        st.pyplot(fig3)
