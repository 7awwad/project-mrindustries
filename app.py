import streamlit as st
import base64
import os
from engine import VastraEngine
from recommender import AuraRecommender

# ── Page config — must be the very first Streamlit command ───────────────────
st.set_page_config(
    page_title="Aura Vision | Premium Boutique",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state defaults ────────────────────────────────────────────────────
for key, val in {
    "view":        "lookbook",
    "dark_mode":   False,
    "community":   "Muslim",
    "fit_out":     None,
    "fit_info":    {},
    "classifier":  None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Load ML models once ───────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initialising Aura Vision engines…")
def load_core():
    return VastraEngine(), AuraRecommender()

engine, recommender = load_core()

# ─────────────────────────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"
GOLD   = "#C9A84C"
CREAM  = "#F9F7F4"
WHITE  = "#FFFFFF"

if st.session_state["dark_mode"]:
    BG      = "#0A0A0A"
    SURFACE = "#161616"
    TEXT    = "#F0EDE8"
    MUTED   = "#888888"
    BORDER  = "rgba(201,168,76,0.15)"
else:
    BG      = CREAM
    SURFACE = WHITE
    TEXT    = NAVY
    MUTED   = "#666666"
    BORDER  = "rgba(13,27,42,0.10)"

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Cormorant+Garamond:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & Base ─────────────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

.stApp {{
    background-color: {BG};
    color: {TEXT};
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}}

/* Hide Streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 0 2rem 4rem; max-width: 1400px; margin: auto; }}

/* ── Typography ───────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5 {{
    font-family: 'Playfair Display', serif !important;
    color: {TEXT} !important;
    letter-spacing: 0.01em;
}}

/* ── Top bar ──────────────────────────────────────────────────────────────── */
.topbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 0 12px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 0;
}}
.topbar-links {{
    display: flex;
    gap: 28px;
    font-size: 0.72rem;
    letter-spacing: 2px;
    color: {MUTED};
    text-transform: uppercase;
}}
.topbar-cta {{
    border: 1px solid {GOLD};
    color: {GOLD};
    padding: 7px 18px;
    border-radius: 2px;
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-decoration: none;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    transition: all 0.25s;
}}
.topbar-cta:hover {{ background: {GOLD}; color: {WHITE}; }}

/* ── Hero wordmark ────────────────────────────────────────────────────────── */
.wordmark-wrap {{
    text-align: center;
    padding: 40px 0 12px;
    position: relative;
}}
.wordmark-rule {{
    width: 60px; height: 1px; background: {GOLD};
    display: inline-block; vertical-align: middle; margin: 0 16px;
}}
.wordmark-tagline {{
    font-size: 0.7rem;
    letter-spacing: 6px;
    color: {GOLD};
    text-transform: uppercase;
    font-family: 'Inter', sans-serif;
    margin-top: 4px;
}}

/* ── Navigation pills ─────────────────────────────────────────────────────── */
.nav-strip {{
    display: flex;
    justify-content: center;
    gap: 0;
    border-top: 1px solid {BORDER};
    border-bottom: 1px solid {BORDER};
    margin: 24px 0;
}}
.nav-pill {{
    padding: 12px 28px;
    font-size: 0.68rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    cursor: pointer;
    border: none;
    background: transparent;
    color: {MUTED};
    font-family: 'Inter', sans-serif;
    transition: all 0.2s;
    position: relative;
}}
.nav-pill.active {{
    color: {TEXT};
    font-weight: 600;
}}
.nav-pill.active::after {{
    content: '';
    position: absolute;
    bottom: -1px; left: 0; right: 0;
    height: 2px;
    background: {GOLD};
}}
.nav-pill:hover {{ color: {GOLD}; }}

/* ── Section label ────────────────────────────────────────────────────────── */
.section-label {{
    font-size: 0.65rem;
    letter-spacing: 4px;
    color: {GOLD};
    text-transform: uppercase;
    font-family: 'Inter', sans-serif;
    margin-bottom: 6px;
}}
.section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    color: {TEXT};
    margin-bottom: 24px;
}}

