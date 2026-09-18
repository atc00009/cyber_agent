import streamlit as st
import sqlite3
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# --- PAGE CONFIG ---
st.set_page_config(page_title="Vighnesh Multi-Region Cyber Agent", layout="wide")

# --- 1. LOCAL DB SETUP ---
def init_db():
    conn = sqlite3.connect("cyber_jobs_global.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        region TEXT,
        company TEXT,
        title TEXT,
        url TEXT,
        score REAL,
        eligibility TEXT,
        missing_skills TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# --- 2. VIGHNESH PROFILE & AI MODEL ---
vighnesh_profile = (
    "SOC Analyst Microsoft Sentinel Defender XDR KQL MITRE ATT&CK ISO 27001 "
    "GDPR CCNA CEH AZ-900 phishing incident response threat hunting"
)

@st.cache_resource
def load_ai():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_ai()
user_emb = model.encode(vighnesh_profile)

# --- 3. MULTI-REGION ROLE FEED (Middle East, UK, DACH, Australia) ---
def get_multi_region_feed():
    return [
        {"id": "me-1", "region": "Middle East (KSA)", "company": "CyberGuard Middle East", "title": "SOC Analyst L2 (Sentinel)", "url": "https://example.com/me1", "desc": "Microsoft Sentinel KQL MITRE ATT&CK 24/7 SIEM monitoring tier 2 triage"},
        {"id": "me-2", "region": "Middle East (UAE)", "company": "Dubai Cyber Operations", "title": "Incident Response Analyst", "url": "https://example.com/me2", "desc": "Defender XDR incident investigation phishing email analysis SOC"},
        {"id": "uk-1", "region": "UK", "company": "BT Security", "title": "Cyber Security Operations Analyst", "url": "https://example.com/uk1", "desc": "Microsoft Sentinel Defender XDR incident response ISO 27001 GDPR UK"},
        {"id": "dach-1", "region": "DACH (Netherlands)", "company": "Adyen NL", "title": "Security Operations Engineer", "url": "https://example.com/dach1", "desc": "SIEM KQL cloud security incident response NIS2 GDPR Amsterdam"},
        {"id": "dach-2", "region": "DACH (Germany)", "company": "SAP SE", "title": "SOC Analyst", "url": "https://example.com/dach2", "desc": "Microsoft Defender XDR SOC monitoring Linux Windows tier 1/2 Walldorf"},
        {"id": "au-1", "region": "Australia", "company": "CyberCX AU", "title": "Security Analyst - SOC", "url": "https://example.com/au1", "desc": "IRAP awareness Microsoft Sentinel SIEM threat detection triage Sydney"}
    ]

def sync_and_score():
    conn = sqlite3.connect("cyber_jobs_global.db")
    c = conn.cursor()
    roles = get_multi_region_feed()
    for r in roles:
        text = f"{r['title']} {r['desc']}"
        job_emb = model.encode(text)
        sim = float(np.dot(user_emb, job_emb) / (np.linalg.norm(user_emb) * np.linalg.norm(job_emb)))
        score = round(sim * 100, 2)
        eligible = "ELIGIBLE ✅" if score >= 45 else "LOW MATCH ⚠️"
        heavy_gaps = [s for s in ["terraform", "kubernetes", "aws"] if s in text.lower() and s not in vighnesh_profile.lower()]
        c.execute("INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?,?)",
                  (r['id'], r['region'], r['company'], r['title'], r['url'], score, eligible, ", ".join(heavy_gaps) or "None"))
    conn.commit()
    conn.close()

sync_and_score()

# --- 4. DASHBOARD UI ---
st.title("🛡️ Vighnesh Gopal — Multi-Region Cyber Job Agent")
st.markdown("Scope: **Middle East, UK, DACH, Australia** | Matching Engine: **Local Semantic AI**")

region_filter = st.selectbox("Filter Region", ["All", "Middle East", "UK", "DACH", "Australia"])
conn = sqlite3.connect("cyber_jobs_global.db")
df = pd.read_sql("SELECT * FROM jobs ORDER BY score DESC", conn)
conn.close()

if region_filter != "All":
    df = df[df['region'].str.contains(region_filter.split(' ')[0], case=False)]

st.markdown("---")
for idx, row in df.iterrows():
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader(f"[{row['company']}] {row['title']}")
        st.caption(f"🌍 Region: **{row['region']}** | 🎯 Semantic Match: **{row['score']}%** | ⚠️ Enterprise Gaps: `{row['missing_skills']}`")
    with c2:
        st.metric("Status", row['eligibility'])
    with c3:
        if st.button("Approve & Queue", key=row['id']):
            st.toast(f"Approved application queue for {row['company']}!")
    st.markdown("---")
