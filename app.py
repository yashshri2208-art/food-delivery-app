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
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;800&family=DM+Sans:wght@400;500;700&display=swap');

html, body, [class*="css"], .stMarkdown, .stButton button, label {
    font-family: 'DM Sans', 'Segoe UI', sans-serif;
}
h1, h2, h3, .display {
    font-family: 'Bricolage Grotesque', 'Segoe UI', sans-serif !important;
}
.hero {
    background: #2B1B2E;
    border-radius: 20px;
    padding: 30px 36px;
    margin-bottom: 22px;
    border-bottom: 6px solid #F2B705;
}
.hero .display {
    color: #F2B705; font-size: 2.6rem; font-weight: 800;
    margin: 0; line-height: 1.1;
}
.hero p { color: #F5EBDD; margin: 8px 0 0 0; font-size: 1.05rem; }
.section-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.5rem; font-weight: 800; margin: 18px 0 8px 0;
}
.rest-card {
    border: 1.5px solid rgba(128,128,128,.30);
    border-radius: 16px; padding: 14px 16px; margin-bottom: 8px;
    background: rgba(242,183,5,.07);
}
.rest-card.selected {
    border: 2.5px solid #D7263D; background: rgba(215,38,61,.08);
}
.rest-card.far { opacity: .55; }
.rest-name { font-size: 1.12rem; font-weight: 700; }
.muted { opacity: .72; font-size: .88rem; }
.pill {
    display: inline-block; padding: 2px 10px; border-radius: 999px;
    font-size: .78rem; font-weight: 700; margin: 6px 6px 0 0;
}
.pill.rating { background: #2E9E83; color: white; }
.pill.time   { background: rgba(242,183,5,.30); }
.pill.dist   { background: rgba(43,27,46,.12); }
.pill.out    { background: #D7263D; color: white; }
.menu-name { font-weight: 700; font-size: 1.02rem; }
.price { font-weight: 700; color: #D7263D; }
.bill-box {
    border: 1.5px solid rgba(128,128,128,.30);
    border-radius: 16px; padding: 16px 18px; margin: 8px 0 12px 0;
}
.bill-row {
    display: flex; justify-content: space-between;
    padding: 6px 0; border-bottom: 1px dashed rgba(128,128,128,.35);
}
.bill-row.saving { color: #2E9E83; font-weight: 700; }
.bill-total {
    display: flex; justify-content: space-between;
    padding-top: 12px; font-size: 1.35rem; font-weight: 800; color: #D7263D;
}
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
    """Button callback: remember which restaurant the customer chose."""
    st.session_state.selected = name


# ---------------------------------------------------------------------------
# 4. SIDEBAR: LOCATION (GPS) AND FILTERS
# ---------------------------------------------------------------------------
st.sidebar.markdown("### 📍 Deliver to")
location_mode = st.sidebar.radio(
    "How should we find you?",
    ["Use my GPS location", "Choose an area"],
    label_visibility="collapsed",
)

user_lat, user_lon = PRESET_LOCATIONS[DEFAULT_LOCATION]
location_label = DEFAULT_LOCATION

if location_mode == "Use my GPS location":
    if GPS_AVAILABLE:
        try:
            st.sidebar.caption("Tap the button below and allow location access in your browser.")
            gps = streamlit_geolocation()  # asks the browser for the live location
            if gps and gps.get("latitude") is not None and gps.get("longitude") is not None:
                user_lat, user_lon = gps["latitude"], gps["longitude"]
                location_label = "Your live GPS location"
                st.sidebar.success(f"Location found: {user_lat:.4f}, {user_lon:.4f}")
            else:
                st.sidebar.info("Waiting for location. Showing results for the campus until then.")
        except Exception:
            st.sidebar.warning("GPS is not working in this browser. Use 'Choose an area' instead.")
    else:
        st.sidebar.warning("GPS package missing. Run: pip install streamlit-geolocation")
    st.sidebar.caption("Demo restaurants are in Sonipat. Outside Sonipat, they will show as out of range.")
else:
    area = st.sidebar.selectbox("Pick your area", list(PRESET_LOCATIONS.keys()))
    user_lat, user_lon = PRESET_LOCATIONS[area]
    location_label = area

st.sidebar.markdown("### 🔎 Filters")
veg_only = st.sidebar.checkbox("Veg items only 🟢")
sort_by = st.sidebar.selectbox("Sort restaurants by", ["Nearest first", "Top rated", "Fastest delivery"])


# ---------------------------------------------------------------------------
# 5. HEADER
# ---------------------------------------------------------------------------
st.markdown(
    f"""
<div class="hero">
  <p class="display">ChaiTapri Eats</p>
  <p>Hot food from five local kitchens, at your door. Delivering to <b>{location_label}</b>.</p>
</div>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 6. RESTAURANTS NEAR YOU (distance and delivery time use the user's location)
# ---------------------------------------------------------------------------
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

# Keep the selected restaurant stored between reruns
if "selected" not in st.session_state:
    st.session_state.selected = ordered[0]["name"]

st.markdown('<div class="section-title">Restaurants near you</div>', unsafe_allow_html=True)

card_columns = st.columns(3)
for i, r in enumerate(ordered):
    with card_columns[i % 3]:
        css_class = "rest-card"
        if r["name"] == st.session_state.selected:
            css_class += " selected"
        if not r["deliverable"]:
            css_class += " far"
        status_pill = (f'<span class="pill time">{r["eta"]} min</span>' if r["deliverable"]
                       else '<span class="pill out">Out of range</span>')
        st.markdown(
            f'<div class="{css_class}">'
            f'<div class="rest-name">{r["emoji"]} {r["name"]}</div>'
            f'<div class="muted">{r["cuisine"]}</div>'
            f'<span class="pill rating">★ {r["rating"]}</span>'
            f'{status_pill}'
            f'<span class="pill dist">{r["distance"]:.1f} km</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        st.button("View menu", key=f"btn_{r['name']}", on_click=select_restaurant, args=(r["name"],))

# Map showing the customer (blue) and all restaurants (red)
with st.expander("🗺️ See the restaurants on the map", expanded=False):
    map_rows = [{"lat": user_lat, "lon": user_lon, "color": "#1E64F0", "size": 140}]
    for r in RESTAURANTS:
        map_rows.append({"lat": r["lat"], "lon": r["lon"], "color": "#D7263D", "size": 90})
    st.map(pd.DataFrame(map_rows), latitude="lat", longitude="lon", color="color", size="size")
    st.caption("Blue dot: you. Red dots: restaurants.")


# ---------------------------------------------------------------------------
# 7. MENU (left) AND CHECKOUT (right)
# ---------------------------------------------------------------------------
restaurant = next(r for r in RESTAURANTS if r["name"] == st.session_state.selected)
menu_col, bill_col = st.columns([3, 2], gap="large")

# ---- Menu ----
cart = []  # list of (item name, quantity, price)
with menu_col:
    st.markdown(
        f'<div class="section-title">{restaurant["emoji"]} {restaurant["name"]} menu</div>',
        unsafe_allow_html=True,
    )
    shown_items = 0
    for item_name, description, price, is_veg in restaurant["menu"]:
        if veg_only and not is_veg:
            continue  # skip non-veg items when the veg filter is on
        shown_items += 1
        with st.container(border=True):
            c1, c2 = st.columns([4, 2])
            dot = "🟢" if is_veg else "🔴"
            c1.markdown(
                f'<div class="menu-name">{dot} {item_name}</div>'
                f'<div class="muted">{description}</div>'
                f'<div class="price">{inr(price)}</div>',
                unsafe_allow_html=True,
            )
            qty = c2.number_input(
                f"Quantity of {item_name}", min_value=0, max_value=10, value=0, step=1,
                key=f"qty_{restaurant['name']}_{item_name}", label_visibility="collapsed",
            )
            if qty > 0:
                cart.append((item_name, qty, price))
    if shown_items == 0:
        st.info("No items match your filter at this restaurant.")

# ---- Checkout ----
with bill_col:
    st.markdown('<div class="section-title">Your order</div>', unsafe_allow_html=True)

    if len(cart) == 0:
        st.info("Your cart is empty. Add items from the menu to see your bill.")
    elif not restaurant["deliverable"]:
        st.error(
            f"{restaurant['name']} is {restaurant['distance']:.1f} km away. "
            f"We deliver within {MAX_DELIVERY_KM} km. Pick a closer restaurant or change your area."
        )
    else:
        try:
            item_total = sum(qty * price for _, qty, price in cart)

            # Checkout options (inputs)
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

            bill = calculate_bill(item_total, restaurant["packaging"], restaurant["distance"],
                                  express, coupon_code, tip)
            eta = estimate_eta(restaurant["prep"], restaurant["distance"], express)

            # Coupon feedback
            if bill["coupon_msg"]:
                if bill["coupon_ok"]:
                    st.success(bill["coupon_msg"])
                else:
                    st.warning(bill["coupon_msg"])

            # Bill (HTML so it looks like a receipt)
            rows = ""
            for name, qty, price in cart:
                rows += (f'<div class="bill-row"><span>{qty} × {name}</span>'
                         f"<span>{inr(qty * price)}</span></div>")
            rows += f'<div class="bill-row"><span>Item total</span><span>{inr(bill["item_total"])}</span></div>'
            if bill["discount"] > 0:
                rows += (f'<div class="bill-row saving"><span>Coupon discount</span>'
                         f'<span>- {inr(bill["discount"])}</span></div>')
            fee_text = "FREE" if bill["delivery_fee"] == 0 else inr(bill["delivery_fee"])
            rows += f'<div class="bill-row"><span>Delivery fee ({restaurant["distance"]:.1f} km)</span><span>{fee_text}</span></div>'
            if bill["express_fee"] > 0:
                rows += f'<div class="bill-row"><span>Express delivery</span><span>{inr(bill["express_fee"])}</span></div>'
            rows += f'<div class="bill-row"><span>Packaging</span><span>{inr(bill["packaging"])}</span></div>'
            rows += f'<div class="bill-row"><span>Platform fee</span><span>{inr(bill["platform_fee"])}</span></div>'
            rows += f'<div class="bill-row"><span>GST (5%)</span><span>{inr(bill["gst"])}</span></div>'
            if bill["tip"] > 0:
                rows += f'<div class="bill-row"><span>Tip</span><span>{inr(bill["tip"])}</span></div>'
            rows += f'<div class="bill-total"><span>To pay</span><span>{inr(bill["total"])}</span></div>'
            st.markdown(f'<div class="bill-box">{rows}</div>', unsafe_allow_html=True)

            st.caption(f"🛵 Estimated delivery in about {eta} minutes. Free delivery above {inr(FREE_DELIVERY_ABOVE)}.")

            # Place order
            if st.button("Place order", type="primary"):
                order_id = "CT" + str(random.randint(10000, 99999))
                partner = random.choice(["Rahul", "Amit", "Sandeep", "Vikram", "Deepak"])
                st.balloons()
                st.success(
                    f"Order {order_id} placed with {restaurant['name']}. "
                    f"{partner} will deliver in about {eta} minutes. "
                    f"Pay {inr(bill['total'])} by {payment}."
                )
                if contactless:
                    st.info("Contactless delivery: your order will be left at the door.")
                if instructions.strip():
                    st.info(f"Note sent to the restaurant: {instructions.strip()}")
        except Exception as error:
            # Safety net so the website never crashes in front of the user
            st.error(f"Something went wrong while preparing your bill: {error}")

st.divider()
st.caption("ChaiTapri Eats is a student project. Restaurants, menus and prices are made up for demonstration.")