/* ── Product card ─────────────────────────────────────────────────────────── */
.product-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 3px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    margin-bottom: 24px;
    position: relative;
}}
.product-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.12);
    border-color: {GOLD};
}}
.product-badge {{
    position: absolute;
    top: 12px; right: 12px;
    background: {GOLD};
    color: {WHITE};
    font-size: 0.6rem;
    letter-spacing: 2px;
    padding: 4px 10px;
    border-radius: 2px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    text-transform: uppercase;
}}
.product-body {{ padding: 14px 16px 16px; }}
.product-cat  {{
    font-size: 0.62rem;
    letter-spacing: 2.5px;
    color: {GOLD};
    text-transform: uppercase;
    font-family: 'Inter', sans-serif;
    margin-bottom: 4px;
}}
.product-name {{
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: {TEXT};
    line-height: 1.3;
    margin-bottom: 10px;
}}
.product-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}}
.product-price {{
    font-size: 1rem;
    font-weight: 600;
    color: {TEXT};
    font-family: 'Cormorant Garamond', serif;
    letter-spacing: 0.5px;
}}
.product-rating {{
    font-size: 0.75rem;
    color: {GOLD};
}}

/* ── Recommendation card ──────────────────────────────────────────────────── */
.rec-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 3px;
    padding: 16px;
    margin-bottom: 12px;
    border-left: 3px solid {GOLD};
    transition: transform 0.2s;
}}
.rec-card:hover {{ transform: translateX(4px); }}
.rec-reason {{
    font-size: 0.78rem;
    color: {MUTED};
    font-style: italic;
    margin-top: 4px;
}}

/* ── Fitting suite ────────────────────────────────────────────────────────── */
.fit-panel {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 3px;
    padding: 28px;
}}
.fit-result-frame {{
    border: 1px solid {BORDER};
    border-radius: 3px;
    overflow: hidden;
    background: {BG};
}}
.measurement-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 16px;
}}
.measurement-item {{
    background: {BG};
    border: 1px solid {BORDER};
    border-radius: 3px;
    padding: 14px 16px;
    text-align: center;
}}
.measurement-value {{
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: {GOLD};
    font-weight: 600;
}}
.measurement-label {{
    font-size: 0.65rem;
    letter-spacing: 2px;
    color: {MUTED};
    text-transform: uppercase;
    margin-top: 2px;
}}
.size-badge {{
    display: inline-block;
    border: 2px solid {GOLD};
    color: {GOLD};
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    padding: 8px 24px;
    border-radius: 3px;
    margin: 16px 0;
    font-weight: 700;
}}

/* ── Classifier card ──────────────────────────────────────────────────────── */
.classifier-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 3px;
    padding: 24px;
    text-align: center;
}}
.class-result {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: {GOLD};
    margin: 8px 0;
}}
.confidence-bar-wrap {{
    background: {BG};
    border-radius: 2px;
    height: 6px;
    margin: 4px 0 2px;
    overflow: hidden;
}}
.confidence-bar {{
    height: 6px;
    background: linear-gradient(90deg, {GOLD}, #e8c96a);
    border-radius: 2px;
}}

/* ── Divider ──────────────────────────────────────────────────────────────── */
.gold-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {GOLD}, transparent);
    margin: 32px 0;
    border: none;
}}

