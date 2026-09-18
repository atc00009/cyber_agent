import sqlite3
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer

# --- CONFIG / PROFILE ---
CANDIDATE_NAME = "Vighnesh Gopal"
CURRENT_DATE = "2026-09-18"  # Simulated current anchor matching prompt context

st.set_page_config(
    page_title=f"{CANDIDATE_NAME} — 24h Cyber Agent (SOC/IR/GRC)",
    layout="wide",
)


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

# Vighnesh Gopal's Profile Text
candidate_profile = (
    "SOC Analyst Microsoft Sentinel Defender XDR KQL MITRE ATT&CK ISO 27001"
    " GDPR CCNA CEH AZ-900 phishing incident response threat hunting GRC"
    " compliance audit"
)


@st.cache_resource
def load_ai():
  return SentenceTransformer("all-MiniLM-L6-v2")


model = load_ai()
user_emb = model.encode(candidate_profile)


# --- 2. MULTI-REGION & 24H VACANCIES FEED ---
def get_daily_feed():
  return [
      {
          "id": "daily-01",
          "date": "2026-09-18",
          "region": "Middle East (KSA)",
          "domain": "SOC",
          "company": "CyberGuard KSA",
          "title": "SOC Analyst L2 (Sentinel)",
          "url": "https://example.com/daily01",
          "contact_email": "soc-careers@cyberguard.ksa",
          "visa_sponsored": True,
          "desc": (
              "Microsoft Sentinel KQL MITRE ATT&CK 24/7 SIEM monitoring tier"
              " 2 triage"
          ),
      },
      {
          "id": "daily-02",
          "date": "2026-09-18",
          "region": "Middle East (UAE)",
          "domain": "IR",
          "company": "Dubai Cyber Ops",
          "title": "Incident Response Analyst",
          "url": "https://example.com/daily02",
          "contact_email": "jobs@dubaicyber.ae",
          "visa_sponsored": False,
          "desc": (
              "Defender XDR incident investigation phishing email analysis"
              " SOC forensics"
          ),
      },
      {
          "id": "daily-03",
          "date": "2026-09-18",
          "region": "UK",
          "domain": "GRC",
          "company": "BT Security",
          "title": "Cyber GRC Analyst",
          "url": "https://example.com/daily03",
          "contact_email": "recruitment@btsecurity.co.uk",
          "visa_sponsored": True,
          "desc": (
              "ISO 27001 GDPR compliance risk assessment audit governance UK"
          ),
      },
      {
          "id": "daily-04",
          "date": "2026-09-18",
          "region": "DACH (Netherlands)",
          "domain": "SOC",
          "company": "Adyen NL",
          "title": "Security Operations Engineer",
          "url": "https://example.com/daily04",
          "contact_email": "careers@adyen.nl",
          "visa_sponsored": True,
          "desc": (
              "SIEM KQL cloud security incident response NIS2 GDPR Amsterdam"
          ),
      },
      {
          "id": "daily-05",
          "date": "2026-09-18",
          "region": "DACH (Germany)",
          "domain": "IR",
          "company": "SAP SE",
          "title": "Cyber Incident Responder",
          "url": "https://example.com/daily05",
          "contact_email": "talents@sap.de",
          "visa_sponsored": False,
          "desc": (
              "Microsoft Defender XDR malware analysis Linux Windows IR"
              " Walldorf"
          ),
      },
      {
          "id": "daily-06",
          "date": "2026-09-18",
          "region": "Australia",
          "domain": "GRC",
          "company": "CyberCX AU",
          "title": "GRC & Security Consultant",
          "url": "https://example.com/daily06",
          "contact_email": "hr@cybercx.com.au",
          "visa_sponsored": False,
          "desc": "IRAP ISO 27001 governance risk compliance audit Sydney",
      },
      {
          "id": "old-01",
          "date": "2026-09-10",
          "region": "UK",
          "domain": "SOC",
          "company": "Legacy Corp",
          "title": "Old SOC Role",
          "url": "https://example.com/old01",
          "contact_email": "hr@legacy.co.uk",
          "visa_sponsored": True,
          "desc": "Sentinel SOC triage",
      },
  ]


