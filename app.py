import sqlite3
from datetime import datetime
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

# --- MODERN CYBER UI CUSTOM CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #F1F5F9;
}

code, pre, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}

.main-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 24px 28px;
    margin-bottom: 24px;
}

.job-card {
    background-color: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 14px;
    transition: border-color 0.2s ease, transform 0.1s ease;
}

.job-card:hover {
    border-color: #0284C7;
}

.badge-eligible {
    background-color: rgba(16, 185, 129, 0.12);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
}

.badge-locked {
    background-color: rgba(239, 68, 68, 0.12);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
}

.tag-chip {
    background-color: #1E293B;
    color: #94A3B8;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    margin-right: 6px;
}

.apply-btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #0284C7;
    color: #FFFFFF !important;
    text-decoration: none;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: center;
    transition: background-color 0.2s;
}

.apply-btn:hover {
    background-color: #0369A1;
}

.locked-btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #1E293B;
    color: #64748B !important;
    text-decoration: none;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    text-align: center;
    cursor: not-allowed;
    border: 1px solid #334155;
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
    min_score = st.slider("Min Match Score (%)", 0, 100, 45)
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
st.markdown(f"""
<div class="main-header">
    <h1 style="margin:0; font-size:1.75rem; font-weight:700;">🛡️ {CANDIDATE_NAME} — Cyber Operations Feed</h1>
    <p style="margin:4px 0 0 0; color:#94A3B8; font-size:0.95rem;">Multi-region telemetry scan across Middle East, UK, DACH & Australia</p>
</div>
""", unsafe_allow_html=True)

# Calculate metrics
total_visible = len(df)
eligible_count = sum((row["score"] >= min_score) and ((not user_needs_visa) or row["visa_sponsored"]) for _, row in df.iterrows())
locked_count = total_visible - eligible_count

m1, m2, m3 = st.columns(3)
m1.metric("Scanned Roles (Filtered)", total_visible)
m2.metric("Eligible Ready to Apply", eligible_count, delta="Matches Criteria" if eligible_count>0 else None)
m3.metric("Condition Locked / Mismatch", locked_count)

st.markdown("---")


# --- 6. ALIGNED CARD FEED ---
if df.empty:
    st.info("No roles match the selected filter parameters.")

for idx, row in df.iterrows():
    score_ok = row["score"] >= min_score
    visa_ok = (not user_needs_visa) or row["visa_sponsored"]
    all_ok = score_ok and visa_ok
    
    badge_html = '<span class="badge-eligible">✅ ALL CONDITIONS MET</span>' if all_ok else '<span class="badge-locked">🔒 LOCKED (MISMATCH)</span>'
    visa_label = "Yes ✅" if row["visa_sponsored"] else "No ❌"
    
    safe_title = row["title"].replace(" ", "%20")
    mailto_url = f"mailto:{row['contact_email']}?subject=Application%20for%20{safe_title}&body=Hi%20Team,%0D%0AI%20am%20applying%20for%20the%20{safe_title}%20role.%20Match%20score:%20{row['score']}%25."
    
    action_html = f'<a href="{mailto_url}" class="apply-btn">📧 Apply via Email</a>' if all_ok else '<span class="locked-btn">🔒 Apply Locked</span>'

    # Structured card container using custom aligned layout
    st.markdown(f"""
    <div class="job-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
            <div style="flex: 1; min-width: 280px;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <a href="{row['url']}" target="_blank" style="font-size:1.1rem; font-weight:700; color:#38BDF8; text-decoration:none;">{row['company']} — {row['title']}</a>
                    {badge_html}
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
                    <span class="tag-chip">🌍 {row['region']}</span>
                    <span class="tag-chip">📁 {row['domain']}</span>
                    <span class="tag-chip">📅 {row['date']}</span>
                    <span class="tag-chip">🛂 Visa: {visa_label}</span>
                </div>
                <div style="font-size:0.85rem; color:#94A3B8;">
                    <span class="mono">Semantic Match: <b>{row['score']}%</b></span> | 
                    <span>Lacking Gaps: <code class="mono">{row['missing_skills']}</code></span>
                </div>
            </div>
            
            <div style="display:flex; flex-direction:column; align-items:flex-end; justify-content:center; gap:8px;">
                <div class="mono" style="font-size:0.75rem; color:#64748B;">{row['contact_email']}</div>
                {action_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