/* ── Streamlit widget overrides ───────────────────────────────────────────── */
.stButton > button {{
    background: transparent !important;
    color: {TEXT} !important;
    border: 1px solid {TEXT} !important;
    border-radius: 2px !important;
    font-size: 0.72rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    font-weight: 500 !important;
}}
.stButton > button:hover {{
    background: {GOLD} !important;
    border-color: {GOLD} !important;
    color: {WHITE} !important;
}}
.stSelectbox label, .stSlider label, .stNumberInput label,
.stFileUploader label, .stTextInput label {{
    font-size: 0.68rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
    font-family: 'Inter', sans-serif !important;
}}
.stSelectbox > div > div {{
    background: {SURFACE} !important;
    border-color: {BORDER} !important;
    color: {TEXT} !important;
    border-radius: 2px !important;
}}
.stDownloadButton > button {{
    background: {GOLD} !important;
    color: {WHITE} !important;
    border-color: {GOLD} !important;
}}
.stDownloadButton > button:hover {{
    background: #b8943e !important;
    border-color: #b8943e !important;
}}
div[data-testid="stMetricValue"] {{
    font-family: 'Playfair Display', serif !important;
    color: {GOLD} !important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _img_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _star_rating(rating: float) -> str:
    full  = int(rating)
    empty = 5 - full
    return "★" * full + "☆" * empty


# ─────────────────────────────────────────────────────────────────────────────
# TOP BAR + WORDMARK
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-links">
        <span>Collections</span>
        <span>Sellers</span>
        <span>About</span>
    </div>
    <a href="#" class="topbar-cta">Sign Up · Join the Club</a>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="wordmark-wrap">
    <span class="wordmark-rule"></span>
    <span style="font-family:'Playfair Display',serif; font-size:2.8rem; font-weight:700; color:{TEXT}; letter-spacing:6px;">
        AURA VISION
    </span>
    <span class="wordmark-rule"></span>
    <div class="wordmark-tagline">AI-Powered Couture · Multi-Community Fashion</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Community + Settings
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<p style='font-size:0.65rem;letter-spacing:3px;color:{MUTED};text-transform:uppercase;'>Settings</p>", unsafe_allow_html=True)
    st.session_state["dark_mode"] = st.toggle("🌙 Dark Mode", value=st.session_state["dark_mode"])
    st.markdown("---")
    st.markdown(f"<p style='font-size:0.65rem;letter-spacing:3px;color:{MUTED};text-transform:uppercase;'>Your Community</p>", unsafe_allow_html=True)
    communities = ["Muslim", "Hindu", "Sikh", "Christian", "Buddhist"]
    comm = st.selectbox("", communities, index=communities.index(st.session_state["community"]), label_visibility="collapsed")
    st.session_state["community"] = comm

comm = st.session_state["community"]

# ─────────────────────────────────────────────────────────────────────────────
# NAV TABS
# ─────────────────────────────────────────────────────────────────────────────
views = {
    "lookbook":    "✦ Lookbook",
    "recommend":   "◈ For You",
    "tryon":       "◎ Fitting Suite",
    "classifier":  "✧ Garment AI",
}
cols_nav = st.columns(len(views))
for i, (view_key, view_label) in enumerate(views.items()):
    with cols_nav[i]:
        active_cls = "active" if st.session_state["view"] == view_key else ""
        if st.button(view_label, key=f"nav_{view_key}"):
            st.session_state["view"] = view_key
            st.rerun()

st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# VIEW 1 — LOOKBOOK
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state["view"] == "lookbook":
    st.markdown(f"""
    <div class="section-label">Curated for you</div>
    <div class="section-title">The {comm} Collection</div>
    """, unsafe_allow_html=True)

    items = recommender.get_curated_collection(comm, max_items=6)

    if not items:
        st.info("No products found for this community.")
    else:
        cols = st.columns(3)
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                img_path = f"images/{item['product_id']}.jpg"
                if os.path.exists(img_path):
                    img_src = f"data:image/jpeg;base64,{_img_b64(img_path)}"
                else:
                    placeholder_txt = item['name'].replace(' ', '+').replace(',', '')
                    img_src = f"https://placehold.co/400x520/{NAVY[1:]}/{CREAM[1:]}/png?text={placeholder_txt}"

                badge_html = '<div class="product-badge">Top Rated</div>' if item["rating"] >= 4.7 else ""

                st.markdown(f"""
                <div class="product-card">
                    {badge_html}
                    <img src="{img_src}" style="width:100%;height:360px;object-fit:cover;display:block;">
                    <div class="product-body">
                        <div class="product-cat">{item['category']}</div>
                        <div class="product-name">{item['name']}</div>
                        <div class="product-footer">
                            <div class="product-price">₹{item['price']:,}</div>
                            <div class="product-rating">{_star_rating(item['rating'])} {item['rating']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("✦ Virtual Try-On", key=f"tryon_{item['product_id']}"):
                    st.session_state["view"] = "tryon"
                    st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# VIEW 2 — PERSONALISED RECOMMENDATIONS (Task 3)
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state["view"] == "recommend":
    st.markdown(f"""
    <div class="section-label">Task 3 · Recommendation Engine</div>
    <div class="section-title">Curated For You</div>
    """, unsafe_allow_html=True)

    with st.expander("⚙  Refine Your Preferences", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            pref_cats = st.multiselect(
                "Preferred Categories",
                ["Top", "Bottom", "Full Body", "Accessory"],
                default=["Full Body", "Accessory"],
            )
        with c2:
            price_range = st.slider("Price Range (₹)", 200, 8000, (500, 4000), step=100)
        past_raw = st.text_input(
            "Past Purchase Tags  (comma-separated)",
            placeholder="e.g. eid, silk, embroidery",
        )

    past_tags = [t.strip() for t in past_raw.split(",") if t.strip()] if past_raw else []

    user_profile = {
        "community":           comm,
        "preferred_categories": pref_cats,
        "price_range":         price_range,
        "past_purchases":      past_tags,
    }

    recs = recommender.get_recommendations(user_profile, top_n=10)

    if not recs:
        st.warning("No matches found. Try widening your price range or adding more tags.")
    else:
        st.markdown(f"<p style='color:{MUTED};font-size:0.8rem;margin-bottom:16px;'>{len(recs)} recommendations found for the <strong>{comm}</strong> community.</p>", unsafe_allow_html=True)
        for rec in recs:
            st.markdown(f"""
            <div class="rec-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <div class="product-cat">{rec['category']}</div>
                        <div class="product-name" style="font-size:1.05rem;">{rec['name']}</div>
                        <div class="rec-reason">✦ {rec['explanation']}</div>
                    </div>
                    <div style="text-align:right;flex-shrink:0;margin-left:16px;">
                        <div class="product-price">₹{rec['price']:,}</div>
                        <div class="product-rating" style="font-size:0.8rem;">{_star_rating(rec['rating'])} {rec['rating']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# VIEW 3 — FITTING SUITE (Tasks 1 + 2)
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state["view"] == "tryon":
    st.markdown(f"""
    <div class="section-label">Task 1 + 2 · Virtual Try-On & Measurements</div>
    <div class="section-title">The Fitting Suite</div>
    """, unsafe_allow_html=True)

    L, R = st.columns([1, 1.25], gap="large")

    with L:
        st.markdown(f'<div class="fit-panel">', unsafe_allow_html=True)
        st.markdown(f"<p class='section-label'>Fitting Parameters</p>", unsafe_allow_html=True)

        h_cm  = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        p_up  = st.file_uploader("Upload Person Photo", type=["jpg", "jpeg", "png"])
        g_up  = st.file_uploader("Upload Garment Image", type=["jpg", "jpeg", "png"])

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("✦ Process AI Fitting", use_container_width=True)

        if run:
            if p_up and g_up:
                with st.spinner("Removing backgrounds · Detecting pose · Overlaying garment…"):
                    res, info = engine.execute_tryon(p_up.read(), g_up.read(), h_cm)
                if res:
                    st.session_state["fit_out"]  = res
                    st.session_state["fit_info"] = info
                    st.success("✔ Fitting complete — see results on the right.")
                else:
                    err = info.get("error", "Unknown error.")
                    st.error(f"Fitting failed: {err}")
            else:
                st.warning("Please upload both a person photo and a garment image.")

        st.markdown("</div>", unsafe_allow_html=True)

    with R:
        if st.session_state["fit_out"]:
            st.image(st.session_state["fit_out"], use_column_width=True)
            st.download_button("⬇ Download Result", st.session_state["fit_out"], "aura_vision_tryon.png", "image/png")

            info = st.session_state.get("fit_info", {})
            meas = info.get("measurements", {})

            if meas and "error" not in meas:
                st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
                st.markdown("<p class='section-label'>Body Measurements</p>", unsafe_allow_html=True)

                st.markdown(f"""
                <div class="measurement-grid">
                    <div class="measurement-item">
                        <div class="measurement-value">{meas.get('shoulder_width','—')}</div>
                        <div class="measurement-label">Shoulder Width</div>
                    </div>
                    <div class="measurement-item">
                        <div class="measurement-value">{meas.get('hip_width','—')}</div>
                        <div class="measurement-label">Hip Width</div>
                    </div>
                    <div class="measurement-item">
                        <div class="measurement-value">{meas.get('torso_length','—')}</div>
                        <div class="measurement-label">Torso Length</div>
                    </div>
                    <div class="measurement-item">
                        <div class="measurement-value" style="font-size:2rem;">{meas.get('recommended_size','—')}</div>
                        <div class="measurement-label">Recommended Size</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Show garment class from Task 4 if available
            gc = info.get("garment_class", {})
            if gc and "class" in gc:
                st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
                st.markdown("<p class='section-label'>Garment Detected As</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="classifier-card">
                    <div class="class-result">{gc['class']}</div>
                    <div style="color:{MUTED};font-size:0.75rem;margin-bottom:8px;">Confidence: {gc.get('confidence',0):.1f}%</div>
                    <div class="confidence-bar-wrap">
                        <div class="confidence-bar" style="width:{gc.get('confidence',0)}%;"></div>
                    </div>
                    <div style="font-size:0.65rem;color:{MUTED};margin-top:8px;">{gc.get('model','')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="height:480px;border:1px dashed {BORDER};border-radius:3px;
                        display:flex;flex-direction:column;align-items:center;justify-content:center;
                        color:{MUTED};text-align:center;gap:12px;">
                <div style="font-size:3rem;opacity:0.3;">◎</div>
                <div style="font-size:0.75rem;letter-spacing:2px;text-transform:uppercase;">
                    Upload photos and click<br>Process AI Fitting
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# VIEW 4 — GARMENT CLASSIFIER (Task 4 Bonus — standalone)
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state["view"] == "classifier":
    st.markdown(f"""
    <div class="section-label">Task 4 (Bonus) · Garment Classifier</div>
    <div class="section-title">Garment Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown(f"<p style='color:{MUTED};font-size:0.85rem;max-width:560px;line-height:1.7;'>Upload any garment image. Aura Vision will classify it using CLIP zero-shot inference into one of five categories: <em>Top, Bottom, Full Length, Headwear</em> or <em>Accessory</em>.</p><br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1:
        g_file = st.file_uploader("Upload Garment Image", type=["jpg", "jpeg", "png"])
        if st.button("✦ Classify Garment", use_container_width=True) and g_file:
            with st.spinner("Analysing garment…"):
                result = engine.classify_garment(g_file.read())
            st.session_state["classifier"] = result

        if g_file:
            st.image(g_file, use_column_width=True)

    with c2:
        result = st.session_state.get("classifier")
        if result:
            st.markdown("<p class='section-label'>Classification Result</p>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="classifier-card">
                <div style="font-size:0.7rem;letter-spacing:3px;color:{MUTED};text-transform:uppercase;margin-bottom:4px;">Detected Category</div>
                <div class="class-result">{result.get('class','—')}</div>
                <div style="color:{MUTED};font-size:0.8rem;margin-bottom:10px;">Confidence: {result.get('confidence',0):.1f}%</div>
                <div class="confidence-bar-wrap" style="height:8px;margin-bottom:16px;">
                    <div class="confidence-bar" style="width:{result.get('confidence',0)}%;height:8px;"></div>
                </div>
                <div style="font-size:0.65rem;color:{MUTED};">{result.get('model','')}</div>
            </div>
            """, unsafe_allow_html=True)

            all_scores = result.get("all_scores")
            if all_scores:
                st.markdown("<p class='section-label' style='margin-top:20px;'>All Scores</p>", unsafe_allow_html=True)
                for label, score in sorted(all_scores.items(), key=lambda x: -x[1]):
                    st.markdown(f"""
                    <div style="margin-bottom:8px;">
                        <div style="display:flex;justify-content:space-between;font-size:0.78rem;
                                    color:{TEXT if score == max(all_scores.values()) else MUTED};margin-bottom:3px;">
                            <span>{label}</span><span>{score:.1f}%</span>
                        </div>
                        <div class="confidence-bar-wrap">
                            <div class="confidence-bar" style="width:{score}%;opacity:{1.0 if score == max(all_scores.values()) else 0.4};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="height:360px;border:1px dashed {BORDER};border-radius:3px;
                        display:flex;flex-direction:column;align-items:center;justify-content:center;
                        color:{MUTED};text-align:center;gap:12px;">
                <div style="font-size:3rem;opacity:0.3;">✧</div>
                <div style="font-size:0.75rem;letter-spacing:2px;text-transform:uppercase;">
                    Upload a garment to<br>see classification
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="border-top:1px solid {BORDER};margin-top:60px;padding:28px 0;
            text-align:center;color:{MUTED};font-size:0.68rem;letter-spacing:2px;">
    AURA VISION  ·  AI-POWERED COUTURE  ·  MULTI-COMMUNITY FASHION PLATFORM
</div>
""", unsafe_allow_html=True)