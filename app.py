import streamlit as st
import requests
from datetime import datetime
import pytz

# ── Config ────────────────────────────────────────────────────────────────────
HAVDALAH_MIN = 50
CANDLE_MIN = 18

st.set_page_config(
    page_title="Shabbat Times",
    page_icon="✡️",
    layout="centered",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
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


# ── Helpers ───────────────────────────────────────────────────────────────────
def is_zip(query: str) -> bool:
    """Return True if the query looks like a US zip code."""
    return query.strip().isdigit() and len(query.strip()) == 5


@st.cache_data(ttl=3600)
def fetch_by_zip(zip_code: str):
    """Fetch Shabbat data using a US zip code."""
    params = {
        "cfg": "json",
        "zip": zip_code,
        "m": HAVDALAH_MIN,
        "b": CANDLE_MIN,
        "M": "on",
    }
    resp = requests.get("https://www.hebcal.com/shabbat", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=3600)
def fetch_by_city(city: str):
    """
    Resolve city name → geoname ID via GeoNames, then fetch from Hebcal.
    Falls back to Hebcal's own city search if GeoNames fails.
    """
    # Step 1: resolve to lat/lng via a free geocoding API
    geo_resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "format": "json", "limit": 1},
        headers={"User-Agent": "shabbat-times-app"},
        timeout=10,
    )
    geo_resp.raise_for_status()
    results = geo_resp.json()
    if not results:
        raise ValueError(f"Could not find location: '{city}'")

    place = results[0]
    lat = place["lat"]
    lng = place["lon"]
    display_name = place.get("display_name", city)
    # Shorten display name to city + country
    parts = display_name.split(",")
    short_name = ", ".join(p.strip() for p in parts[:2])

    # Step 2: fetch from Hebcal using lat/lng
    params = {
        "cfg": "json",
        "latitude": lat,
        "longitude": lng,
        "tzid": "auto",
        "m": HAVDALAH_MIN,
        "b": CANDLE_MIN,
        "M": "on",
    }
    resp = requests.get("https://www.hebcal.com/shabbat", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    data["_resolved_name"] = short_name  # stash for display
    return data


def parse_shabbat(data: dict):
    """Pull out parsha + candle/havdalah times."""
    result = {
        "parsha": None,
        "hebrew": None,
        "shabbat_date": None,
        "candles": None,
        "havdalah": None,
        "torah_link": None,
        "timezone": data.get("location", {}).get("tzid", "UTC"),
        "city": data.get("_resolved_name") or data.get("location", {}).get("city", ""),
    }
    for item in data.get("items", []):
        cat = item.get("category", "")
        if cat == "parashat":
            result["parsha"] = (
                item.get("title", "")
                .replace("Parashat ", "")
                .replace("Parshah ", "")
            )
            result["hebrew"] = item.get("hebrew", "")
            result["torah_link"] = item.get("link", "")
            d = item.get("date", "")
            if d:
                result["shabbat_date"] = datetime.fromisoformat(d[:10]).strftime("%B %-d, %Y")
        elif cat == "candles":
            dt_str = item.get("date", "")
            if dt_str:
                try:
                    tz = pytz.timezone(result["timezone"])
                    dt = datetime.fromisoformat(dt_str).astimezone(tz)
                except Exception:
                    dt = datetime.fromisoformat(dt_str[:16])
                result["candles"] = dt.strftime("%-I:%M %p")
        elif cat == "havdalah":
            dt_str = item.get("date", "")
            if dt_str:
                try:
                    tz = pytz.timezone(result["timezone"])
                    dt = datetime.fromisoformat(dt_str).astimezone(tz)
                except Exception:
                    dt = datetime.fromisoformat(dt_str[:16])
                result["havdalah"] = dt.strftime("%-I:%M %p")
    return result


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1.5rem 0 0.5rem 0;">
    <div style="font-family:'DM Serif Display',serif; font-size:1.6rem; color:#1a1a1a;">✡️ Shabbat Times</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    location_input = st.text_input(
        "Location",
        placeholder="Enter a city (e.g. Chicago) or zip code (e.g. 10001)",
        label_visibility="collapsed",
    )
with col2:
    search = st.button("Search", use_container_width=True)

if location_input and (search or True):  # auto-search on input change
    query = location_input.strip()
    try:
        if is_zip(query):
            raw = fetch_by_zip(query)
            # For zip, Hebcal returns city in location block
            loc = raw.get("location", {})
            city_label = f"{loc.get('city', query)}, {loc.get('state', '')}"
        else:
            raw = fetch_by_city(query)
            city_label = raw.get("_resolved_name", query)

        info = parse_shabbat(raw)
        if not city_label:
            city_label = info["city"] or query

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
                f'<a href="{link}" target="_blank" style="font-size:0.82rem;color:#888;'
                f'text-decoration:none;border-bottom:1px solid #ccc;padding-bottom:1px;">'
                f'Read on Sefaria ↗</a></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="times-header">Shabbat Times</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="times-grid">
            <div class="time-card">
                <div class="label">Candle Lighting</div>
                <div class="value">{candles}</div>
                <div class="note">{CANDLE_MIN} min before sunset</div>
            </div>
            <div class="time-card">
                <div class="label">Havdalah</div>
                <div class="value">{havdalah}</div>
                <div class="note">{HAVDALAH_MIN} min after sunset</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="city-badge"><span>📍 {city_label}</span></div>', unsafe_allow_html=True)

    except ValueError as ve:
        st.markdown(f'<div class="error-box">⚠️ {ve}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f'<div class="error-box">⚠️ Could not load Shabbat data. Check your connection.<br><small>{e}</small></div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; color:#bbb; padding: 3rem 0; font-size:0.9rem;">
        Enter a city or zip code above to get started
    </div>
    """, unsafe_allow_html=True)
