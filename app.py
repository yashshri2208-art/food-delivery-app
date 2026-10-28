"""
ChaiTapri Eats - Food Delivery Website (Streamlit)
===================================================
Python Programming for Business Students - End Term Project

What this app does:
  1. Finds the customer's location (GPS or a chosen area)
  2. Shows nearby restaurants with distance, rating and delivery time
  3. Lets the customer pick items from a restaurant's menu
  4. Calculates a full bill: items, coupon, delivery fee, GST, tip, total
  5. Places the order and shows a confirmation

Run with:  streamlit run app.py
"""

import math
import random

import pandas as pd
import streamlit as st

# The GPS feature needs the 'streamlit-geolocation' package.
# If it is not installed, the app still works using the "Choose an area" option.
try:
    from streamlit_geolocation import streamlit_geolocation
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False


# ---------------------------------------------------------------------------
# 1. PAGE SETUP AND STYLING
# ---------------------------------------------------------------------------
st.set_page_config(page_title="ChaiTapri Eats", page_icon="🍛", layout="wide")

# Custom CSS: gives the page its own look (colours, fonts, cards).
# Palette: ink #2B1B2E, turmeric #F2B705, chilli #D7263D, mint #2E9E83
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');
:root { --ink:#211626; --gold:#ffc928; --red:#ff5a52; --cream:#fff7e8; --mint:#48c9a5; }
html, body, [class*="css"], .stMarkdown, .stButton button, label {
    font-family:'DM Sans','Segoe UI',sans-serif;
}
h1,h2,h3,.display { font-family:'Bricolage Grotesque','Segoe UI',sans-serif !important; }
.block-container { padding-top:1.7rem; padding-bottom:3rem; animation: pageIn .55s ease both; }
@keyframes pageIn { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
@keyframes floatFood { 0%,100% { transform:translateY(0) rotate(-4deg); } 50% { transform:translateY(-12px) rotate(4deg); } }
@keyframes glow { 0%,100% { box-shadow:0 0 0 rgba(255,201,40,0); } 50% { box-shadow:0 0 36px rgba(255,201,40,.18); } }
.stApp { background:radial-gradient(ellipse at 85% 0%, rgba(255,201,40,.07), transparent 30%), #101116; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#241b2a,#191a22); border-right:1px solid rgba(255,255,255,.08); }
[data-testid="stSidebar"] h3 { color:var(--gold); }
.stButton button { border-radius:13px; min-height:2.8rem; font-weight:700; transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease; }
.stButton button:hover { transform:translateY(-2px); box-shadow:0 8px 22px rgba(0,0,0,.2); border-color:var(--gold); }
.stButton button[kind="primary"] { background:linear-gradient(135deg,#ff6458,#ed3f50); border:0; color:white; }
.hero { background:linear-gradient(120deg,#2b1b2e,#42243a 60%,#2b1b2e); border-radius:22px; padding:27px 32px; margin-bottom:22px; border-bottom:5px solid var(--gold); box-shadow:0 16px 44px rgba(0,0,0,.2); }
.hero .display { color:var(--gold); font-size:2.25rem; font-weight:800; margin:0; line-height:1.1; }
.hero p { color:#fff7e8; margin:8px 0 0; font-size:1.02rem; }
.section-title { font-family:'Bricolage Grotesque',sans-serif; font-size:1.55rem; font-weight:800; margin:18px 0 8px; }
.rest-card { border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:18px; margin-bottom:8px; background:linear-gradient(145deg,rgba(255,201,40,.09),rgba(255,255,255,.025)); min-height:130px; transition:transform .2s ease,border-color .2s ease; }
.rest-card:hover { transform:translateY(-3px); border-color:rgba(255,201,40,.55); }
.rest-card.selected { border:2px solid var(--red); background:rgba(255,90,82,.08); }
.rest-card.far { opacity:.55; }
.rest-name { font-size:1.12rem; font-weight:700; }
.muted { opacity:.72; font-size:.88rem; }
.pill { display:inline-block; padding:4px 10px; border-radius:999px; font-size:.78rem; font-weight:700; margin:7px 5px 0 0; }
.pill.rating { background:#258f78; color:white; } .pill.time { background:rgba(255,201,40,.19); color:#ffe08a; } .pill.dist { background:rgba(255,255,255,.09); } .pill.out { background:var(--red); color:white; }
.menu-name { font-weight:700; font-size:1.02rem; } .price { font-weight:700; color:var(--red); }
.bill-box { border:1px solid rgba(255,255,255,.13); border-radius:18px; padding:18px 20px; margin:8px 0 12px; background:rgba(255,255,255,.025); }
.bill-row { display:flex; justify-content:space-between; gap:16px; padding:8px 0; border-bottom:1px dashed rgba(255,255,255,.14); }
.bill-row.saving { color:var(--mint); font-weight:700; } .bill-total { display:flex; justify-content:space-between; gap:16px; padding-top:14px; font-size:1.35rem; font-weight:800; color:var(--gold); }
/* Welcome page */
[data-testid="stAppViewContainer"]:has(.landing-screen) [data-testid="stSidebar"] { display:none; }
[data-testid="stAppViewContainer"]:has(.landing-screen) [data-testid="stHeader"] { background:transparent; }
[data-testid="stAppViewContainer"]:has(.landing-screen) .block-container { max-width:1400px; padding-top:1.2rem; }
.landing-screen { position:relative; overflow:hidden; min-height:70vh; border-radius:30px; padding:clamp(28px,6vw,84px); background:radial-gradient(circle at 82% 35%,rgba(255,201,40,.22),transparent 24%),radial-gradient(circle at 72% 75%,rgba(255,90,82,.22),transparent 27%),linear-gradient(135deg,#211526 0%,#332039 48%,#17171f 100%); border:1px solid rgba(255,255,255,.12); box-shadow:0 25px 80px rgba(0,0,0,.32); animation:pageIn .8s ease both; }
.landing-screen:after { content:''; position:absolute; width:390px; height:390px; border:1px solid rgba(255,201,40,.22); border-radius:50%; right:-90px; top:12%; box-shadow:0 0 0 35px rgba(255,201,40,.035),0 0 0 75px rgba(255,201,40,.025); pointer-events:none; }
.brand-mark { display:inline-flex; align-items:center; justify-content:center; width:58px; height:58px; border-radius:19px; background:var(--gold); color:#26192a; font-size:30px; box-shadow:0 10px 30px rgba(255,201,40,.18); }
.landing-kicker { color:var(--mint); text-transform:uppercase; letter-spacing:.18em; font-size:.78rem; font-weight:800; margin-top:28px; }
.landing-title { color:#fff7e8; font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:clamp(3.2rem,8vw,6.8rem); line-height:.93; letter-spacing:-.055em; margin:16px 0 20px; max-width:800px; }
.landing-title span { color:var(--gold); }
.landing-copy { color:rgba(255,247,232,.78); font-size:clamp(1rem,2vw,1.25rem); line-height:1.7; max-width:590px; }
.food-orbit { position:absolute; right:9%; top:24%; width:210px; height:210px; border-radius:50%; display:flex; align-items:center; justify-content:center; background:linear-gradient(145deg,rgba(255,201,40,.2),rgba(255,90,82,.12)); border:1px solid rgba(255,255,255,.15); font-size:105px; animation:floatFood 5s ease-in-out infinite,glow 4s ease-in-out infinite; }
.food-orbit-small { position:absolute; right:27%; top:59%; font-size:44px; animation:floatFood 4.2s ease-in-out infinite; }
.landing-perks { display:flex; flex-wrap:wrap; gap:10px; margin-top:34px; }
.landing-perks span { padding:10px 14px; border:1px solid rgba(255,255,255,.13); background:rgba(255,255,255,.055); color:#fff7e8; border-radius:999px; font-size:.88rem; }
.landing-footer { color:rgba(255,247,232,.5); font-size:.8rem; margin-top:36px; }
@media (max-width:800px) { .food-orbit { position:relative; right:auto; top:auto; width:140px; height:140px; font-size:70px; margin:30px 0 0; } .food-orbit-small { display:none; } .landing-screen { min-height:auto; } }

/* Extra polish: CSS-only motion, so the project still uses Python + Streamlit. */
@keyframes gradientDrift { 0%,100% { background-position:0% 50%; } 50% { background-position:100% 50%; } }
@keyframes riseIn { from { opacity:0; transform:translateY(22px) scale(.985); } to { opacity:1; transform:translateY(0) scale(1); } }
@keyframes softPulse { 0%,100% { box-shadow:0 0 0 0 rgba(255,201,40,.16); } 50% { box-shadow:0 0 0 9px rgba(255,201,40,0); } }
@keyframes ringSpin { from { transform:rotate(0deg); } to { transform:rotate(360deg); } }
@keyframes sparkle { 0%,100% { opacity:.45; transform:scale(.94); } 50% { opacity:1; transform:scale(1.06); } }
html { scroll-behavior:smooth; }
.block-container { animation:riseIn .55s cubic-bezier(.2,.75,.25,1) both; }
.stApp { background-image:radial-gradient(ellipse at 8% 18%,rgba(255,90,82,.075),transparent 27%),radial-gradient(ellipse at 90% 4%,rgba(255,201,40,.085),transparent 30%),linear-gradient(145deg,#101116,#15121a 55%,#101116); background-size:160% 160%; animation:gradientDrift 24s ease-in-out infinite; }
.hero { background:linear-gradient(115deg,#211526,#45233d,#282039,#211526); background-size:240% 240%; animation:gradientDrift 16s ease infinite, riseIn .65s ease both; position:relative; overflow:hidden; }
.hero:after { content:'✦'; position:absolute; right:34px; top:10px; font-size:74px; line-height:1; color:rgba(255,201,40,.12); animation:sparkle 4s ease-in-out infinite; pointer-events:none; }
.hero .display { letter-spacing:-.035em; text-shadow:0 4px 22px rgba(255,201,40,.12); }
.rest-card { backdrop-filter:blur(12px); animation:riseIn .55s cubic-bezier(.2,.75,.25,1) both; }
.rest-card:hover { transform:translateY(-5px) scale(1.012); box-shadow:0 16px 36px rgba(0,0,0,.22); }
.stButton button { position:relative; overflow:hidden; }
.stButton button:active { transform:scale(.975); }
.stButton button[kind="primary"] { background:linear-gradient(115deg,#ff6458,#e93f55,#ff8a50); background-size:200% 200%; animation:gradientDrift 8s ease infinite; box-shadow:0 8px 24px rgba(255,90,82,.13); }
.stButton button[kind="primary"]:hover { box-shadow:0 12px 30px rgba(255,90,82,.27); }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius:16px !important; border-color:rgba(255,255,255,.12) !important; background:linear-gradient(145deg,rgba(255,255,255,.035),rgba(255,255,255,.012)); transition:border-color .2s ease,transform .2s ease,box-shadow .2s ease; }
[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color:rgba(255,201,40,.32) !important; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] { border-radius:12px; }
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus { border-color:var(--gold); box-shadow:0 0 0 2px rgba(255,201,40,.12); }
.pill { transition:transform .18s ease,filter .18s ease; }
.pill:hover { transform:translateY(-2px); filter:brightness(1.12); }
.landing-screen { background-size:180% 180%; animation:gradientDrift 18s ease infinite, riseIn .8s cubic-bezier(.2,.75,.25,1) both; }
.landing-screen:before { content:''; position:absolute; width:330px; height:330px; border-radius:50%; right:2%; bottom:-180px; background:rgba(255,90,82,.12); filter:blur(35px); animation:floatFood 7s ease-in-out infinite; pointer-events:none; }
.landing-screen:after { animation:ringSpin 38s linear infinite; }
.brand-mark { animation:riseIn .7s .08s both,softPulse 4s 1s ease-in-out infinite; }
.landing-kicker { animation:riseIn .7s .16s both; }
.landing-title { animation:riseIn .75s .24s both; }
.landing-copy { animation:riseIn .75s .34s both; }
.landing-perks span { transition:transform .2s ease,border-color .2s ease,background .2s ease; }
.landing-perks span:hover { transform:translateY(-3px); border-color:rgba(255,201,40,.45); background:rgba(255,201,40,.09); }
.landing-footer { letter-spacing:.08em; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; scroll-behavior:auto !important; transition-duration:.01ms !important; } }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 2. DATA: LOCATIONS, RESTAURANTS, MENUS, COUPONS, PRICING RULES
# ---------------------------------------------------------------------------
# Coordinates are approximate (latitude, longitude) around Sonipat, Haryana.
PRESET_LOCATIONS = {
    "OP Jindal Global University": (28.9540, 77.0960),
    "Sonipat Bus Stand": (28.9931, 77.0151),
    "Rai, Sonipat": (28.9316, 77.0919),
    "Kundli (far - to test the delivery limit)": (28.8648, 77.1264),
}
DEFAULT_LOCATION = "OP Jindal Global University"

# Each restaurant is a dictionary. A menu item is (name, description, price, is_veg).
RESTAURANTS = [
    {
        "name": "Spice Route Kitchen", "emoji": "🍛", "cuisine": "North Indian",
        "rating": 4.5, "prep": 25, "packaging": 15, "lat": 28.9590, "lon": 77.0900,
        "menu": [
            ("Paneer Butter Masala", "Creamy tomato gravy, soft paneer", 240, True),
            ("Dal Makhani", "Slow-cooked black lentils", 190, True),
            ("Butter Chicken", "Tandoori chicken in rich gravy", 290, False),
            ("Chicken Biryani", "Dum biryani with raita", 260, False),
            ("Butter Naan", "Fresh from the tandoor", 45, True),
            ("Jeera Rice", "Fragrant cumin rice", 120, True),
        ],
    },
    {
        "name": "Burger Barn", "emoji": "🍔", "cuisine": "Burgers and Fries",
        "rating": 4.2, "prep": 18, "packaging": 10, "lat": 28.9480, "lon": 77.1010,
        "menu": [
            ("Classic Veg Burger", "Crispy patty, lettuce, mayo", 99, True),
            ("Crispy Chicken Burger", "Double crunch chicken fillet", 149, False),
            ("Cheese Fries", "Loaded with melted cheese", 109, True),
            ("Peri Peri Fries", "Spicy and crunchy", 99, True),
            ("Chicken Wings (6 pcs)", "Smoky BBQ glaze", 179, False),
            ("Chocolate Shake", "Thick and chilled", 119, True),
        ],
    },
    {
        "name": "Pizza Piazza", "emoji": "🍕", "cuisine": "Italian",
        "rating": 4.4, "prep": 28, "packaging": 20, "lat": 28.9700, "lon": 77.0800,
        "menu": [
            ("Margherita Pizza", "Classic cheese and basil", 199, True),
            ("Farmhouse Pizza", "Capsicum, onion, tomato, corn", 299, True),
            ("Pepperoni Pizza", "Loaded with pepperoni", 329, False),
            ("Garlic Bread", "Buttery and toasted", 119, True),
            ("Pasta Alfredo", "White sauce penne", 219, True),
            ("Choco Lava Cake", "Warm molten centre", 99, True),
        ],
    },
    {
        "name": "Dragon Wok", "emoji": "🥡", "cuisine": "Chinese",
        "rating": 4.1, "prep": 22, "packaging": 15, "lat": 28.9560, "lon": 77.1100,
        "menu": [
            ("Veg Hakka Noodles", "Wok-tossed with veggies", 150, True),
            ("Chicken Fried Rice", "Egg and chicken, smoky wok flavour", 180, False),
            ("Veg Manchurian", "Crispy balls in tangy sauce", 160, True),
            ("Chilli Chicken", "Dry, spicy and saucy", 220, False),
            ("Veg Spring Rolls", "Crunchy golden rolls", 120, True),
            ("Hot and Sour Soup", "Peppery and warming", 110, True),
        ],
    },
    {
        "name": "Green Bowl", "emoji": "🥗", "cuisine": "Healthy (Pure Veg)",
        "rating": 4.6, "prep": 15, "packaging": 12, "lat": 28.9520, "lon": 77.0990,
        "menu": [
            ("Quinoa Salad Bowl", "Quinoa, veggies, lemon dressing", 189, True),
            ("Paneer Wrap", "Grilled paneer in a whole wheat wrap", 149, True),
            ("Fresh Fruit Bowl", "Seasonal fruits", 129, True),
            ("Cold-Pressed Juice", "No added sugar", 99, True),
            ("Hummus Platter", "With pita and veggie sticks", 169, True),
            ("Oats Banana Smoothie", "Filling and light", 119, True),
        ],
    },
]

# Coupons: type, value, maximum discount, minimum order and description
COUPONS = {
    "WELCOME50": {"type": "percent", "value": 50, "cap": 100, "min": 199,
                  "desc": "50% off up to ₹100 on orders of ₹199 or more"},
    "FOODIE20": {"type": "percent", "value": 20, "cap": 80, "min": 299,
                 "desc": "20% off up to ₹80 on orders of ₹299 or more"},
    "FREEDEL": {"type": "freedel", "value": 0, "cap": 0, "min": 149,
                "desc": "Free delivery on orders of ₹149 or more"},
}

# Pricing rules (all amounts in rupees)
MAX_DELIVERY_KM = 10       # we do not deliver beyond this road distance
ROAD_FACTOR = 1.3          # road distance is roughly 1.3 x straight-line distance
FREE_DELIVERY_ABOVE = 499  # free delivery when the item total is at least this
PLATFORM_FEE = 5
EXPRESS_FEE = 30
GST_RATE = 0.05            # 5% GST on food


# ---------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------------------------
def inr(amount):
    """Format a number as Indian rupees, e.g. 1234.5 -> ₹1,234.50"""
    return f"₹{amount:,.2f}"


def road_distance_km(lat1, lon1, lat2, lon2):
    """Haversine formula: straight-line distance between two GPS points,
    multiplied by ROAD_FACTOR to estimate the real road distance."""
    earth_radius = 6371  # km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(d_lon / 2) ** 2)
    straight_line = 2 * earth_radius * math.asin(math.sqrt(a))
    return straight_line * ROAD_FACTOR


def estimate_eta(prep_minutes, distance_km, express):
    """Delivery time = cooking time + riding time (about 25 km/h in the city)."""
    ride_minutes = distance_km / 25 * 60
    eta = prep_minutes + ride_minutes
    if express:
        eta = eta - 8  # express orders are prioritised
    return max(10, round(eta))


def base_delivery_fee(distance_km, item_total):
    """Delivery fee depends on the order value and the distance."""
    if item_total >= FREE_DELIVERY_ABOVE:
        return 0
    elif distance_km <= 2:
        return 20
    elif distance_km <= 5:
        return 35
    elif distance_km <= 8:
        return 50
    else:
        return 70


def apply_coupon(code, item_total, delivery_fee):
    """Check a coupon code. Returns (discount, new_delivery_fee, message, is_valid)."""
    if code == "":
        return 0, delivery_fee, "", True

    if code not in COUPONS:
        return 0, delivery_fee, "Coupon not found. Check the spelling.", False

    coupon = COUPONS[code]
    if item_total < coupon["min"]:
        short_by = coupon["min"] - item_total
        return 0, delivery_fee, f"Add items worth {inr(short_by)} more to use {code}.", False

    if coupon["type"] == "percent":
        discount = min(item_total * coupon["value"] / 100, coupon["cap"])
        return round(discount, 2), delivery_fee, f"{code} applied. You save {inr(discount)}.", True
    else:  # free delivery coupon
        return 0, 0, f"{code} applied. Delivery is free.", True


def calculate_bill(item_total, packaging, distance_km, express, code, tip):
    """Put the whole bill together and return it as a dictionary."""
    fee = base_delivery_fee(distance_km, item_total)
    discount, fee, coupon_msg, coupon_ok = apply_coupon(code, item_total, fee)

    express_fee = EXPRESS_FEE if express else 0
    taxable_amount = item_total - discount           # GST is charged on food after discount
    gst = round(taxable_amount * GST_RATE, 2)
    total = taxable_amount + fee + express_fee + packaging + PLATFORM_FEE + gst + tip

    return {
        "item_total": item_total, "discount": discount, "delivery_fee": fee,
        "express_fee": express_fee, "packaging": packaging,
        "platform_fee": PLATFORM_FEE, "gst": gst, "tip": tip,
        "total": round(total, 2), "coupon_msg": coupon_msg, "coupon_ok": coupon_ok,
    }


def select_restaurant(name):
    """Remember the chosen restaurant."""
    if st.session_state.get("selected") != name:
        st.session_state.cart = {}
    st.session_state.selected = name
    st.session_state.page = "Menu"


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 4. APP STATE AND WELCOME EXPERIENCE
# ---------------------------------------------------------------------------
if "entered_app" not in st.session_state:
    st.session_state.entered_app = False
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "selected" not in st.session_state:
    st.session_state.selected = RESTAURANTS[0]["name"]
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "last_order" not in st.session_state:
    st.session_state.last_order = None

# First visit: show a full-screen brand introduction before the ordering app.
if not st.session_state.entered_app:
    st.markdown(
        """
        <div class="landing-screen">
          <div class="brand-mark">🍜</div>
          <div class="landing-kicker">Your campus food companion</div>
          <div class="landing-title">Good food.<br><span>Good mood.</span></div>
          <div class="landing-copy">Cravings don't wait. Discover your favourite local kitchens, find something delicious, and get it delivered right to your door at OP Jindal Global University.</div>
          <div class="landing-perks">
            <span>✦ Local favourites</span><span>⚡ Quick delivery</span><span>₹ Easy-on-pocket picks</span>
          </div>
          <div class="food-orbit">🍔</div><div class="food-orbit-small">🍕</div>
          <div class="landing-footer">MADE FOR YOUR CRAVINGS · SONIPAT, HARYANA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    spacer1, action_col, spacer2 = st.columns([1.2, 1.1, 2.2])
    with action_col:
        if st.button("Explore restaurants  →", type="primary", use_container_width=True, key="enter_ordering_app"):
            st.session_state.entered_app = True
            st.session_state.page = "Home"
            st.rerun()
    st.stop()

# ---------------------------------------------------------------------------
# 5. APP STATE AND NAVIGATION
# ---------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "selected" not in st.session_state:
    st.session_state.selected = RESTAURANTS[0]["name"]
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "last_order" not in st.session_state:
    st.session_state.last_order = None

st.sidebar.markdown("### 🍜 ChaiTapri Eats")
if st.sidebar.button("← Welcome screen", use_container_width=True):
    st.session_state.entered_app = False
    st.rerun()
pages = ["Home", "Menu", "Cart", "Checkout"]
page = st.sidebar.radio(
    "Navigate",
    pages,
    index=pages.index(st.session_state.page) if st.session_state.page in pages else 0,
)
st.session_state.page = page

st.sidebar.divider()
st.sidebar.markdown("### 📍 Deliver to")
location_mode = st.sidebar.radio(
    "How should we find you?",
    ["Use my GPS location", "Choose an area"],
    label_visibility="collapsed",
    key="location_mode",
)

user_lat, user_lon = PRESET_LOCATIONS[DEFAULT_LOCATION]
location_label = DEFAULT_LOCATION

if location_mode == "Use my GPS location":
    if GPS_AVAILABLE:
        try:
            st.sidebar.caption("Allow location access in your browser.")
            gps = streamlit_geolocation()
            if gps and gps.get("latitude") is not None and gps.get("longitude") is not None:
                user_lat, user_lon = gps["latitude"], gps["longitude"]
                location_label = "Your live GPS location"
                st.sidebar.success(f"Location found: {user_lat:.4f}, {user_lon:.4f}")
            else:
                st.sidebar.info("Waiting for location. Showing campus results meanwhile.")
        except Exception:
            st.sidebar.warning("GPS is not working. Use 'Choose an area' instead.")
    else:
        st.sidebar.warning("GPS package missing. Use 'Choose an area' instead.")
    st.sidebar.caption("Demo restaurants are in Sonipat.")
else:
    area = st.sidebar.selectbox("Pick your area", list(PRESET_LOCATIONS.keys()))
    user_lat, user_lon = PRESET_LOCATIONS[area]
    location_label = area

st.sidebar.markdown("### 🔎 Filters")
veg_only = st.sidebar.checkbox("Veg items only 🟢")
sort_by = st.sidebar.selectbox(
    "Sort restaurants by", ["Nearest first", "Top rated", "Fastest delivery"]
)

# Calculate distance and delivery estimates for each demo restaurant.
for r in RESTAURANTS:
    r["distance"] = road_distance_km(user_lat, user_lon, r["lat"], r["lon"])
    r["eta"] = estimate_eta(r["prep"], r["distance"], False)
    r["deliverable"] = r["distance"] <= MAX_DELIVERY_KM

if sort_by == "Nearest first":
    ordered = sorted(RESTAURANTS, key=lambda r: r["distance"])
elif sort_by == "Top rated":
    ordered = sorted(RESTAURANTS, key=lambda r: r["rating"], reverse=True)
else:
    ordered = sorted(RESTAURANTS, key=lambda r: r["eta"])

restaurant = next(
    (r for r in RESTAURANTS if r["name"] == st.session_state.selected),
    ordered[0],
)

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def cart_count():
    return sum(st.session_state.cart.values())

def cart_item_total():
    return sum(
        quantity * item[2]
        for item in restaurant["menu"]
        for quantity in [st.session_state.cart.get(item[0], 0)]
    )

# Shared header
st.markdown(
    f"""
    <div class="hero">
      <p class="display">🍜 ChaiTapri Eats</p>
      <p>Local kitchens. Big cravings. Delivered to <b>{location_label}</b>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

nav1, nav2, nav3, nav4 = st.columns(4)
for col, label, target in [
    (nav1, "🏠 Home", "Home"),
    (nav2, "🍽️ Menu", "Menu"),
    (nav3, f"🛒 Cart ({cart_count()})", "Cart"),
    (nav4, "💳 Checkout", "Checkout"),
]:
    if col.button(label, use_container_width=True, type="primary" if st.session_state.page == target else "secondary"):
        go_to(target)

st.divider()

# ---------------------------------------------------------------------------
# 5. HOME PAGE
# ---------------------------------------------------------------------------
if st.session_state.page == "Home":
    st.markdown("## Find your next meal")
    st.write("Five local kitchens, plenty of comfort food. Pick a place and let's get your order started.")

    card_columns = st.columns(3)
    for i, r in enumerate(ordered):
        with card_columns[i % 3]:
            status = f"{r['eta']} min delivery" if r["deliverable"] else "Outside delivery area"
            st.markdown(
                f"""
                <div class="rest-card">
                  <div class="rest-name">{r['emoji']} {r['name']}</div>
                  <div class="muted">{r['cuisine']}</div>
                  <span class="pill rating">★ {r['rating']}</span>
                  <span class="pill time">{status}</span>
                  <span class="pill dist">{r['distance']:.1f} km</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("View menu", key=f"home_{r['name']}", use_container_width=True):
                select_restaurant(r["name"])
                st.rerun()

    with st.expander("🗺️ See restaurants on the map"):
        map_rows = [{"lat": user_lat, "lon": user_lon, "color": "#1E64F0", "size": 140}]
        for r in RESTAURANTS:
            map_rows.append({"lat": r["lat"], "lon": r["lon"], "color": "#D7263D", "size": 90})
        st.map(pd.DataFrame(map_rows), latitude="lat", longitude="lon", color="color", size="size")
        st.caption("Blue dot: delivery location. Red dots: restaurants.")

# ---------------------------------------------------------------------------
# 6. MENU PAGE
# ---------------------------------------------------------------------------
elif st.session_state.page == "Menu":
    st.markdown(f"## {restaurant['emoji']} {restaurant['name']}")
    st.caption(
        f"{restaurant['cuisine']} · ★ {restaurant['rating']} · "
        f"{restaurant['distance']:.1f} km away · about {restaurant['eta']} min"
    )

    chosen_restaurant = st.selectbox(
        "Choose a restaurant",
        [r["name"] for r in ordered],
        index=[r["name"] for r in ordered].index(restaurant["name"]),
        key="menu_restaurant_selector",
    )
    if chosen_restaurant != st.session_state.selected:
        select_restaurant(chosen_restaurant)
        st.rerun()

    if not restaurant["deliverable"]:
        st.error(
            f"We deliver within {MAX_DELIVERY_KM} km. Choose another restaurant or change your delivery area."
        )

    shown_items = 0
    for item_name, description, price, is_veg in restaurant["menu"]:
        if veg_only and not is_veg:
            continue
        shown_items += 1
        with st.container(border=True):
            item_col, price_col, action_col = st.columns([4, 1.2, 1.5])
            dot = "🟢" if is_veg else "🔴"
            item_col.markdown(f"**{dot} {item_name}**")
            item_col.caption(description)
            price_col.markdown(f"**{inr(price)}**")
            current_qty = st.session_state.cart.get(item_name, 0)
            action_col.caption(f"In cart: {current_qty}")
            add_col, remove_col = action_col.columns(2)
            if add_col.button("+", key=f"add_{restaurant['name']}_{item_name}", use_container_width=True):
                if restaurant["deliverable"]:
                    st.session_state.cart[item_name] = current_qty + 1
                    st.rerun()
            if remove_col.button("−", key=f"remove_{restaurant['name']}_{item_name}", use_container_width=True):
                if current_qty > 1:
                    st.session_state.cart[item_name] = current_qty - 1
                elif current_qty == 1:
                    del st.session_state.cart[item_name]
                st.rerun()

    if shown_items == 0:
        st.info("No items match your filter at this restaurant.")

    st.divider()
    st.markdown(f"**Cart subtotal: {inr(cart_item_total())}**")
    left, right = st.columns(2)
    if left.button("Continue shopping", use_container_width=True):
        go_to("Home")
    if right.button("View cart", type="primary", use_container_width=True):
        go_to("Cart")

# ---------------------------------------------------------------------------
# 7. CART PAGE
# ---------------------------------------------------------------------------
elif st.session_state.page == "Cart":
    st.markdown("## 🛒 Your cart")
    if not st.session_state.cart:
        st.info("Your cart is empty. Visit the menu to add something delicious.")
        if st.button("Browse restaurants", type="primary"):
            go_to("Home")
    else:
        st.caption(f"Order from {restaurant['name']}")
        for item_name, description, price, is_veg in restaurant["menu"]:
            quantity = st.session_state.cart.get(item_name, 0)
            if quantity <= 0:
                continue
            row1, row2, row3, row4 = st.columns([4, 1, 1, 1.5])
            row1.write(item_name)
            row2.write(f"{inr(price)}")
            row3.write(f"× {quantity}")
            row4.write(f"**{inr(price * quantity)}**")
            minus_col, plus_col, remove_col = st.columns([1, 1, 2])
            if minus_col.button("−", key=f"cart_minus_{item_name}"):
                if quantity > 1:
                    st.session_state.cart[item_name] = quantity - 1
                else:
                    del st.session_state.cart[item_name]
                st.rerun()
            if plus_col.button("+", key=f"cart_plus_{item_name}"):
                st.session_state.cart[item_name] = quantity + 1
                st.rerun()
            if remove_col.button("Remove item", key=f"cart_remove_{item_name}"):
                del st.session_state.cart[item_name]
                st.rerun()
            st.divider()

        st.markdown(f"### Item total: {inr(cart_item_total())}")
        col_a, col_b = st.columns(2)
        if col_a.button("← Back to menu", use_container_width=True):
            go_to("Menu")
        if col_b.button("Proceed to checkout", type="primary", use_container_width=True):
            go_to("Checkout")

# ---------------------------------------------------------------------------
# 8. CHECKOUT PAGE
# ---------------------------------------------------------------------------
elif st.session_state.page == "Checkout":
    st.markdown("## 💳 Checkout")
    if not st.session_state.cart:
        st.info("Your cart is empty. Add food before checking out.")
        if st.button("Browse menu", type="primary"):
            go_to("Menu")
    elif not restaurant["deliverable"]:
        st.error(
            f"{restaurant['name']} is {restaurant['distance']:.1f} km away. "
            f"We deliver within {MAX_DELIVERY_KM} km. Choose a closer restaurant or change your area."
        )
        if st.button("Choose another restaurant"):
            go_to("Home")
    else:
        st.markdown(f"**Restaurant:** {restaurant['name']}")
        st.markdown("### Order summary")
        for item_name, description, price, is_veg in restaurant["menu"]:
            quantity = st.session_state.cart.get(item_name, 0)
            if quantity > 0:
                st.write(f"{quantity} × {item_name} — {inr(quantity * price)}")

        item_total = cart_item_total()
        st.divider()
        delivery_speed = st.radio("Delivery speed", ["Standard", "Express ⚡ (+₹30)"], horizontal=True)
        express = delivery_speed.startswith("Express")
        tip = st.select_slider("Tip for your delivery partner (₹)", options=[0, 10, 20, 30, 50], value=0)
        coupon_code = st.text_input("Coupon code", placeholder="Try WELCOME50").strip().upper()
        payment = st.selectbox("Payment method", ["UPI", "Credit / Debit Card", "Cash on Delivery"])
        contactless = st.checkbox("Contactless delivery")
        instructions = st.text_input("Cooking or delivery note", placeholder="Less spicy, ring the bell...")

        with st.expander("Available coupons"):
            for code, info in COUPONS.items():
                st.markdown(f"**{code}**: {info['desc']}")

        bill = calculate_bill(
            item_total, restaurant["packaging"], restaurant["distance"],
            express, coupon_code, tip
        )
        eta = estimate_eta(restaurant["prep"], restaurant["distance"], express)

        if bill["coupon_msg"]:
            if bill["coupon_ok"]:
                st.success(bill["coupon_msg"])
            else:
                st.warning(bill["coupon_msg"])

        rows = ""
        for name, qty, price in [
            (item_name, st.session_state.cart.get(item_name, 0), price)
            for item_name, description, price, is_veg in restaurant["menu"]
        ]:
            if qty > 0:
                rows += (
                    f'<div class="bill-row"><span>{qty} × {name}</span>'
                    f'<span>{inr(qty * price)}</span></div>'
                )
        rows += f'<div class="bill-row"><span>Item total</span><span>{inr(bill["item_total"])}</span></div>'
        if bill["discount"] > 0:
            rows += f'<div class="bill-row saving"><span>Coupon discount</span><span>- {inr(bill["discount"])}</span></div>'
        fee_text = "FREE" if bill["delivery_fee"] == 0 else inr(bill["delivery_fee"])
        rows += f'<div class="bill-row"><span>Delivery fee</span><span>{fee_text}</span></div>'
        if bill["express_fee"] > 0:
            rows += f'<div class="bill-row"><span>Express delivery</span><span>{inr(bill["express_fee"])}</span></div>'
        rows += f'<div class="bill-row"><span>Packaging</span><span>{inr(bill["packaging"])}</span></div>'
        rows += f'<div class="bill-row"><span>Platform fee</span><span>{inr(bill["platform_fee"])}</span></div>'
        rows += f'<div class="bill-row"><span>GST (5%)</span><span>{inr(bill["gst"])}</span></div>'
        if bill["tip"] > 0:
            rows += f'<div class="bill-row"><span>Tip</span><span>{inr(bill["tip"])}</span></div>'
        rows += f'<div class="bill-total"><span>To pay</span><span>{inr(bill["total"])}</span></div>'
        st.markdown(f'<div class="bill-box">{rows}</div>', unsafe_allow_html=True)
        st.caption(f"Estimated delivery in about {eta} minutes.")

        if st.button("Place order", type="primary", use_container_width=True):
            order_id = "CT" + str(random.randint(10000, 99999))
            partner = random.choice(["Rahul", "Amit", "Sandeep", "Vikram", "Deepak"])
            st.session_state.last_order = {
                "order_id": order_id,
                "restaurant": restaurant["name"],
                "partner": partner,
                "eta": eta,
                "total": bill["total"],
                "payment": payment,
                "contactless": contactless,
                "instructions": instructions.strip(),
            }
            st.session_state.cart = {}
            st.balloons()
            st.success(f"Order {order_id} placed successfully!")
            st.markdown(f"### Thank you for ordering from {restaurant['name']}!")
            st.write(f"Your delivery partner is **{partner}**.")
            st.write(f"Estimated delivery: **{eta} minutes**.")
            st.write(f"Total paid / payable: **{inr(bill['total'])}** via **{payment}**.")
            if contactless:
                st.info("Contactless delivery: your order will be left at the door.")
            if instructions.strip():
                st.info(f"Note sent to the restaurant: {instructions.strip()}")
        elif st.session_state.last_order:
            last = st.session_state.last_order
            st.caption(f"Previous demo order: {last['order_id']} from {last['restaurant']}.")

st.divider()
st.caption("ChaiTapri Eats is a student project. Restaurants, menus and prices are made up for demonstration.")