def sync_daily():
  conn = sqlite3.connect("cyber_jobs_daily.db")
  c = conn.cursor()
  roles = get_daily_feed()
  for r in roles:
    text = f"{r['title']} {r['desc']}"
    job_emb = model.encode(text)
    sim = float(
        np.dot(user_emb, job_emb)
        / (np.linalg.norm(user_emb) * np.linalg.norm(job_emb))
    )
    score = round(sim * 100, 2)
    heavy_gaps = [
        s
        for s in ["terraform", "kubernetes", "aws", "irap"]
        if s in text.lower() and s not in candidate_profile.lower()
    ]
    c.execute(
        """
        INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            r["id"],
            r["date"],
            r["region"],
            r["domain"],
            r["company"],
            r["title"],
            r["url"],
            r["contact_email"],
            r["visa_sponsored"],
            score,
            ", ".join(heavy_gaps) or "None",
        ),
    )
  conn.commit()
  conn.close()


sync_daily()

# --- 3. DASHBOARD UI & CONDITION GATE ---
st.title(f"🛡️ {CANDIDATE_NAME} — 24-Hour Cyber Job Agent")
st.markdown(
    "Focus Domains: **SOC, IR, GRC** | Scope: **Middle East, UK, DACH,"
    " Australia**"
)

# Sidebar Condition Rules
st.sidebar.header("⚙️ Application Conditions Gate")
only_24h = st.sidebar.checkbox(
    "Strictly Last 24 Hours Only", value=True, help="Filters posts matching current sync/date window"
)
user_needs_visa = st.sidebar.checkbox(
    "Do you require Visa Sponsorship?", value=True
)
min_score = st.sidebar.slider("Minimum Match Score (%)", 0, 100, 45)
selected_domains = st.sidebar.multiselect(
    "Target Domains", ["SOC", "IR", "GRC"], default=["SOC", "IR", "GRC"]
)
region_filter = st.selectbox(
    "Filter Region", ["All", "Middle East", "UK", "DACH", "Australia"]
)

conn = sqlite3.connect("cyber_jobs_daily.db")
df = pd.read_sql("SELECT * FROM jobs ORDER BY score DESC", conn)
conn.close()

# Apply filters
if only_24h:
  df = df[df["date"] == CURRENT_DATE]
if region_filter != "All":
  df = df[df["region"].str.contains(region_filter.split(" ")[0], case=False)]
df = df[df["domain"].isin(selected_domains)]

st.markdown("---")
st.subheader(f"Filtered Feed Results ({len(df)} roles found)")

for idx, row in df.iterrows():
  score_ok = row["score"] >= min_score
  visa_ok = (not user_needs_visa) or row["visa_sponsored"]
  all_conditions_met = score_ok and visa_ok

  col1, col2, col3 = st.columns([3, 2, 2])
  with col1:
    st.subheader(f"[{row['company']}]({row['url']}) — {row['title']}")
    st.caption(
        f"📅 Date: `{row['date']}` | 🌍 **{row['region']}** | 📁 Domain:"
        f" **{row['domain']}** | 🎯 Match: **{row['score']}%**"
    )
    st.caption(
        f"🛂 Visa Sponsored:"
        f" **{'Yes ✅' if row['visa_sponsored'] else 'No ❌'}** | ⚠️ Lacking"
        f" Gaps: `{row['missing_skills']}`"
    )
    st.code(f"HR Contact: {row['contact_email']}", language="text")

  with col2:
    if all_conditions_met:
      st.success("✅ ALL CONDITIONS MATCH")
      st.markdown(f"- Score $\\ge$ {min_score}% met")
      st.markdown("- Visa rule satisfied")
    else:
      st.error("❌ CONDITION MISMATCH")
      if not score_ok:
        st.markdown(f"- Score below {min_score}% threshold")
      if not visa_ok:
        st.markdown("- Visa sponsorship required, but role offers None")

  with col3:
    safe_title = row["title"].replace(" ", "%20")
    mailto_url = f"mailto:{row['contact_email']}?subject=Application%20for%20{safe_title}&body=Hi%20Team,%0D%0AI%20am%20applying%20for%20the%20{safe_title}%20role.%20Match%20score:%20{row['score']}%25."
    if all_conditions_met:
      st.markdown(
          f'<a href="{mailto_url}" style="display:inline-block;padding:0.6rem'
          ' 1rem;background-color:#00AA55;color:white;text-decoration:none;border-radius:4px;font-weight:bold;">📧'
          " Apply via Email</a>",
          unsafe_allow_html=True,
      )
    else:
      st.markdown(
          '<button disabled style="padding:0.6rem'
          " 1rem;background-color:#444;color:#aaa;border:none;border-radius:4px;cursor:not-allowed;'>🔒"
          " Apply Locked (Conditions Unmet)</button>",
          unsafe_allow_html=True,
      )
  st.markdown("---")
