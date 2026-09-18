import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer

# --- CONFIG / PROFILE ---
CANDIDATE_NAME = "Vighnesh Gopal"
CURRENT_DATE = "2026-09-18"

st.set_page_config(
    page_title=f"{CANDIDATE_NAME} — 24h Cyber Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- GLOBAL STYLES (Fonts only, no layout HTML hacks) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
code, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
""", unsafe_allow_html=True)


# --- 1. LOCAL DB SETUP ---
def init_db():
    conn = sqlite3.connect("cyber_jobs_daily.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        date TEXT,
        region TEXT,
        domain TEXT,
        company TEXT,
        title TEXT,
        url TEXT,
        contact_email TEXT,
        visa_sponsored BOOLEAN,
        score REAL,
        missing_skills TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

candidate_profile = (
    "SOC Analyst Microsoft Sentinel Defender XDR KQL MITRE ATT&CK ISO 27001 "
    "GDPR CCNA CEH AZ-900 phishing incident response threat hunting GRC compliance audit"
)

@st.cache_resource
def load_ai():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_ai()
user_emb = model.encode(candidate_profile)


# --- 2. MULTI-REGION & 24H VACANCIES FEED ---
def get_daily_feed():
    return [
        {"id": "daily-01", "date": "2026-09-18", "region": "Middle East (KSA)", "domain": "SOC", "company": "CyberGuard KSA", "title": "SOC Analyst L2 (Sentinel)", "url": "https://example.com/daily01", "contact_email": "soc-careers@cyberguard.ksa", "visa_sponsored": True, "desc": "Microsoft Sentinel KQL MITRE ATT&CK 24/7 SIEM monitoring tier 2 triage"},
        {"id": "daily-02", "date": "2026-09-18", "region": "Middle East (UAE)", "domain": "IR", "company": "Dubai Cyber Ops", "title": "Incident Response Analyst", "url": "https://example.com/daily02", "contact_email": "jobs@dubaicyber.ae", "visa_sponsored": False, "desc": "Defender XDR incident investigation phishing email analysis SOC forensics"},
        {"id": "daily-03", "date": "2026-09-18", "region": "UK", "domain": "GRC", "company": "BT Security", "title": "Cyber GRC Analyst", "url": "https://example.com/daily03", "contact_email": "recruitment@btsecurity.co.uk", "visa_sponsored": True, "desc": "ISO 27001 GDPR compliance risk assessment audit governance UK"},
        {"id": "daily-04", "date": "2026-09-18", "region": "DACH (Netherlands)", "domain": "SOC", "company": "Adyen NL", "title": "Security Operations Engineer", "url": "https://example.com/daily04", "contact_email": "careers@adyen.nl", "visa_sponsored": True, "desc": "SIEM KQL cloud security incident response NIS2 GDPR Amsterdam"},
        {"id": "daily-05", "date": "2026-09-18", "region": "DACH (Germany)", "domain": "IR", "company": "SAP SE", "title": "Cyber Incident Responder", "url": "https://example.com/daily05", "contact_email": "talents@sap.de", "visa_sponsored": False, "desc": "Microsoft Defender XDR malware analysis Linux Windows IR Walldorf"},
        {"id": "daily-06", "date": "2026-09-18", "region": "Australia", "domain": "GRC", "company": "CyberCX AU", "title": "GRC & Security Consultant", "url": "https://example.com/daily06", "contact_email": "hr@cybercx.com.au", "visa_sponsored": False, "desc": "IRAP ISO 27001 governance risk compliance audit Sydney"},
        {"id": "old-01", "date": "2026-09-10", "region": "UK", "domain": "SOC", "company": "Legacy Corp", "title": "Old SOC Role", "url": "https://example.com/old01", "contact_email": "hr@legacy.co.uk", "visa_sponsored": True, "desc": "Sentinel SOC triage"}
    ]

def sync_daily():
    conn = sqlite3.connect("cyber_jobs_daily.db")
    c = conn.cursor()
    roles = get_daily_feed()
    for r in roles:
        text = f"{r['title']} {r['desc']}"
        job_emb = model.encode(text)
        sim = float(np.dot(user_emb, job_emb) / (np.linalg.norm(user_emb) * np.linalg.norm(job_emb)))
        score = round(sim * 100, 2)
        heavy_gaps = [s for s in ["terraform", "kubernetes", "aws", "irap"] if s in text.lower() and s not in candidate_profile.lower()]
        c.execute("""
        INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (r['id'], r['date'], r['region'], r['domain'], r['company'], r['title'], r['url'], r['contact_email'], r['visa_sponsored'], score, ", ".join(heavy_gaps) or "None"))
    conn.commit()
    conn.close()

