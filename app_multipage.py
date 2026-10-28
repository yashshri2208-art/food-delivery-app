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
    """Remember the chosen restaurant."""
    if st.session_state.get("selected") != name:
        st.session_state.cart = {}
    st.session_state.selected = name
    st.session_state.page = "Menu"
    st.session_state.page_navigation = "Menu"


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 4. APP STATE AND NAVIGATION
# ---------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "page_navigation" not in st.session_state:
    st.session_state.page_navigation = st.session_state.page
if "selected" not in st.session_state:
    st.session_state.selected = RESTAURANTS[0]["name"]
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "last_order" not in st.session_state:
    st.session_state.last_order = None

st.sidebar.markdown("### 🍽️ ChaiTapri Eats")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Menu", "Cart", "Checkout"],
    key="page_navigation",
    on_change=lambda: st.session_state.update(page=st.session_state.page_navigation),
)
page = st.session_state.page_navigation
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
    st.session_state.page_navigation = page_name
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
      <p class="display">ChaiTapri Eats</p>
      <p>Hot food from five local kitchens, at your door. Delivering to <b>{location_label}</b>.</p>
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
    st.write("Choose a local kitchen to browse its menu and start your order.")

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
