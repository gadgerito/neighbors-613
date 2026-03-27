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

# ── Password gate ─────────────────────────────────────────────────────────────
APP_PASSWORD = "shabbatshalom"  # change this to whatever you want

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 0 1rem 0;">
        <div style="font-family:'DM Serif Display',serif; font-size:1.6rem; color:#1a1a1a;">✡️ Shabbat Times</div>
        <div style="color:#aaa; font-size:0.85rem; margin-top:0.5rem;">Enter the password to continue</div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pw = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Password")
        if st.button("Enter", use_container_width=True):
            if pw == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    st.stop()

# ── Temporary in-memory message store (replace with MongoDB later) ─────────────
# TODO: swap this section out for MongoDB when ready.
# Each message: {"username": str, "tag": str, "text": str, "timestamp": datetime}
if "messages" not in st.session_state:
    st.session_state.messages = []
        

def save_message(username, tag, text):
    """Save a message. Replace body with MongoDB insert when ready."""
    st.session_state.messages.append({
        "username": username,
        "tag": tag,
        "text": text,
        "timestamp": datetime.now(),
    })

def get_messages():
    """Get all messages. Replace body with MongoDB find() when ready."""
    return sorted(st.session_state.messages, key=lambda m: m["timestamp"], reverse=True)

# ── Parsha lookup ─────────────────────────────────────────────────────────────
PARSHA_DATA = {
    "Bereshit":           ("https://www.chabad.org/parshah/default_cdo/aid/2112/jewish/Bereishit.htm",        "bereshit"),
    "Noach":              ("https://www.chabad.org/parshah/default_cdo/aid/2113/jewish/Noach.htm",             "noach"),
    "Lech-Lecha":         ("https://www.chabad.org/parshah/default_cdo/aid/2114/jewish/Lech-Lecha.htm",       "lech-lecha"),
    "Vayera":             ("https://www.chabad.org/parshah/default_cdo/aid/2115/jewish/Vayera.htm",            "vayera"),
    "Chayei Sara":        ("https://www.chabad.org/parshah/default_cdo/aid/2116/jewish/Chayei-Sara.htm",      "chayei-sara"),
    "Toldot":             ("https://www.chabad.org/parshah/default_cdo/aid/2117/jewish/Toldot.htm",            "toldot"),
    "Vayetzei":           ("https://www.chabad.org/parshah/default_cdo/aid/2118/jewish/Vayetzei.htm",         "vayetzei"),
    "Vayishlach":         ("https://www.chabad.org/parshah/default_cdo/aid/2119/jewish/Vayishlach.htm",       "vayishlach"),
    "Vayeshev":           ("https://www.chabad.org/parshah/default_cdo/aid/2120/jewish/Vayeshev.htm",         "vayeshev"),
    "Miketz":             ("https://www.chabad.org/parshah/default_cdo/aid/2121/jewish/Miketz.htm",            "miketz"),
    "Vayigash":           ("https://www.chabad.org/parshah/default_cdo/aid/2122/jewish/Vayigash.htm",         "vayigash"),
    "Vayechi":            ("https://www.chabad.org/parshah/default_cdo/aid/2123/jewish/Vayechi.htm",          "vayechi"),
    "Shemot":             ("https://www.chabad.org/parshah/default_cdo/aid/2124/jewish/Shemot.htm",           "shemot"),
    "Vaera":              ("https://www.chabad.org/parshah/default_cdo/aid/2125/jewish/Vaera.htm",             "vaera"),
    "Bo":                 ("https://www.chabad.org/parshah/default_cdo/aid/2126/jewish/Bo.htm",                "bo"),
    "Beshalach":          ("https://www.chabad.org/parshah/default_cdo/aid/2127/jewish/Beshalach.htm",        "beshalach"),
    "Yitro":              ("https://www.chabad.org/parshah/default_cdo/aid/2128/jewish/Yitro.htm",             "yitro"),
    "Mishpatim":          ("https://www.chabad.org/parshah/default_cdo/aid/2129/jewish/Mishpatim.htm",        "mishpatim"),
    "Terumah":            ("https://www.chabad.org/parshah/default_cdo/aid/2130/jewish/Terumah.htm",          "terumah"),
    "Tetzaveh":           ("https://www.chabad.org/parshah/default_cdo/aid/2131/jewish/Tetzaveh.htm",         "tetzaveh"),
    "Ki Tisa":            ("https://www.chabad.org/parshah/default_cdo/aid/2132/jewish/Ki-Tisa.htm",          "ki-tisa"),
    "Vayakhel":           ("https://www.chabad.org/parshah/default_cdo/aid/2133/jewish/Vayakhel.htm",         "vayakhel"),
    "Pekudei":            ("https://www.chabad.org/parshah/default_cdo/aid/2134/jewish/Pekudei.htm",          "pekudei"),
    "Vayakhel-Pekudei":   ("https://www.chabad.org/parshah/default_cdo/aid/2133/jewish/Vayakhel.htm",         "vayakhel"),
    "Vayikra":            ("https://www.chabad.org/parshah/default_cdo/aid/2135/jewish/Vayikra.htm",          "vayikra"),
    "Tzav":               ("https://www.chabad.org/parshah/default_cdo/aid/2136/jewish/Tzav.htm",              "tzav"),
    "Shmini":             ("https://www.chabad.org/parshah/default_cdo/aid/2137/jewish/Shmini.htm",           "shemini"),
    "Tazria":             ("https://www.chabad.org/parshah/default_cdo/aid/2138/jewish/Tazria.htm",           "tazria"),
    "Metzora":            ("https://www.chabad.org/parshah/default_cdo/aid/2139/jewish/Metzora.htm",          "metzora"),
    "Tazria-Metzora":     ("https://www.chabad.org/parshah/default_cdo/aid/2138/jewish/Tazria.htm",           "tazria"),
    "Achrei Mot":         ("https://www.chabad.org/parshah/default_cdo/aid/2140/jewish/Achrei-Mot.htm",       "acharei-mot"),
    "Kedoshim":           ("https://www.chabad.org/parshah/default_cdo/aid/2141/jewish/Kedoshim.htm",         "kedoshim"),
    "Achrei Mot-Kedoshim":("https://www.chabad.org/parshah/default_cdo/aid/2140/jewish/Achrei-Mot.htm",       "acharei-mot"),
    "Emor":               ("https://www.chabad.org/parshah/default_cdo/aid/2142/jewish/Emor.htm",              "emor"),
    "Behar":              ("https://www.chabad.org/parshah/default_cdo/aid/2143/jewish/Behar.htm",             "behar"),
    "Bechukotai":         ("https://www.chabad.org/parshah/default_cdo/aid/2144/jewish/Bechukotai.htm",       "bechukotai"),
    "Behar-Bechukotai":   ("https://www.chabad.org/parshah/default_cdo/aid/2143/jewish/Behar.htm",            "behar"),
    "Bamidbar":           ("https://www.chabad.org/parshah/default_cdo/aid/2145/jewish/Bamidbar.htm",         "bamidbar"),
    "Nasso":              ("https://www.chabad.org/parshah/default_cdo/aid/2146/jewish/Nasso.htm",             "naso"),
    "Beha'alotcha":       ("https://www.chabad.org/parshah/default_cdo/aid/2147/jewish/Behaalotcha.htm",      "behaalotcha"),
    "Sh'lach":            ("https://www.chabad.org/parshah/default_cdo/aid/2148/jewish/Shelach.htm",          "shelach-lecha"),
    "Korach":             ("https://www.chabad.org/parshah/default_cdo/aid/2149/jewish/Korach.htm",           "korach"),
    "Chukat":             ("https://www.chabad.org/parshah/default_cdo/aid/2150/jewish/Chukat.htm",           "chukat"),
    "Balak":              ("https://www.chabad.org/parshah/default_cdo/aid/2151/jewish/Balak.htm",             "balak"),
    "Chukat-Balak":       ("https://www.chabad.org/parshah/default_cdo/aid/2150/jewish/Chukat.htm",           "chukat"),
    "Pinchas":            ("https://www.chabad.org/parshah/default_cdo/aid/2152/jewish/Pinchas.htm",          "pinchas"),
    "Matot":              ("https://www.chabad.org/parshah/default_cdo/aid/2153/jewish/Matot.htm",             "matot"),
    "Masei":              ("https://www.chabad.org/parshah/default_cdo/aid/2154/jewish/Masei.htm",             "masei"),
    "Matot-Masei":        ("https://www.chabad.org/parshah/default_cdo/aid/2153/jewish/Matot.htm",            "matot"),
    "Devarim":            ("https://www.chabad.org/parshah/default_cdo/aid/2155/jewish/Devarim.htm",          "devarim"),
    "Vaetchanan":         ("https://www.chabad.org/parshah/default_cdo/aid/2156/jewish/Vaetchanan.htm",       "vaetchanan"),
    "Eikev":              ("https://www.chabad.org/parshah/default_cdo/aid/2157/jewish/Eikev.htm",             "eikev"),
    "Re'eh":              ("https://www.chabad.org/parshah/default_cdo/aid/2158/jewish/Reeh.htm",              "reeh"),
    "Shoftim":            ("https://www.chabad.org/parshah/default_cdo/aid/2159/jewish/Shoftim.htm",          "shoftim"),
    "Ki Teitzei":         ("https://www.chabad.org/parshah/default_cdo/aid/2160/jewish/Ki-Teitzei.htm",       "ki-teitzei"),
    "Ki Tavo":            ("https://www.chabad.org/parshah/default_cdo/aid/2161/jewish/Ki-Tavo.htm",          "ki-tavo"),
    "Nitzavim":           ("https://www.chabad.org/parshah/default_cdo/aid/2162/jewish/Nitzavim.htm",         "nitzavim"),
    "Vayeilech":          ("https://www.chabad.org/parshah/default_cdo/aid/2163/jewish/Vayeilech.htm",        "vayeilech"),
    "Nitzavim-Vayeilech": ("https://www.chabad.org/parshah/default_cdo/aid/2162/jewish/Nitzavim.htm",         "nitzavim"),
    "Ha'Azinu":           ("https://www.chabad.org/parshah/default_cdo/aid/2164/jewish/Haazinu.htm",          "haazinu"),
    "V'Zot HaBerachah":   ("https://www.chabad.org/parshah/default_cdo/aid/2165/jewish/Vezot-Haberachah.htm","vezot-habracha"),
}

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main { background-color: #fafaf8; }

.hero { text-align: center; padding: 2.5rem 0 1.5rem 0; }
.hero-label { font-size: 0.78rem; letter-spacing: 0.18em; text-transform: uppercase; color: #888; margin-bottom: 0.4rem; }
.hero-parsha { font-family: 'DM Serif Display', serif; font-size: 3.2rem; color: #1a1a1a; line-height: 1.1; margin: 0; }
.hero-hebrew { font-family: 'DM Serif Display', serif; font-style: italic; font-size: 1.3rem; color: #555; margin-top: 0.3rem; }
.hero-date { font-size: 0.9rem; color: #999; margin-top: 0.6rem; }

.divider { border: none; border-top: 1px solid #e8e6e1; margin: 2rem 0; }

.section-header { font-size: 0.78rem; letter-spacing: 0.16em; text-transform: uppercase; color: #888; margin-bottom: 1.2rem; text-align: center; }

.times-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; max-width: 480px; margin: 0 auto; }
.time-card { background: #ffffff; border: 1px solid #eeece8; border-radius: 12px; padding: 1.1rem 1.2rem; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.time-card .label { font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; color: #aaa; margin-bottom: 0.35rem; }
.time-card .value { font-family: 'DM Serif Display', serif; font-size: 1.55rem; color: #1a1a1a; }
.time-card .note { font-size: 0.7rem; color: #bbb; margin-top: 0.2rem; }

.resource-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; max-width: 480px; margin: 0 auto; }
.resource-card { background: #ffffff; border: 1px solid #eeece8; border-radius: 12px; padding: 1rem 1.1rem; text-decoration: none !important; color: #1a1a1a; box-shadow: 0 1px 4px rgba(0,0,0,0.04); display: block; }
.resource-card:hover { box-shadow: 0 3px 10px rgba(0,0,0,0.09); border-color: #d4d0c8; }
.resource-card .r-icon { font-size: 1.4rem; margin-bottom: 0.3rem; }
.resource-card .r-name { font-size: 0.82rem; font-weight: 500; color: #333; }
.resource-card .r-desc { font-size: 0.7rem; color: #aaa; margin-top: 0.15rem; }

/* Message board */
.msg-card {
    background: #ffffff; border: 1px solid #eeece8;
    border-radius: 12px; padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.msg-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; flex-wrap: wrap; }
.msg-username { font-weight: 500; font-size: 0.88rem; color: #1a1a1a; }
.msg-tag {
    font-size: 0.68rem; padding: 0.15rem 0.55rem;
    border-radius: 99px; background: #f0ede8; color: #666;
    letter-spacing: 0.04em;
}
.msg-time { font-size: 0.68rem; color: #bbb; margin-left: auto; }
.msg-text { font-size: 0.88rem; color: #444; line-height: 1.55; }

.city-badge { text-align: center; margin-top: 0.5rem; }
.city-badge span { display: inline-block; background: #f0ede8; color: #666; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.25rem 0.8rem; border-radius: 99px; }

.error-box { background: #fff5f5; border: 1px solid #fcc; border-radius: 8px; padding: 1rem; color: #c00; font-size: 0.88rem; text-align: center; }
/* Upcoming events */
.events-list { max-width: 480px; margin: 0 auto; }
.event-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid #f0ede8;
}
.event-row:last-child { border-bottom: none; }
.event-date {
    min-width: 72px; font-size: 0.75rem;
    color: #999; letter-spacing: 0.03em;
}
.event-dot {
    width: 8px; height: 8px; border-radius: 50%;
    flex-shrink: 0;
}
.event-name { font-size: 0.88rem; color: #1a1a1a; flex: 1; }
.event-hebrew { font-size: 0.75rem; color: #aaa; }
.event-candles { font-size: 0.75rem; color: #888; margin-left: auto; white-space: nowrap; }
.dot-major { background: #c0846a; }
.dot-minor { background: #a0b090; }
.dot-roshchodesh { background: #8aaec0; }
.dot-cholhamoed { background: #c0a870; }

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Data fetching ─────────────────────────────────────────────────────────────
def is_zip(query):
    return query.strip().isdigit() and len(query.strip()) == 5

@st.cache_data(ttl=3600)
def fetch_by_zip(zip_code):
    params = {"cfg": "json", "zip": zip_code, "m": HAVDALAH_MIN, "b": CANDLE_MIN, "M": "on"}
    r = requests.get("https://www.hebcal.com/shabbat", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=3600)
def fetch_by_city(city):
    geo = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "format": "json", "limit": 1},
        headers={"User-Agent": "shabbat-times-app"},
        timeout=10,
    )
    geo.raise_for_status()
    results = geo.json()
    if not results:
        raise ValueError(f"Could not find location: '{city}'")
    place = results[0]
    parts = place.get("display_name", city).split(",")
    short_name = ", ".join(p.strip() for p in parts[:2])
    params = {"cfg": "json", "latitude": place["lat"], "longitude": place["lon"],
              "tzid": "auto", "m": HAVDALAH_MIN, "b": CANDLE_MIN, "M": "on"}
    r = requests.get("https://www.hebcal.com/shabbat", params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    data["_resolved_name"] = short_name
    return data
@st.cache_data(ttl=3600)
def fetch_upcoming_events(lat, lng, tzid):
    """Fetch all Jewish holidays for the rest of the Jewish year."""
    today = datetime.now().date()
    # Jewish year ends in September/October — fetch through end of next Tishrei
    end_year = today.year + 1 if today.month >= 9 else today.year
    params = {
        "v": 1,
        "cfg": "json",
        "latitude": lat,
        "longitude": lng,
        "tzid": tzid,
        "maj": "on",       # major holidays
        "min": "on",       # minor holidays
        "mod": "on",       # modern holidays
        "roshchodesh": "on",
        "cholhamoed": "on",
        "start": today.isoformat(),
        "end": f"{end_year}-09-30",
    }
    r = requests.get("https://www.hebcal.com/hebcal", params=params, timeout=10)
    r.raise_for_status()
    return r.json()
@st.cache_data(ttl=3600)
def get_coordinates(zip_code=None, city=None):
    """Get lat/lng/tzid from Hebcal location data."""
    if zip_code:
        params = {"cfg": "json", "zip": zip_code, "m": 18, "b": 18}
        r = requests.get("https://www.hebcal.com/shabbat", params=params, timeout=10)
        r.raise_for_status()
        loc = r.json().get("location", {})
        return loc.get("latitude"), loc.get("longitude"), loc.get("tzid", "America/New_York")
    else:
        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "shabbat-times-app"},
            timeout=10,
        )
        results = geo.json()
        if not results:
            return None, None, "UTC"
        place = results[0]
        # rough tzid from nominatim (Hebcal will handle conversion)
        return float(place["lat"]), float(place["lon"]), "auto"

def parse_shabbat(data):
    result = {"parsha": None, "hebrew": None, "shabbat_date": None,
              "candles": None, "havdalah": None, "torah_link": None,
              "timezone": data.get("location", {}).get("tzid", "UTC"),
              "city": data.get("_resolved_name") or data.get("location", {}).get("city", "")}
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


# ── Session state init ────────────────────────────────────────────────────────
if "username" not in st.session_state:
    st.session_state.username = ""
if "username_set" not in st.session_state:
    st.session_state.username_set = False


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1.5rem 0 0.5rem 0;">
    <div style="font-family:'DM Serif Display',serif; font-size:1.6rem; color:#1a1a1a;">✡️ Shabbat Times</div>
</div>
""", unsafe_allow_html=True)

# ── Location input ────────────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    location_input = st.text_input("Location", placeholder="Enter a city or zip code", label_visibility="collapsed")
with col2:
    st.button("Search", use_container_width=True)

if location_input:
    query = location_input.strip()
    try:
        if is_zip(query):
            raw = fetch_by_zip(query)
            loc = raw.get("location", {})
            city_label = f"{loc.get('city', query)}, {loc.get('state', '')}"
        else:
            raw = fetch_by_city(query)
            city_label = raw.get("_resolved_name", query)

        info = parse_shabbat(raw)
        if not city_label:
            city_label = info["city"] or query

        parsha  = info["parsha"] or "—"
        hebrew  = info["hebrew"] or ""
        date_d  = info["shabbat_date"] or ""
        candles = info["candles"] or "—"
        havdala = info["havdalah"] or "—"
        link    = info["torah_link"] or ""

        # Parsha hero
        st.markdown(f"""
        <div class="hero">
            <div class="hero-label">This week's parsha</div>
            <div class="hero-parsha">{parsha}</div>
            <div class="hero-hebrew">{hebrew}</div>
            <div class="hero-date">{date_d}</div>
        </div>
        """, unsafe_allow_html=True)

        # Resources
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Learn & Explore</div>', unsafe_allow_html=True)
        pdata = PARSHA_DATA.get(parsha, (None, None))
        chabad_url  = pdata[0] or "https://www.chabad.org/parshah"
        mjl_slug    = pdata[1] or parsha.lower().replace(" ", "-")
        sefaria_url = link or f"https://www.sefaria.org/topics/parasha/{parsha.lower().replace(' ', '-')}"
        yt_url      = f"https://www.youtube.com/results?search_query={requests.utils.quote('parashat ' + parsha + ' Torah shiur')}"
        cards_html = '<div class="resource-grid">'
        for icon, name, desc, url in [
            ("📖", "Sefaria",            "Full text + commentary",  sefaria_url),
            ("🕍", "Chabad.org",         "In-depth summary",        chabad_url),
            ("📚", "My Jewish Learning", "Accessible overview",     f"https://www.myjewishlearning.com/article/{mjl_slug}-summary/"),
            ("▶️", "YouTube Shiurim",    "Video Torah talks",       yt_url),
        ]:
            cards_html += f'<a class="resource-card" href="{url}" target="_blank" rel="noopener noreferrer"><div class="r-icon">{icon}</div><div class="r-name">{name}</div><div class="r-desc">{desc}</div></a>'
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

        # Times
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Shabbat Times</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="times-grid">
            <div class="time-card">
                <div class="label">Candle Lighting</div>
                <div class="value">{candles}</div>
                <div class="note">{CANDLE_MIN} min before sunset</div>
            </div>
            <div class="time-card">
                <div class="label">Havdalah</div>
                <div class="value">{havdala}</div>
                <div class="note">{HAVDALAH_MIN} min after sunset</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="city-badge"><span>📍 {city_label}</span></div>', unsafe_allow_html=True)

    except ValueError as ve:
        st.markdown(f'<div class="error-box">⚠️ {ve}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f'<div class="error-box">⚠️ Could not load data.<br><small>{e}</small></div>', unsafe_allow_html=True)

else:
    st.markdown('<div style="text-align:center; color:#bbb; padding: 3rem 0; font-size:0.9rem;">Enter a city or zip code above to get started</div>', unsafe_allow_html=True)


# ── Message board ─────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Community Board</div>', unsafe_allow_html=True)

# Username setup
if not st.session_state.username_set:
    st.markdown('<div style="text-align:center; color:#888; font-size:0.85rem; margin-bottom:0.75rem;">Choose a display name to join the conversation</div>', unsafe_allow_html=True)
    ucol1, ucol2 = st.columns([3, 1])
    with ucol1:
        name_input = st.text_input("Username", placeholder="Your name or nickname", label_visibility="collapsed", key="name_input")
    with ucol2:
        if st.button("Join", use_container_width=True):
            if name_input.strip():
                st.session_state.username = name_input.strip()
                st.session_state.username_set = True
                st.rerun()
            else:
                st.warning("Please enter a name.")
else:
    # Logged-in composer
    st.markdown(f'<div style="font-size:0.8rem; color:#888; margin-bottom:0.6rem;">Posting as <strong style="color:#444">{st.session_state.username}</strong> · <span style="cursor:pointer; color:#bbb;">not you?</span></div>', unsafe_allow_html=True)

    tag = st.selectbox(
        "Tag",
        ["🕊️ Shabbat Shalom", "📖 Dvar Torah", "❓ Question", "💬 Discussion"],
        label_visibility="collapsed",
    )
    msg_text = st.text_area("Message", placeholder="Share a Shabbat wish, thought on the parsha, or start a discussion...", label_visibility="collapsed", height=90, key="msg_input")

    pcol1, pcol2 = st.columns([1, 4])
    with pcol1:
        if st.button("Post", use_container_width=True):
            if msg_text.strip():
                save_message(st.session_state.username, tag, msg_text.strip())
                st.rerun()
            else:
                st.warning("Message can't be empty.")
    with pcol2:
        if st.button("Switch name", use_container_width=False):
            st.session_state.username_set = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

# Display messages
messages = get_messages()
if messages:
    for msg in messages:
        ts = msg["timestamp"]
        time_str = ts.strftime("%-I:%M %p · %b %-d") if isinstance(ts, datetime) else ""
        st.markdown(f"""
        <div class="msg-card">
            <div class="msg-header">
                <span class="msg-username">{msg['username']}</span>
                <span class="msg-tag">{msg['tag']}</span>
                <span class="msg-time">{time_str}</span>
            </div>
            <div class="msg-text">{msg['text']}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align:center; color:#ccc; padding: 2rem 0; font-size:0.88rem;">No messages yet — be the first to post! 🕯️</div>', unsafe_allow_html=True)