sync_daily()


# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### ⚙️ Evaluation Rules")
    only_24h = st.checkbox("Strictly 24h Window", value=True)
    user_needs_visa = st.checkbox("Require Visa Sponsorship", value=True)
    min_score = st.slider("Min Match Score (%)", 0, 100, 40)  # Default lowered to 40%
    selected_domains = st.multiselect("Domains", ["SOC", "IR", "GRC"], default=["SOC", "IR", "GRC"])
    region_filter = st.selectbox("Region Filter", ["All", "Middle East", "UK", "DACH", "Australia"])
    
    st.markdown("---")
    st.markdown(f"**Target Profile:**\n`{CANDIDATE_NAME}`")


# --- 4. LOAD & FILTER DATA ---
conn = sqlite3.connect("cyber_jobs_daily.db")
df = pd.read_sql("SELECT * FROM jobs ORDER BY score DESC", conn)
conn.close()

if only_24h:
    df = df[df["date"] == CURRENT_DATE]
if region_filter != "All":
    df = df[df["region"].str.contains(region_filter.split(" ")[0], case=False)]
df = df[df["domain"].isin(selected_domains)]


# --- 5. TOP HEADER & METRIC SUMMARY ---
st.title(f"🛡️ {CANDIDATE_NAME} — Cyber Operations Feed")
st.caption("Multi-region telemetry scan across Middle East, UK, DACH & Australia")

total_visible = len(df)
eligible_count = sum((row["score"] >= min_score) and ((not user_needs_visa) or row["visa_sponsored"]) for _, row in df.iterrows())
locked_count = total_visible - eligible_count

m1, m2, m3 = st.columns(3)
m1.metric("Scanned Roles (Filtered)", total_visible)
m2.metric("Eligible Ready to Apply", eligible_count)
m3.metric("Condition Locked / Mismatch", locked_count)

st.markdown("---")


# --- 6. NATIVE STREAMLIT CARD FEED ---
if df.empty:
    st.info("No roles match the selected filter parameters.")

for idx, row in df.iterrows():
    score_ok = row["score"] >= min_score
    visa_ok = (not user_needs_visa) or row["visa_sponsored"]
    all_ok = score_ok and visa_ok
    
    badge = "✅ **ALL CONDITIONS MET**" if all_ok else "🔒 **LOCKED (MISMATCH)**"
    visa_label = "Yes ✅" if row["visa_sponsored"] else "No ❌"
    
    safe_title = row["title"].replace(" ", "%20")
    mailto_url = f"mailto:{row['contact_email']}?subject=Application%20for%20{safe_title}&body=Hi%20Team,%0D%0AI%20am%20applying%20for%20the%20{safe_title}%20role.%20Match%20score:%20{row['score']}%25."

    with st.container(border=True):
        col_main, col_action = st.columns([3, 1.3])
        
        with col_main:
            st.markdown(f"### [{row['company']}]({row['url']}) — {row['title']}  {badge}")
            st.markdown(f"🌍 **Region:** {row['region']} &nbsp;|&nbsp; 📁 **Domain:** {row['domain']} &nbsp;|&nbsp; 📅 **Date:** {row['date']} &nbsp;|&nbsp; 🛂 **Visa:** {visa_label}")
            st.markdown(f"🎯 **Semantic Match:** `{row['score']}%` &nbsp;|&nbsp; ⚠️ **Lacking Gaps:** `{row['missing_skills']}`")
            
        with col_action:
            st.code(row['contact_email'], language=None)
            if all_ok:
                st.markdown(
                    f'<a href="{mailto_url}" style="display:block;text-align:center;padding:0.5rem 1rem;background-color:#0284C7;color:white;text-decoration:none;border-radius:6px;font-weight:600;">📧 Apply via Email</a>',
                    unsafe_allow_html=True
                )
            else:
                st.button("🔒 Locked", disabled=True, key=f"lock_{row['id']}", use_container_width=True)
