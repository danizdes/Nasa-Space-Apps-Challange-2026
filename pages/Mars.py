## TEST CODE FOR MARS GLOBE PREVIEW ##

## Same pattern as pages/Globe Test.py — martian textures + Mars site seeds

# Import Streamlit
import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mars Test", page_icon="🔴", layout="wide")

st.title("🔴 Interactive Mars Globe")
st.caption("Drag to rotate, scroll to zoom. Pick a martian location below — the globe "
           "zooms in, then redirects to Introduction. Textures load from CDN.")

# ---------------------------------------------------------------------------
# Locations: structured data. Coordinates live here, HTML just consumes JSON.
# Dummy martian seeds — swap/preload from catalog later.
DEFAULT_LOCATIONS = [
    {"name": "Jezero Crater (Perseverance)", "lat": 18.38,  "lng": 77.58},
    {"name": "Gale Crater (Curiosity)",      "lat": -5.4,   "lng": 137.8},
    {"name": "Olympus Mons",                 "lat": 18.65,  "lng": -133.8},
    {"name": "Valles Marineris",             "lat": -14.0,  "lng": -59.0},
    {"name": "Hellas Planitia",              "lat": -42.4,  "lng": 70.5},
    {"name": "Elysium Planitia (InSight)",   "lat": 4.5,    "lng": 135.9},
    {"name": "Utopia Planitia",              "lat": 46.7,   "lng": 117.5},
    {"name": "North Polar Ice Cap",          "lat": 85.0,   "lng": 0.0},
]

if "mars_locations" not in st.session_state:
    st.session_state.mars_locations = [dict(x) for x in DEFAULT_LOCATIONS]

# ---------------------------------------------------------------------------
# Input form: add custom coordinates
with st.expander("➕ Add martian location by coordinates", expanded=False):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 0.6])
    name = c1.text_input("Name", key="mars_name", placeholder="e.g. Hellas rim site")
    lat = c2.number_input("Latitude", -90.0, 90.0, 0.0, format="%.4f", key="mars_lat")
    lng = c3.number_input("Longitude", -180.0, 180.0, 0.0, format="%.4f", key="mars_lng")
    if c4.button("Add", use_container_width=True, type="primary"):
        if name.strip():
            st.session_state.mars_locations.append(
                {"name": name.strip(), "lat": round(lat, 4), "lng": round(lng, 4)})
            st.success(f"Added **{name}** — globe updated.")
        else:
            st.error("Name required.")
    if st.button("↺ Reset to dummy seeds"):
        st.session_state.mars_locations = [dict(x) for x in DEFAULT_LOCATIONS]
        st.rerun()

# Current locations table
df = pd.DataFrame(st.session_state.mars_locations)
st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# HTML template. __LOCATIONS__ placeholder gets replaced with JSON from Python.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://unpkg.com/globe.gl@2/dist/globe.gl.min.js"></script>
<style>
  html, body { margin: 0; padding: 0; background: #0B0F1A; color: #E6EDF3;
               font-family: 'Source Sans Pro', sans-serif; overflow: hidden; }
  #wrapper { position: relative; width: 100vw; height: 620px; }
  #globe { width: 100%; height: 100%; cursor: grab; }
  #globe:active { cursor: grabbing; }
  #bottom { position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
            z-index: 10; display: flex; gap: 10px; align-items: center; }
  #bottom label { font-size: 14px; color: #8B9BB4; }
  select { background: rgba(21,28,44,.9); color: #E6EDF3; border: 1px solid #2A3A55;
           border-radius: 8px; padding: 8px 12px; font-size: 14px; min-width: 260px; }
  #status { position: absolute; top: 12px; left: 12px; z-index: 10; font-size: 14px;
            color: #FFFFFF; background: rgba(252,61,33,.92); padding: 8px 14px;
            border-radius: 8px; opacity: 0; transition: opacity .3s;
            box-shadow: 0 4px 14px rgba(0,0,0,.45); }
  #status.show { opacity: 1; }
</style>
</head>
<body>
<div id="wrapper">
  <div id="globe"></div>
  <div id="status">Zooming in…</div>
  <div id="err" style="position:absolute;top:12px;left:12px;z-index:11;font-size:13px;
       color:#FC3D21;background:rgba(21,28,44,.9);padding:8px 12px;border-radius:8px;
       display:none;max-width:60%;"></div>
  <div id="bottom">
    <label for="loc">📍 Choose martian location:</label>
    <select id="loc"><option value="">— select —</option></select>
  </div>
</div>

<script>
// Coordinates injected from Streamlit session state
const LOCATIONS = __LOCATIONS__;

const select = document.getElementById('loc');
const status = document.getElementById('status');
const errBox = document.getElementById('err');

// Populate dropdown FIRST — works even if the globe fails to load
Object.keys(LOCATIONS).forEach(name => {
  const opt = document.createElement('option');
  opt.value = name; opt.textContent = name;
  select.appendChild(opt);
});

// Globe init: separate try/catch so failures can't kill the dropdown
let globe = null;
try {
  globe = new Globe(document.getElementById('globe'), { animateIn: true })
    // Martian surface texture (CORS-enabled CDN — solarsystemscope lacks CORS headers)
    .globeImageUrl('https://cdn.jsdelivr.net/gh/jeromeetienne/threex.planets@master/images/marsmap1k.jpg')
    .bumpImageUrl('https://cdn.jsdelivr.net/gh/jeromeetienne/threex.planets@master/images/marsbump1k.jpg')
    .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
    .atmosphereColor('#E8734A')
    .atmosphereAltitude(0.18)
    // Mark every input location with a colored point + hover label
    .pointsData(Object.values(LOCATIONS).map((c, i) => ({
      ...c, color: i % 2 ? '#FC3D21' : '#3D9EFF' })))
    .pointAltitude(0.02)
    .pointRadius(0.6)
    .pointLabel(d => d.name);
  globe.pointOfView({ lat: 10, lng: 0, altitude: 2.5 }, 0);
} catch (e) {
  errBox.textContent = 'Globe failed to load: ' + e.message +
    ' — check internet/CDN access. Dropdown still works.';
  errBox.style.display = 'block';
}

// Select → two-stage cinematic zoom → redirect to Introduction
select.onchange = () => {
  const loc = LOCATIONS[select.value];
  if (!loc || !globe) return;
  status.innerHTML = '🔍 Zooming in on <b>' + select.value + '</b>…';
  status.classList.add('show');
  // Stage 1: glide toward the region; Stage 2: sink down after stage 1 ends
  globe.pointOfView({ lat: loc.lat * 0.6, lng: loc.lng * 0.5, altitude: 2.5 }, 1500);
  setTimeout(() => globe.pointOfView({ lat: loc.lat, lng: loc.lng, altitude: 0.45 }, 2500), 1400);
  setTimeout(() => {
    status.textContent = 'Redirecting…';
    // Streamlit multipage: Introduction is the main app → "/"
    window.parent.location.href = '/';
  }, 4200);
};
</script>
</body>
</html>
"""

HTML = HTML_TEMPLATE.replace("__LOCATIONS__", json.dumps(
    {loc["name"]: {"lat": loc["lat"], "lng": loc["lng"]}
     for loc in st.session_state.mars_locations},
    ensure_ascii=False,
))

components.html(HTML, height=660, scrolling=False)

st.info("**Test flow:** dropdown → two-stage zoom (~4s total) → redirects to "
        "Introduction. Coordinates live in `st.session_state.mars_locations` — "
        "HTML receives them as JSON, so the catalog can drop straight in later.")
