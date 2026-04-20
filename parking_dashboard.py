import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SU Parking Survey Dashboard",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background-color: #f7f8fc; }

.metric-card {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 4px solid;
    margin-bottom: 4px;
}
.metric-card.orange { border-color: #f97316; }
.metric-card.blue   { border-color: #3b82f6; }
.metric-card.red    { border-color: #ef4444; }
.metric-card.green  { border-color: #22c55e; }

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.1;
}
.metric-label {
    font-size: 0.82rem;
    color: #6b7280;
    margin-top: 4px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e3a5f;
    padding: 8px 0 4px 0;
    border-bottom: 2px solid #e5e7eb;
    margin-bottom: 16px;
}

.insight-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 0.9rem;
    color: #1e3a5f;
}

.tag {
    display: inline-block;
    background: #e0e7ff;
    color: #3730a3;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 2px;
    font-family: 'DM Mono', monospace;
}

.stSelectbox label, .stMultiSelect label { font-weight: 600; color: #374151; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df_raw = pd.read_csv("parking_csv.csv", encoding="latin1", skiprows=[1, 2, 3])
    df = df_raw.dropna(subset=["Q1"])
    df = df[~df["Q1"].astype(str).str.startswith("{")].reset_index(drop=True)
    for q in ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Q10","Q14","Q15","Q16","Q17","Q18","Q19"]:
        if q in df.columns:
            df[q] = pd.to_numeric(df[q], errors="coerce")
    return df

df = load_data()

# ── Label Maps ───────────────────────────────────────────────────────────────
MAPS = {
    "Q1":  {1:"Freshman", 2:"Sophomore", 3:"Junior", 4:"Senior", 5:"Graduate/Other"},
    "Q2":  {1:"Yes", 2:"No", 3:"Sometimes"},
    "Q3":  {1:"Never", 2:"Rarely", 3:"Sometimes", 4:"Often", 5:"Always/Daily"},
    "Q4":  {1:"On-street", 2:"University lot/garage", 3:"Off-campus lot", 4:"Varies"},
    "Q5":  {1:"< 5 min", 2:"5–15 min", 3:"15–30 min", 4:"30–45 min", 5:"> 45 min"},
    "Q6":  {1:"Never", 2:"Rarely", 3:"Sometimes", 4:"Often", 5:"Always"},
    "Q7":  {1:"None", 2:"Low", 3:"Moderate", 4:"High", 5:"Extreme"},
    "Q8":  {1:"Yes", 2:"Sometimes", 3:"No"},
    "Q9":  {1:"Yes", 2:"No"},
    "Q10": {1:"Never", 2:"Rarely", 3:"Sometimes", 4:"Often", 5:"Always"},
    "Q11_opts": {
        "1": "Convenience", "2": "Schedule mismatch",
        "3": "Heavy loads/equipment", "4": "Weather",
        "5": "Unreliable shuttle", "6": "Other"
    },
    "Q14": {1:"< $25", 2:"$25–$50", 3:"$50–$100", 4:"$100–$150", 5:"> $150"},
    "Q15": {1:"Yes", 2:"No"},
    "Q16": {1:"Live availability map", 2:"Reserve in advance", 3:"Price comparison", 4:"Alert when spot opens"},
    "Q17": {3:"Fair", 4:"Poor", 5:"Very Poor"},
    "Q18": {1:"More parking structures", 2:"Shuttle improvements", 3:"Reserved smart spots",
            4:"Real-time app", 5:"Reduced permit cost", 6:"Other"},
    "Q19": {1:"Very likely", 2:"Somewhat likely", 3:"Unlikely"},
}

COLORS = {
    "primary":   "#1e3a5f",
    "accent":    "#3b82f6",
    "orange":    "#f97316",
    "green":     "#22c55e",
    "red":       "#ef4444",
    "muted":     "#94a3b8",
    "palette":   ["#1e3a5f","#3b82f6","#60a5fa","#93c5fd","#bfdbfe","#dbeafe"],
    "diverging": ["#ef4444","#f97316","#facc15","#86efac","#22c55e"],
}

def apply_map(series, q):
    return series.map(MAPS[q])

def bar_chart(counts, title, color_seq=None, orientation="h"):
    if color_seq is None:
        color_seq = COLORS["palette"]
    colors = [color_seq[i % len(color_seq)] for i in range(len(counts))]
    if orientation == "h":
        fig = go.Figure(go.Bar(
            x=counts.values, y=counts.index,
            orientation="h",
            marker_color=colors,
            text=[f"{v} ({v/counts.sum()*100:.0f}%)" for v in counts.values],
            textposition="outside",
            textfont=dict(size=13, color="#ffffff", family="DM Sans"),
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=13, color="#ffffff"), x=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(autorange="reversed", tickfont=dict(color="#e2e8f0", size=12)),
            margin=dict(l=10, r=80, t=40, b=10),
            plot_bgcolor="#1e293b", paper_bgcolor="#1e293b",
            height=max(220, len(counts)*52 + 60),
            showlegend=False,
        )
    else:
        fig = go.Figure(go.Bar(
            x=counts.index, y=counts.values,
            marker_color=colors,
            text=[f"{v}\n({v/counts.sum()*100:.0f}%)" for v in counts.values],
            textposition="outside",
            textfont=dict(size=12, color="#ffffff", family="DM Sans"),
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=13, color="#ffffff"), x=0),
            yaxis=dict(showgrid=True, gridcolor="#334155", zeroline=False,
                       tickfont=dict(color="#e2e8f0")),
            xaxis=dict(showgrid=False, tickfont=dict(color="#e2e8f0")),
            margin=dict(l=10, r=20, t=40, b=10),
            plot_bgcolor="#1e293b", paper_bgcolor="#1e293b",
            height=300, showlegend=False,
        )
    return fig

def donut_chart(counts, title):
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values,
        hole=0.52,
        marker=dict(colors=COLORS["palette"][:len(counts)],
                    line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, color="#ffffff"),
        insidetextorientation="radial",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#ffffff"), x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="#1e293b", paper_bgcolor="#1e293b",
        height=300, showlegend=False,
    )
    return fig

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🅿️ SU Parking Survey")
    st.markdown(f"**{len(df)} valid responses**")
    st.markdown("---")

    st.markdown("### 🔍 Filter Responses")
    year_opts = ["All"] + list(MAPS["Q1"].values())
    sel_year = st.selectbox("Year at SU", year_opts)

    car_opts = ["All"] + list(MAPS["Q2"].values())
    sel_car = st.selectbox("Car Access", car_opts)

    st.markdown("---")
    st.markdown("### 📌 Navigate")
    page = st.radio("Section", [
        "📊 Overview",
        "🚗 Parking Behavior",
        "😤 Pain Points",
        "💡 Solutions & Demand",
        "💬 Open Responses",
    ])

# ── Apply Filters ─────────────────────────────────────────────────────────────
dff = df.copy()
if sel_year != "All":
    yr_code = {v:k for k,v in MAPS["Q1"].items()}[sel_year]
    dff = dff[dff["Q1"] == yr_code]
if sel_car != "All":
    car_code = {v:k for k,v in MAPS["Q2"].items()}[sel_car]
    dff = dff[dff["Q2"] == car_code]

n = len(dff)

# ── Helper: filtered counts ───────────────────────────────────────────────────
def vc(q, m):
    return apply_map(dff[q].dropna(), q).value_counts().reindex(list(m.values())).dropna()

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Overview
# ═══════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("# 📊 Overview")
    st.markdown(f"Showing **{n}** responses · Filter: Year={sel_year}, Car={sel_car}")
    st.markdown("---")

    # KPI cards
    pct_car     = (dff["Q2"] == 1).sum() / n * 100 if n else 0
    pct_late    = dff["Q6"].isin([3,4,5]).sum() / n * 100 if n else 0
    pct_app     = (dff["Q15"] == 1).sum() / n * 100 if n else 0
    avg_rating  = dff["Q17"].mean() if n else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card orange">
            <div class="metric-value">{pct_car:.0f}%</div>
            <div class="metric-label">Have car access</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card red">
            <div class="metric-value">{pct_late:.0f}%</div>
            <div class="metric-label">Late to class (parking)</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card blue">
            <div class="metric-value">{pct_app:.0f}%</div>
            <div class="metric-label">Want real-time app</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card green">
            <div class="metric-value">{avg_rating:.1f}/5</div>
            <div class="metric-label">Avg parking rating (5=worst)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        counts = vc("Q1", MAPS["Q1"])
        st.plotly_chart(bar_chart(counts, "Respondents by Year"), use_container_width=True)
    with col2:
        counts = vc("Q2", MAPS["Q2"])
        st.plotly_chart(donut_chart(counts, "Has Regular Car Access on Campus"), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        counts = vc("Q17", MAPS["Q17"])
        st.plotly_chart(bar_chart(counts, "Overall Parking Rating (1=Excellent, 5=Very Poor)",
                                  color_seq=COLORS["diverging"]), use_container_width=True)
    with col4:
        counts = vc("Q7", MAPS["Q7"])
        st.plotly_chart(bar_chart(counts, "Parking Stress Level",
                                  color_seq=COLORS["diverging"]), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Parking Behavior
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🚗 Parking Behavior":
    st.markdown("# 🚗 Parking Behavior")
    st.markdown(f"Showing **{n}** responses")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        counts = vc("Q3", MAPS["Q3"])
        st.plotly_chart(bar_chart(counts, "Drive Frequency to Campus"), use_container_width=True)
    with col2:
        counts = vc("Q4", MAPS["Q4"])
        st.plotly_chart(bar_chart(counts, "Usual Parking Location"), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        counts = vc("Q5", MAPS["Q5"])
        st.plotly_chart(bar_chart(counts, "Avg Time to Find Parking"), use_container_width=True)
    with col4:
        counts = vc("Q10", MAPS["Q10"])
        st.plotly_chart(bar_chart(counts, "Shuttle/Trolley Use Instead of Driving"), use_container_width=True)

    # Q11 multi-select
    st.markdown('<div class="section-header">Why Drive Instead of Taking Shuttle?</div>', unsafe_allow_html=True)
    q11_data = dff["Q11"].dropna()
    reason_counts = {}
    for val in q11_data:
        for code in str(val).split(","):
            code = code.strip()
            label = MAPS["Q11_opts"].get(code, f"Option {code}")
            reason_counts[label] = reason_counts.get(label, 0) + 1
    if reason_counts:
        rc_series = pd.Series(reason_counts).sort_values(ascending=True)
        fig = bar_chart(rc_series, "Reasons for Driving Over Shuttle (multi-select)")
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Pain Points
# ═══════════════════════════════════════════════════════════════════════════
elif page == "😤 Pain Points":
    st.markdown("# 😤 Pain Points")
    st.markdown(f"Showing **{n}** responses")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        counts = vc("Q6", MAPS["Q6"])
        st.plotly_chart(bar_chart(counts, "How Often Late to Class Due to Parking",
                                  color_seq=COLORS["diverging"]), use_container_width=True)
    with col2:
        counts = vc("Q7", MAPS["Q7"])
        st.plotly_chart(bar_chart(counts, "Parking Stress Level",
                                  color_seq=COLORS["diverging"]), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        counts = vc("Q8", MAPS["Q8"])
        st.plotly_chart(donut_chart(counts, "Ever Skipped Class Due to Parking"), use_container_width=True)
    with col4:
        counts = vc("Q9", MAPS["Q9"])
        st.plotly_chart(donut_chart(counts, "Ever Left Class Early to Avoid Ticket"), use_container_width=True)

    # Heatmap: Late to Class vs Time to Find Parking
    st.markdown('<div class="section-header">Late to Class Frequency vs. Time to Find Parking</div>', unsafe_allow_html=True)

    cross2 = dff[["Q5","Q6"]].dropna()
    cross2["Parking Time"] = cross2["Q5"].map(MAPS["Q5"])
    cross2["Late Frequency"] = cross2["Q6"].map(MAPS["Q6"])

    time_order = ["< 5 min","5–15 min","15–30 min","30–45 min","> 45 min"]
    late_order = ["Never","Rarely","Sometimes","Often","Always"]

    ct2 = pd.crosstab(cross2["Late Frequency"], cross2["Parking Time"])
    ct2 = ct2.reindex(index=[r for r in late_order if r in ct2.index],
                      columns=[c for c in time_order if c in ct2.columns]).fillna(0)

    fig = go.Figure(go.Heatmap(
        z=ct2.values,
        x=ct2.columns.tolist(),
        y=ct2.index.tolist(),
        colorscale=[[0,"#1e293b"],[0.25,"#1d4ed8"],[0.6,"#f97316"],[1.0,"#ef4444"]],
        text=ct2.values.astype(int),
        texttemplate="%{text}",
        textfont=dict(size=14, color="white"),
        showscale=True,
        colorbar=dict(
            tickfont=dict(color="#e2e8f0"),
            title=dict(text="# respondents", font=dict(color="#e2e8f0")),
        ),
    ))
    fig.update_layout(
        height=340,
        plot_bgcolor="#1e293b", paper_bgcolor="#1e293b",
        xaxis=dict(title="Time to Find Parking",
                   tickfont=dict(color="#e2e8f0"),
                   title_font=dict(color="#e2e8f0")),
        yaxis=dict(title="Late to Class Frequency",
                   tickfont=dict(color="#e2e8f0"),
                   title_font=dict(color="#e2e8f0")),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""<div class="insight-box">
        📌 颜色越深（红/橙）代表该组合人数越多。右上角聚集说明<strong>找车时间越长，迟到越频繁</strong>。
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Solutions & Demand
# ═══════════════════════════════════════════════════════════════════════════
elif page == "💡 Solutions & Demand":
    st.markdown("# 💡 Solutions & Demand")
    st.markdown(f"Showing **{n}** responses")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        counts = vc("Q15", MAPS["Q15"])
        st.plotly_chart(donut_chart(counts, "Would Use Real-Time Parking App?"), use_container_width=True)
    with col2:
        counts = vc("Q19", MAPS["Q19"])
        st.plotly_chart(bar_chart(counts, "Likelihood to Use App/Reserved System",
                                  color_seq=["#22c55e","#86efac","#fca5a5"]), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        counts = vc("Q16", MAPS["Q16"])
        st.plotly_chart(bar_chart(counts, "Most Useful App Feature"), use_container_width=True)
    with col4:
        counts = vc("Q18", MAPS["Q18"])
        st.plotly_chart(bar_chart(counts, "Preferred Solution to Improve Parking"), use_container_width=True)

    st.markdown('<div class="section-header">Willingness to Pay / Month for Guaranteed Spot</div>', unsafe_allow_html=True)
    counts = vc("Q14", MAPS["Q14"])
    fig = bar_chart(counts, "", orientation="v",
                    color_seq=["#bfdbfe","#93c5fd","#3b82f6","#1d4ed8","#1e3a5f"])
    st.plotly_chart(fig, use_container_width=True)

    # Insight box
    pct_pay_50plus = dff["Q14"].isin([3,4,5]).sum() / n * 100 if n else 0
    st.markdown(f"""<div class="insight-box">
        💡 <strong>{pct_pay_50plus:.0f}%</strong> of respondents are willing to pay <strong>$50+/month</strong>
        for a guaranteed spot near campus — indicating strong demand for a premium parking product.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Open Responses
# ═══════════════════════════════════════════════════════════════════════════
elif page == "💬 Open Responses":
    st.markdown("# 💬 Open Responses")
    st.markdown("---")

    for q, label in [("Q20", "Additional Comments / Concerns"), ("Q21", "What Should University Know?")]:
        st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
        texts = dff[q].dropna()
        texts = texts[~texts.str.lower().isin(["no","na","nope!","none","n/a","nothing","nope","no."])]
        if len(texts) == 0:
            st.info("No responses (after filtering non-answers).")
        else:
            for i, txt in enumerate(texts, 1):
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:12px 16px;
                    margin:6px 0;box-shadow:0 1px 4px rgba(0,0,0,0.07);font-size:0.9rem;color:#374151;">
                    <span class="tag">#{i}</span> {txt}
                </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)