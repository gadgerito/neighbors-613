import streamlit as st
import requests
from datetime import datetime, date
import pytz

# ── Config ────────────────────────────────────────────────────────────────────
# Change these to your city. Find your geo ID at https://www.hebcal.com/shabbat/
CITY_NAME = "New York"
HEBCAL_GEO_ID = "5128581"          # geonameid for New York City
TIMEZONE = "America/New_York"

st.set_page_config(
    page_title="Shabbat Times",
    page_icon="✡️",
    layout="centered",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background-color: #fafaf8; }

.hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
}
.hero-label {
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 0.4rem;
}
.hero-parsha {
    font-family: 'DM Serif Display', serif;
    font-size: 3.2rem;
    color: #1a1a1a;
    line-height: 1.1;
    margin: 0;
}
.hero-hebrew {
    font-family: 'DM Serif Display', serif;
    font-style: italic;
    font-size: 1.3rem;
    color: #555;
    margin-top: 0.3rem;
}
.hero-date {
    font-size: 0.9rem;
    color: #999;
    margin-top: 0.6rem;
}

.divider {
    border: none;
    border-top: 1px solid #e8e6e1;
    margin: 2rem 0;
}

.times-header {
    font-size: 0.78rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 1.2rem;
    text-align: center;
}

.times-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    max-width: 480px;
    margin: 0 auto;
}
.time-card {
    background: #ffffff;
    border: 1px solid #eeece8;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.time-card .label {
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #aaa;
    margin-bottom: 0.35rem;
}
.time-card .value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.55rem;
    color: #1a1a1a;
}
.time-card .note {
    font-size: 0.7rem;
    color: #bbb;
    margin-top: 0.2rem;
}

.city-badge {
    text-align: center;
    margin-top: 0.5rem;
}
.city-badge span {
    display: inline-block;
    background: #f0ede8;
    color: #666;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.25rem 0.8rem;
    border-radius: 99px;
}

.error-box {
    background: #fff5f5;
    border: 1px solid #fcc;
    border-radius: 8px;
    padding: 1rem;
    color: #c00;
    font-size: 0.88rem;
    text-align: center;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Data fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_shabbat_data(geo_id: str):
    """Fetch this week's parsha + candle/havdalah times from Hebcal."""
    url = "https://www.hebcal.com/shabbat"
    params = {
        "cfg": "json",
        "geonameid": geo_id,
        "m": 50,          # havdalah at 50 min after sunset
        "b": 18,          # candle lighting 18 min before sunset
        "M": "on",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def parse_shabbat(data: dict):
    """Pull out the fields we care about."""
    result = {
        "parsha": None,
        "hebrew": None,
        "shabbat_date": None,
        "candles": None,
        "havdalah": None,
        "torah_link": None,
    }
    for item in data.get("items", []):
        cat = item.get("category", "")
        if cat == "parashat":
            result["parsha"] = item.get("title", "").replace("Parashat ", "").replace("Parshah ", "")
            result["hebrew"] = item.get("hebrew", "")
            result["torah_link"] = item.get("link", "")
            d = item.get("date", "")
            if d:
                result["shabbat_date"] = datetime.fromisoformat(d[:10]).strftime("%B %-d, %Y")
        elif cat == "candles":
            dt_str = item.get("date", "")
            if dt_str:
                tz = pytz.timezone(TIMEZONE)
                dt = datetime.fromisoformat(dt_str).astimezone(tz)
                result["candles"] = dt.strftime("%-I:%M %p")
        elif cat == "havdalah":
            dt_str = item.get("date", "")
            if dt_str:
                tz = pytz.timezone(TIMEZONE)
                dt = datetime.fromisoformat(dt_str).astimezone(tz)
                result["havdalah"] = dt.strftime("%-I:%M %p")
    return result


# ── Render ────────────────────────────────────────────────────────────────────
try:
    raw = get_shabbat_data(HEBCAL_GEO_ID)
    info = parse_shabbat(raw)

    parsha_display = info["parsha"] or "—"
    hebrew_display = info["hebrew"] or ""
    date_display   = info["shabbat_date"] or ""
    candles        = info["candles"] or "—"
    havdalah       = info["havdalah"] or "—"
    link           = info["torah_link"] or ""

    st.markdown(f"""
    <div class="hero">
        <div class="hero-label">This week's parsha</div>
        <div class="hero-parsha">{parsha_display}</div>
        <div class="hero-hebrew">{hebrew_display}</div>
        <div class="hero-date">{date_display}</div>
    </div>
    """, unsafe_allow_html=True)

    if link:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:0.5rem">'
            f'<a href="{link}" target="_blank" style="font-size:0.82rem;color:#888;text-decoration:none;'
            f'border-bottom:1px solid #ccc;padding-bottom:1px;">Read on Sefaria ↗</a></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<div class="times-header">Shabbat Times</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="times-grid">
        <div class="time-card">
            <div class="label">Candle Lighting</div>
            <div class="value">{candles}</div>
            <div class="note">18 min before sunset</div>
        </div>
        <div class="time-card">
            <div class="label">Havdalah</div>
            <div class="value">{havdalah}</div>
            <div class="note">50 min after sunset</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="city-badge"><span>📍 {CITY_NAME}</span></div>', unsafe_allow_html=True)

except Exception as e:
    st.markdown(f'<div class="error-box">⚠️ Could not load Shabbat data. Check your internet connection.<br><small>{e}</small></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
