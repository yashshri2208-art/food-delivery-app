"""
ChaiTapri Eats - Food Delivery Website (Streamlit)
===================================================
Python Programming for Business Students - End Term Project

What this app does:
  1. Finds the customer's location (GPS or a chosen area)
  2. Shows nearby restaurants with distance, rating and delivery time
  3. Lets the customer pick items from a restaurant's menu
  4. Calculates a full bill: items, coupon, delivery fee, GST, tip, total
  5. Places demo orders and shows a short simulated delivery journey
  6. Suggests complementary items and tracks free-delivery milestones

Run with:  streamlit run app.py
"""

import math
import random
import time

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
/* Welcome screen: three original, illustrated campaign-style backgrounds. */
@keyframes welcomeRotate { 0%,30% { opacity:1; } 34%,96% { opacity:0; } 100% { opacity:1; } }
.welcome-carousel { position:absolute; inset:0; overflow:hidden; border-radius:30px; background:#211526; }
.welcome-slide { position:absolute; inset:0; opacity:0; animation:welcomeRotate 24s ease-in-out infinite; will-change:opacity; }
.welcome-slide:nth-child(1) { animation-delay:0s; background:radial-gradient(circle at 82% 36%,#ffbb52 0%,transparent 28%),linear-gradient(120deg,#341437 0%,#762548 52%,#f56c48 100%); }
.welcome-slide:nth-child(2) { animation-delay:8s; background:radial-gradient(circle at 85% 25%,#e0fc76 0%,transparent 27%),linear-gradient(120deg,#142c31 0%,#176c63 52%,#54ad77 100%); }
.welcome-slide:nth-child(3) { animation-delay:16s; background:radial-gradient(circle at 83% 32%,#ffbbdc 0%,transparent 27%),linear-gradient(120deg,#25163e 0%,#553d9b 54%,#c86dba 100%); }
.welcome-slide:before { content:""; position:absolute; width:360px; height:360px; border:2px solid rgba(255,255,255,.23); border-radius:50%; right:6%; top:12%; box-shadow:0 0 0 45px rgba(255,255,255,.055),0 0 0 95px rgba(255,255,255,.035); }
.welcome-slide:after { content:""; position:absolute; inset:0; background:linear-gradient(90deg,rgba(17,12,26,.72),rgba(17,12,26,.12) 80%); }
.welcome-sticker { position:absolute; right:10%; top:27%; font-size:clamp(105px,15vw,205px); transform:rotate(-12deg); filter:drop-shadow(0 22px 28px rgba(0,0,0,.22)); z-index:1; animation:floatFood 5s ease-in-out infinite; }
.landing-screen > :not(.welcome-carousel) { position:relative; z-index:2; }
@media (max-width:800px) { .welcome-sticker { right:2%; top:20%; opacity:.32; } }
@media (prefers-reduced-motion: reduce) { .welcome-slide { animation:none; } .welcome-slide:nth-child(1) { opacity:1; } }
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
.landing-perks span { display:inline-flex; align-items:center; justify-content:center; gap:8px; padding:10px 16px; border:1px solid rgba(255,255,255,.13); background:rgba(255,255,255,.055); color:#fff7e8; border-radius:999px; font-size:.88rem; line-height:1.2; white-space:nowrap; } .landing-perks .perk-icon { display:inline-flex; align-items:center; justify-content:center; flex:0 0 auto; width:1.1em; margin:0; padding:0; border:0; background:transparent; font-size:1em; line-height:1; }
.landing-footer { color:rgba(255,247,232,.5); font-size:.8rem; margin-top:36px; }
@media (max-width:800px) { .food-orbit { position:relative; right:auto; top:auto; width:140px; height:140px; font-size:70px; margin:30px 0 0; } .food-orbit-small { display:none; } .landing-screen { min-height:auto; } }


/* Keep the welcome campaign copy clear of the logo, perks and CTA at every screen size. */
.landing-screen { min-height: min(760px, 78vh); min-height: max(620px, 78vh); padding:clamp(26px,4vw,56px); }
.welcome-copy { position:absolute !important; left:clamp(26px,4vw,56px); top:clamp(190px,26vh,245px); right:clamp(26px,38%,520px); opacity:0; animation:welcomeRotate 24s ease-in-out infinite; pointer-events:none; z-index:3; will-change:opacity; }
.welcome-copy-1 { animation-delay:0s; }
.welcome-copy-2 { animation-delay:8s; }
.welcome-copy-3 { animation-delay:16s; }
.welcome-copy .landing-kicker { margin-top:0; font-size:clamp(.68rem,1vw,.78rem); }
.welcome-copy .landing-title { margin-top:12px; margin-bottom:14px; font-size:clamp(2.65rem,5.4vw,5.1rem); line-height:.98; letter-spacing:-.045em; overflow-wrap:normal; }
.welcome-copy .landing-copy { max-width:540px; font-size:clamp(.92rem,1.4vw,1.12rem); line-height:1.5; }
.landing-perks { position:absolute; left:clamp(26px,4vw,56px); right:clamp(26px,4vw,56px); bottom:58px; margin-top:0; z-index:4; }
.landing-footer { position:absolute; left:clamp(26px,4vw,56px); bottom:24px; margin-top:0; z-index:4; }
@media (max-width:900px) { .landing-screen { min-height:680px; padding:26px; } .welcome-copy { top:210px; right:26px; } .welcome-copy .landing-title { font-size:clamp(2.6rem,7.2vw,4.2rem); max-width:660px; } .welcome-sticker { right:1%; top:22%; opacity:.26; } .landing-perks { bottom:66px; } }
@media (max-width:560px) { .landing-screen { min-height:720px; padding:22px; } .brand-mark { width:50px; height:50px; font-size:25px; } .welcome-copy { left:22px; right:22px; top:190px; } .welcome-copy .landing-title { font-size:clamp(2.4rem,11vw,3.5rem); line-height:1; } .welcome-copy .landing-copy { font-size:.95rem; } .welcome-sticker { top:30%; right:0; opacity:.16; } .landing-perks { left:22px; right:22px; bottom:68px; gap:7px; } .landing-perks span { font-size:.76rem; padding:8px 10px; } .landing-footer { left:22px; bottom:22px; font-size:.68rem; } }
@media (prefers-reduced-motion: reduce) { .welcome-copy { animation:none; } .welcome-copy-1 { opacity:1; } .welcome-copy-2,.welcome-copy-3 { display:none; } }

/* Welcome screen: pin the campaign to the actual viewport so Streamlit gutters cannot leave black margins. */
[data-testid="stAppViewContainer"]:has(.landing-screen) [data-testid="stHeader"],
[data-testid="stAppViewContainer"]:has(.landing-screen) [data-testid="stToolbar"] { display:none !important; height:0 !important; visibility:hidden !important; }
[data-testid="stAppViewContainer"]:has(.landing-screen) .main,
[data-testid="stAppViewContainer"]:has(.landing-screen) section.main,
[data-testid="stAppViewContainer"]:has(.landing-screen) section.main > div,
[data-testid="stAppViewContainer"]:has(.landing-screen) .main .block-container,
[data-testid="stAppViewContainer"]:has(.landing-screen) [data-testid="stVerticalBlock"] { max-width:none !important; width:100% !important; padding:0 !important; margin:0 !important; gap:0 !important; }
[data-testid="stAppViewContainer"]:has(.landing-screen) .landing-screen { position:fixed !important; inset:0 !important; z-index:50 !important; width:100vw !important; height:100vh !important; height:100dvh !important; min-height:100vh !important; min-height:100dvh !important; box-sizing:border-box !important; margin:0 !important; border:0 !important; border-radius:0 !important; box-shadow:none !important; }
[data-testid="stAppViewContainer"]:has(.landing-screen) [data-testid="stButton"] { position:fixed !important; left:50% !important; bottom:28px !important; transform:translateX(-50%) !important; width:min(360px, calc(100vw - 36px)) !important; z-index:1001 !important; margin:0 !important; }
[data-testid="stAppViewContainer"]:has(.landing-screen) [data-testid="stButton"] button { width:100% !important; min-height:60px !important; padding:16px 24px !important; white-space:nowrap !important; }
[data-testid="stAppViewContainer"]:has(.landing-screen) [data-testid="stButton"] button p { font-size:1.12rem !important; white-space:nowrap !important; overflow:visible !important; text-overflow:clip !important; }
[data-testid="stAppViewContainer"]:has(.landing-screen) [data-testid="stButton"] button span { white-space:nowrap !important; overflow:visible !important; text-overflow:clip !important; }
@media (max-width:560px) { [data-testid="stAppViewContainer"]:has(.landing-screen) .landing-screen { padding:22px !important; } }

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

/* Distinct branch interfaces; same brand palette, different layouts */
.branch-hero { position:relative; overflow:hidden; padding:30px 32px; border-radius:24px; margin:4px 0 22px; border:1px solid rgba(255,255,255,.10); animation:pageIn .48s ease both; }
.branch-hero:after { content:""; position:absolute; right:-38px; top:-70px; width:210px; height:210px; border:1px solid rgba(255,255,255,.10); border-radius:50%; box-shadow:0 0 0 25px rgba(255,255,255,.025),0 0 0 52px rgba(255,255,255,.02); pointer-events:none; }
.branch-kicker { text-transform:uppercase; letter-spacing:.16em; font-size:.75rem; font-weight:800; color:var(--mint); margin-bottom:12px; }
.branch-title { font-family:'Bricolage Grotesque',sans-serif; font-size:clamp(1.8rem,4vw,3.3rem); line-height:1.04; font-weight:800; color:var(--gold); max-width:850px; }
.branch-description { color:rgba(255,247,232,.82); font-size:1rem; line-height:1.65; max-width:780px; margin-top:12px; }
.branch-meta { display:flex; flex-wrap:wrap; gap:10px; margin-top:20px; }
.branch-meta span { padding:8px 12px; border-radius:999px; background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.09); font-size:.82rem; }
.restaurant-tile { min-height:250px; border:1px solid rgba(255,255,255,.12); border-radius:22px; padding:20px; margin-bottom:9px; background:linear-gradient(145deg,rgba(255,201,40,.12),rgba(255,90,82,.045) 55%,rgba(255,255,255,.025)); transition:transform .24s ease,border-color .24s ease,box-shadow .24s ease; animation:pageIn .5s ease both; }
.restaurant-tile:hover { transform:translateY(-5px); border-color:rgba(255,201,40,.55); box-shadow:0 16px 34px rgba(0,0,0,.22); }
.tile-emoji { font-size:2.6rem; margin-bottom:12px; animation:floatFood 5s ease-in-out infinite; }
.tile-cuisine { color:var(--mint); text-transform:uppercase; letter-spacing:.12em; font-size:.7rem; font-weight:800; }
.tile-name { font-family:'Bricolage Grotesque',sans-serif; font-size:1.2rem; font-weight:800; margin:5px 0 12px; color:#fff7e8; }
.tile-stats { display:flex; gap:8px; flex-wrap:wrap; font-size:.8rem; }
.tile-stats span { background:rgba(255,255,255,.08); border-radius:999px; padding:5px 9px; }
.tile-status { color:var(--gold); margin-top:15px; font-weight:700; font-size:.88rem; }
.promo-strip { display:flex; flex-wrap:wrap; justify-content:space-around; gap:12px; margin-top:24px; padding:18px; border:1px solid rgba(255,255,255,.10); border-radius:18px; background:linear-gradient(90deg,rgba(255,201,40,.08),rgba(255,90,82,.06)); }
.promo-strip span { font-weight:700; font-size:.88rem; }
.menu-footer,.cart-total-card,.location-preview { display:flex; align-items:center; justify-content:space-between; gap:14px; border-radius:18px; border:1px solid rgba(255,201,40,.25); padding:18px 20px; margin:14px 0; background:linear-gradient(110deg,rgba(255,201,40,.11),rgba(255,255,255,.025)); }
.menu-footer strong,.cart-total-card strong { color:var(--gold); font-size:1.6rem; }
.cart-total-card { display:flex; flex-direction:column; align-items:flex-start; gap:5px; min-height:110px; }
.cart-total-card small { color:rgba(255,247,232,.62); }
.location-preview { justify-content:flex-start; margin-top:16px; }
.location-pin { font-size:2rem; }
.location-preview div { display:flex; flex-direction:column; gap:5px; }
.location-preview small { color:rgba(255,247,232,.65); }
.empty-state { text-align:center; border:1px dashed rgba(255,201,40,.35); border-radius:24px; padding:45px 22px; background:radial-gradient(circle at 50% 0%,rgba(255,201,40,.08),transparent 55%); animation:pageIn .5s ease both; }
.empty-emoji { font-size:3.4rem; }
.empty-state p { color:rgba(255,247,232,.65); }
.receipt-box { background:linear-gradient(145deg,rgba(255,255,255,.045),rgba(255,201,40,.045)); }
.app-footer { display:flex; flex-direction:column; gap:6px; text-align:center; padding:18px 8px; color:rgba(255,247,232,.65); }
.app-footer strong { color:var(--gold); font-size:1rem; }
.app-footer small { font-size:.75rem; }


.branch-home { background:radial-gradient(circle at 88% 22%,rgba(255,201,40,.19),transparent 28%),linear-gradient(125deg,#2b1b2e,#3b253e 60%,#201923); border-bottom:4px solid var(--gold); }
.branch-menu { background:radial-gradient(circle at 90% 10%,rgba(72,201,165,.18),transparent 30%),linear-gradient(125deg,#172a29,#263b37 58%,#211626); border-bottom:4px solid var(--mint); }
.branch-cart { background:radial-gradient(circle at 88% 15%,rgba(255,90,82,.2),transparent 30%),linear-gradient(125deg,#321f29,#402631 58%,#211626); border-bottom:4px solid var(--red); }
.branch-checkout { background:radial-gradient(circle at 90% 12%,rgba(255,201,40,.18),transparent 28%),linear-gradient(125deg,#292235,#292c3b 60%,#211626); border-bottom:4px solid var(--gold); }
.branch-location { background:radial-gradient(circle at 88% 18%,rgba(72,201,165,.18),transparent 28%),linear-gradient(125deg,#1c2c32,#263843 60%,#211626); border-bottom:4px solid var(--mint); }
.branch-my-orders { background:radial-gradient(circle at 88% 18%,rgba(255,90,82,.15),transparent 28%),linear-gradient(125deg,#302135,#3a2943 60%,#211626); border-bottom:4px solid var(--red); }

/* Auto-rotating homepage hero carousel (CSS only; no JavaScript or extra package). */
.hero-carousel { position:relative; height:320px; overflow:hidden; border-radius:24px; margin:18px 0 28px; border:1px solid rgba(255,255,255,.12); box-shadow:0 18px 48px rgba(0,0,0,.3); background:#211626; }
.hero-slide { position:absolute; inset:0; display:flex; align-items:flex-end; padding:clamp(22px,4vw,44px); background-size:cover; background-position:center; opacity:0; animation:heroRotate 18s infinite; }
.hero-slide:before { content:""; position:absolute; inset:0; background:linear-gradient(90deg,rgba(17,15,21,.93) 0%,rgba(17,15,21,.72) 42%,rgba(17,15,21,.12) 100%),linear-gradient(0deg,rgba(17,15,21,.45),transparent 60%); }
.hero-slide-content { position:relative; z-index:1; max-width:650px; }
.hero-slide-kicker { color:#ffc928; text-transform:uppercase; font-size:.78rem; font-weight:800; letter-spacing:.16em; margin-bottom:8px; }
.hero-slide-title { font-family:'Bricolage Grotesque',sans-serif; font-size:clamp(2rem,4.5vw,3.8rem); line-height:1; letter-spacing:-.04em; font-weight:800; color:#fff7e8; margin-bottom:10px; }
.hero-slide-copy { color:rgba(255,247,232,.88); font-size:1rem; max-width:520px; }
.hero-slide:nth-child(1) { animation-delay:0s; }
.hero-slide:nth-child(2) { animation-delay:6s; }
.hero-slide:nth-child(3) { animation-delay:12s; }
@keyframes heroRotate { 0%,29% { opacity:1; transform:scale(1); } 33%,96% { opacity:0; transform:scale(1.035); } 100% { opacity:1; transform:scale(1); } }
.crave-feature { border:1px solid rgba(255,201,40,.22); border-radius:18px; padding:17px; background:linear-gradient(135deg,rgba(255,201,40,.09),rgba(255,90,82,.045)); height:100%; }
.badge-unlocked { border:1px solid rgba(72,201,165,.3); border-radius:14px; padding:12px; background:rgba(72,201,165,.08); margin-bottom:8px; }
.badge-locked { border:1px dashed rgba(255,255,255,.18); border-radius:14px; padding:12px; opacity:.65; margin-bottom:8px; }
@media (prefers-reduced-motion: reduce) { .hero-slide { animation:none; } .hero-slide:nth-child(1) { opacity:1; } }
@media (max-width:700px) { .hero-carousel { height:300px; } .hero-slide { padding:22px; } }

/* Consistent image proportions across the restaurant discovery and menu screens. */
.restaurant-photo {
    display:block;
    width:100%;
    height:220px;
    object-fit:cover;
    object-position:center;
    border-radius:18px;
    margin:0 0 12px 0;
    border:1px solid rgba(255,255,255,.10);
    background:#211626;
}
/* Restaurant discovery images use a consistent landscape crop. Menu items intentionally use text-first cards. */
@media (max-width:700px) {
    .restaurant-photo { height:190px; }
}

/* Smart-cart recommendations and delivery progress */
.smart-pair { border:1px solid rgba(72,201,165,.28); border-radius:16px; padding:15px 18px; background:linear-gradient(110deg,rgba(72,201,165,.11),rgba(255,201,40,.045)); margin:10px 0; }
.smart-pair strong { color:#8ee6cc; }
.delivery-stage { border:1px solid rgba(255,201,40,.25); border-radius:18px; padding:20px; background:linear-gradient(135deg,rgba(255,201,40,.09),rgba(255,90,82,.06)); margin:12px 0; }
.food-badge { display:inline-block; padding:3px 9px; border-radius:999px; font-size:.75rem; font-weight:800; margin-top:4px; }
.food-badge.veg { color:#a9f0c0; background:rgba(44,165,94,.16); }
.food-badge.nonveg { color:#ffaaa6; background:rgba(255,90,82,.16); }
.food-photo { border-radius:14px; overflow:hidden; }
.menu-item-title { font-size:1.04rem; font-weight:800; letter-spacing:-.01em; }
.menu-item-desc { color:rgba(255,247,232,.72); font-size:.86rem; line-height:1.45; }
.menu-card-price { color:var(--gold); font-size:1.1rem; font-weight:800; }
.fav-button { border:1px solid rgba(255,90,82,.25); border-radius:999px; padding:4px 9px; }
.tile-photo-caption { color:rgba(255,247,232,.6); font-size:.74rem; }
.order-timeline { display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 16px; }
.order-timeline span { flex:1; min-width:130px; border:1px solid rgba(72,201,165,.24); border-radius:12px; padding:10px; background:rgba(72,201,165,.07); font-size:.82rem; }
@media (max-width:700px) { .branch-hero { padding:22px 18px; } .restaurant-tile { min-height:unset; } .menu-footer { align-items:flex-start; flex-direction:column; } }

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
            ("Dal Makhani", "Slow-cooked black lentils with butter", 190, True),
            ("Shahi Paneer", "Paneer in a rich cashew and tomato gravy", 230, True),
            ("Butter Chicken", "Tandoori chicken in a rich makhani gravy", 290, False),
            ("Chicken Biryani", "Fragrant dum biryani served with raita", 260, False),
            ("Veg Pulao", "Basmati rice with vegetables and whole spices", 170, True),
            ("Butter Naan", "Soft tandoor-baked naan brushed with butter", 45, True),
            ("Garlic Naan", "Tandoor naan with garlic and coriander", 60, True),
            ("Jeera Rice", "Steamed basmati rice tempered with cumin", 120, True),
            ("Paneer Tikka", "Tandoori paneer with peppers and chutney", 190, True),
            ("Hara Bhara Kebab", "Spinach and pea patties with mint chutney", 150, True),
            ("Gulab Jamun (2 pcs)", "Warm milk-solid dumplings in sugar syrup", 80, True),
            ("Masala Chaas", "Chilled spiced buttermilk", 55, True),
            ("Mango Lassi", "Thick yoghurt drink with mango", 95, True),
            ("Masala Chai", "Freshly brewed tea with milk and warming spices", 35, True),
            ("Adrak Chai", "Hot milk tea brewed with fresh ginger", 40, True),
        ],
    },
    {
        "name": "Burger Barn", "emoji": "🍔", "cuisine": "Burgers and Fries",
        "rating": 4.2, "prep": 18, "packaging": 10, "lat": 28.9480, "lon": 77.1010,
        "menu": [
            ("Classic Veg Burger", "Crispy veg patty, lettuce and house sauce", 99, True),
            ("Double Cheese Veg Burger", "Double patty with melted cheese", 149, True),
            ("Crispy Chicken Burger", "Crunchy chicken fillet with spicy mayo", 149, False),
            ("Smoky BBQ Chicken Burger", "Grilled chicken, BBQ sauce and onions", 179, False),
            ("Cheese Fries", "Golden fries loaded with cheese sauce", 109, True),
            ("Peri Peri Fries", "Crispy fries tossed in peri peri seasoning", 99, True),
            ("Chicken Wings (6 pcs)", "Wings tossed in smoky BBQ glaze", 179, False),
            ("Veg Nuggets (6 pcs)", "Crunchy vegetable bites with dip", 89, True),
            ("Onion Rings", "Crispy battered onion rings", 79, True),
            ("Chocolate Shake", "Thick chocolate milkshake", 119, True),
            ("Strawberry Shake", "Creamy strawberry milkshake", 119, True),
            ("Classic Lemonade", "Fresh lemon, mint and soda", 69, True),
            ("Brownie with Ice Cream", "Chocolate brownie with vanilla scoop", 129, True),
            ("Vanilla Soft Serve", "Classic creamy soft serve", 59, True),
        ],
    },
    {
        "name": "Pizza Piazza", "emoji": "🍕", "cuisine": "Italian",
        "rating": 4.4, "prep": 28, "packaging": 20, "lat": 28.9700, "lon": 77.0800,
        "menu": [
            ("Margherita Pizza", "Mozzarella, tomato sauce and basil", 199, True),
            ("Farmhouse Pizza", "Capsicum, onion, tomato and sweet corn", 299, True),
            ("Four Cheese Pizza", "A rich blend of four cheeses", 349, True),
            ("Pepperoni Pizza", "Classic pepperoni with mozzarella", 329, False),
            ("BBQ Chicken Pizza", "BBQ chicken, onion and smoky sauce", 349, False),
            ("Pasta Alfredo", "Penne in creamy white sauce", 219, True),
            ("Arrabbiata Pasta", "Penne in a spicy tomato sauce", 199, True),
            ("Garlic Bread", "Toasted bread with garlic butter", 119, True),
            ("Cheesy Garlic Bread", "Garlic bread topped with mozzarella", 149, True),
            ("Jalapeno Poppers", "Cheese-filled bites with jalapeno", 129, True),
            ("Classic Tiramisu Cup", "Coffee-soaked dessert with creamy layers", 149, True),
            ("Choco Lava Cake", "Warm chocolate cake with molten centre", 99, True),
            ("Iced Tea", "Chilled lemon iced tea", 79, True),
            ("Cold Coffee", "Chilled coffee blended with milk", 109, True),
        ],
    },
    {
        "name": "Dragon Wok", "emoji": "🥡", "cuisine": "Chinese and Indo-Chinese",
        "rating": 4.1, "prep": 22, "packaging": 15, "lat": 28.9560, "lon": 77.1100,
        "menu": [
            ("Veg Hakka Noodles", "Wok-tossed noodles with crunchy vegetables", 150, True),
            ("Chicken Hakka Noodles", "Wok noodles with chicken and spring onion", 190, False),
            ("Veg Fried Rice", "Wok-fried rice with vegetables", 145, True),
            ("Chicken Fried Rice", "Wok-fried rice with chicken and egg", 180, False),
            ("Veg Manchurian", "Crispy vegetable balls in tangy sauce", 160, True),
            ("Chilli Chicken", "Chicken tossed with chilli, peppers and onion", 220, False),
            ("Paneer Chilli", "Crispy paneer tossed in chilli sauce", 195, True),
            ("Veg Spring Rolls", "Crispy rolls filled with seasoned vegetables", 120, True),
            ("Chicken Momos (6 pcs)", "Steamed chicken dumplings with spicy chutney", 150, False),
            ("Veg Momos (6 pcs)", "Steamed vegetable dumplings with chutney", 120, True),
            ("Hot and Sour Soup", "Peppery soup with vegetables", 110, True),
            ("Sweet Corn Chicken Soup", "Comforting chicken and sweet corn soup", 130, False),
            ("Chilli Garlic Potatoes", "Crispy potatoes in chilli garlic sauce", 135, True),
            ("Classic Lemon Soda", "Fresh lemon soda, sweet or salted", 65, True),
        ],
    },
    {
        "name": "Green Bowl", "emoji": "🥗", "cuisine": "Healthy (Pure Veg)",
        "rating": 4.6, "prep": 15, "packaging": 12, "lat": 28.9520, "lon": 77.0990,
        "menu": [
            ("Quinoa Salad Bowl", "Quinoa, fresh vegetables and lemon dressing", 189, True),
            ("Paneer Wrap", "Grilled paneer in a whole-wheat wrap", 149, True),
            ("Mediterranean Chickpea Bowl", "Chickpeas, cucumber, tomato and herbs", 179, True),
            ("Grilled Paneer Protein Bowl", "Paneer, brown rice and seasonal greens", 219, True),
            ("Avocado Toast", "Multigrain toast with avocado and seeds", 199, True),
            ("Hummus Platter", "Hummus with pita and vegetable sticks", 169, True),
            ("Sweet Potato Wedges", "Oven-baked wedges with herb seasoning", 99, True),
            ("Corn and Spinach Soup", "Light soup with corn and spinach", 109, True),
            ("Fresh Fruit Bowl", "Seasonal fresh-cut fruits", 129, True),
            ("Greek Yoghurt Parfait", "Yoghurt, granola and seasonal fruit", 139, True),
            ("Chia Seed Pudding", "Chia soaked in milk with fruit", 119, True),
            ("Cold-Pressed Juice", "Fresh juice with no added sugar", 99, True),
            ("Oats Banana Smoothie", "Banana, oats and milk smoothie", 119, True),
            ("Mint Cucumber Cooler", "Refreshing cucumber, mint and lime", 89, True),
        ],
    },
    {
        "name": "Sunrise Breakfast Club", "emoji": "🍳", "cuisine": "All-day Breakfast · Indian & Global",
        "rating": 4.7, "prep": 16, "packaging": 12, "lat": 28.9550, "lon": 77.0930,
        "menu": [
            ("Chocos with Cold Milk", "Chocolate cereal served with chilled milk", 99, True),
            ("Classic Cornflakes Bowl", "Golden cornflakes with cold milk", 89, True),
            ("Honey Oats & Banana", "Rolled oats, banana and a touch of honey", 119, True),
            ("Butter Toast", "Toasted bread served with creamy butter", 59, True),
            ("Jam & Butter Toast", "Crisp toast with butter and fruit jam", 69, True),
            ("Grilled Veg Sandwich", "Toasted sandwich with vegetables and cheese", 119, True),
            ("Bombay Masala Sandwich", "Potato, cucumber, tomato and green chutney", 109, True),
            ("Egg and Cheese Sandwich", "Scrambled egg and cheese in toasted bread", 139, False),
            ("Idli Sambar (3 pcs)", "Soft steamed idlis with sambar and coconut chutney", 99, True),
            ("Masala Dosa", "Crisp dosa filled with spiced potato masala", 129, True),
            ("Plain Dosa", "Golden rice-and-lentil crepe with chutneys", 99, True),
            ("Medu Vada (2 pcs)", "Crispy lentil doughnuts with sambar", 89, True),
            ("Chole Bhature", "Fluffy bhature with spicy chickpea curry", 159, True),
            ("Aloo Paratha", "Stuffed potato paratha with curd and pickle", 119, True),
            ("Poha", "Light flattened rice with peanuts, curry leaves and lemon", 89, True),
            ("Vegetable Upma", "Comforting semolina breakfast with vegetables", 89, True),
            ("English Breakfast Plate", "Baked beans, toast, sautéed mushrooms and grilled tomato", 229, True),
            ("Pancakes with Maple Syrup", "Fluffy pancakes with maple syrup", 179, True),
            ("Waffles with Chocolate", "Golden waffles with chocolate sauce", 189, True),
            ("Butter Croissant", "Flaky, buttery French-style croissant", 99, True),
            ("Bagel with Cream Cheese", "Toasted bagel with smooth cream cheese", 149, True),
            ("Shakshuka with Toast", "Eggs poached in spiced tomato and pepper sauce", 199, False),
            ("Japanese Tamago Sandwich", "Soft milk bread with Japanese-style egg filling", 169, False),
            ("Breakfast Burrito", "Tortilla with scrambled egg, beans and cheese", 189, False),
            ("Greek Yoghurt Granola Bowl", "Greek yoghurt, crunchy granola and seasonal fruit", 149, True),
            ("Fresh Orange Juice", "Freshly squeezed orange juice", 99, True),
            ("Filter Coffee", "South Indian filter coffee with milk", 59, True),
            ("Masala Chai", "Indian milk tea brewed with warming spices", 35, True),
        ],
    },
]

# Categorise each dish into menu sections, as used by food-ordering apps.
# Unlisted items safely fall back to the closest general category.
MENU_CATEGORIES = {
    "Paneer Butter Masala": "Main Course", "Dal Makhani": "Main Course", "Shahi Paneer": "Main Course",
    "Butter Chicken": "Main Course", "Chicken Biryani": "Main Course", "Veg Pulao": "Main Course",
    "Jeera Rice": "Main Course", "Paneer Tikka": "Starters", "Hara Bhara Kebab": "Starters",
    "Butter Naan": "Sides & Breads", "Garlic Naan": "Sides & Breads", "Gulab Jamun (2 pcs)": "Desserts",
    "Masala Chaas": "Drinks", "Mango Lassi": "Drinks", "Masala Chai": "Drinks", "Adrak Chai": "Drinks",
    "Classic Veg Burger": "Burgers", "Double Cheese Veg Burger": "Burgers", "Crispy Chicken Burger": "Burgers",
    "Smoky BBQ Chicken Burger": "Burgers", "Cheese Fries": "Sides", "Peri Peri Fries": "Sides",
    "Chicken Wings (6 pcs)": "Starters", "Veg Nuggets (6 pcs)": "Starters", "Onion Rings": "Sides",
    "Chocolate Shake": "Drinks", "Strawberry Shake": "Drinks", "Classic Lemonade": "Drinks",
    "Brownie with Ice Cream": "Desserts", "Vanilla Soft Serve": "Desserts",
    "Margherita Pizza": "Pizza", "Farmhouse Pizza": "Pizza", "Four Cheese Pizza": "Pizza",
    "Pepperoni Pizza": "Pizza", "BBQ Chicken Pizza": "Pizza", "Pasta Alfredo": "Pasta",
    "Arrabbiata Pasta": "Pasta", "Garlic Bread": "Sides", "Cheesy Garlic Bread": "Sides",
    "Jalapeno Poppers": "Starters", "Classic Tiramisu Cup": "Desserts", "Choco Lava Cake": "Desserts",
    "Iced Tea": "Drinks", "Cold Coffee": "Drinks",
    "Veg Hakka Noodles": "Noodles & Rice", "Chicken Hakka Noodles": "Noodles & Rice", "Veg Fried Rice": "Noodles & Rice",
    "Chicken Fried Rice": "Noodles & Rice", "Veg Manchurian": "Starters", "Chilli Chicken": "Starters",
    "Paneer Chilli": "Starters", "Veg Spring Rolls": "Starters", "Chicken Momos (6 pcs)": "Starters",
    "Veg Momos (6 pcs)": "Starters", "Hot and Sour Soup": "Soups", "Sweet Corn Chicken Soup": "Soups",
    "Chilli Garlic Potatoes": "Sides", "Classic Lemon Soda": "Drinks",
    "Quinoa Salad Bowl": "Bowls & Mains", "Paneer Wrap": "Wraps", "Mediterranean Chickpea Bowl": "Bowls & Mains",
    "Grilled Paneer Protein Bowl": "Bowls & Mains", "Avocado Toast": "Starters & Light Bites",
    "Hummus Platter": "Sides & Light Bites", "Sweet Potato Wedges": "Sides & Light Bites",
    "Corn and Spinach Soup": "Soups", "Fresh Fruit Bowl": "Desserts & Fruit", "Greek Yoghurt Parfait": "Desserts & Fruit",
    "Chia Seed Pudding": "Desserts & Fruit", "Cold-Pressed Juice": "Drinks", "Oats Banana Smoothie": "Drinks",
    "Mint Cucumber Cooler": "Drinks",
    "Chocos with Cold Milk": "Cereals & Bowls", "Classic Cornflakes Bowl": "Cereals & Bowls",
    "Honey Oats & Banana": "Cereals & Bowls", "Greek Yoghurt Granola Bowl": "Cereals & Bowls",
    "Butter Toast": "Toast & Sandwiches", "Jam & Butter Toast": "Toast & Sandwiches",
    "Grilled Veg Sandwich": "Toast & Sandwiches", "Bombay Masala Sandwich": "Toast & Sandwiches",
    "Egg and Cheese Sandwich": "Toast & Sandwiches", "Bagel with Cream Cheese": "Toast & Sandwiches",
    "Idli Sambar (3 pcs)": "South Indian", "Masala Dosa": "South Indian",
    "Plain Dosa": "South Indian", "Medu Vada (2 pcs)": "South Indian",
    "Chole Bhature": "Indian Breakfast", "Aloo Paratha": "Indian Breakfast",
    "Poha": "Indian Breakfast", "Vegetable Upma": "Indian Breakfast",
    "English Breakfast Plate": "Global Breakfast", "Pancakes with Maple Syrup": "Global Breakfast",
    "Waffles with Chocolate": "Global Breakfast", "Butter Croissant": "Global Breakfast",
    "Shakshuka with Toast": "Global Breakfast", "Japanese Tamago Sandwich": "Global Breakfast",
    "Breakfast Burrito": "Global Breakfast", "Fresh Orange Juice": "Drinks",
    "Filter Coffee": "Drinks",
}

# Carefully chosen illustrative food photos: overhead for pizza/salads, front-on
# for burgers, and three-quarter views for curries, noodles and plated mains.
# Images are illustrative category visuals, not claims that they show the exact dish.
RESTAURANT_PHOTOS = {
    "Spice Route Kitchen": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=1200&q=85",
    "Burger Barn": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1200&q=85",
    "Pizza Piazza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=85",
    "Dragon Wok": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=1200&q=85",
    "Green Bowl": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=85",
    "Sunrise Breakfast Club": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?auto=format&fit=crop&w=1200&q=85",
}
MENU_PHOTOS = {
    "Main Course": RESTAURANT_PHOTOS["Spice Route Kitchen"], "Starters": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80",
    "Sides & Breads": "https://images.unsplash.com/photo-1619158401201-8fa932741a0a?auto=format&fit=crop&w=600&q=80",
    "Drinks": "https://images.unsplash.com/photo-1513558161293-c37a6079382d?auto=format&fit=crop&w=600&q=80",
    "Desserts": "https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=600&q=80",
    "Burgers": RESTAURANT_PHOTOS["Burger Barn"], "Sides": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=600&q=80",
    "Pizza": RESTAURANT_PHOTOS["Pizza Piazza"], "Pasta": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=600&q=80",
    "Noodles & Rice": RESTAURANT_PHOTOS["Dragon Wok"], "Soups": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=600&q=80",
    "Bowls & Mains": RESTAURANT_PHOTOS["Green Bowl"], "Wraps": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?auto=format&fit=crop&w=600&q=80",
    "Starters & Light Bites": RESTAURANT_PHOTOS["Green Bowl"], "Sides & Light Bites": RESTAURANT_PHOTOS["Green Bowl"],
    "Desserts & Fruit": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=600&q=80",
}

# Coupons: type, value, maximum discount, minimum order and description
COUPONS = {
    "WELCOME50": {"type": "percent", "value": 50, "cap": 100, "min": 199,
                  "desc": "50% off up to ₹100 on orders of ₹199 or more"},
    "FOODIE20": {"type": "percent", "value": 20, "cap": 80, "min": 299,
                 "desc": "20% off up to ₹80 on orders of ₹299 or more"},
    "FREEDEL": {"type": "freedel", "value": 0, "cap": 0, "min": 149,
                "desc": "Free delivery on orders of ₹149 or more"},
    "PRAMODSIRPRO": {"type": "percent", "value": 15, "cap": 75, "min": 249,
                  "desc": "Pramod Sir's Python Perk: 15% off up to ₹75 on orders of ₹249 or more"},
    "SIRPLS": {"type": "percent", "value": 10, "cap": 50, "min": 199,
               "desc": "Sir, Please Save My GPA: 10% off up to ₹50 on orders of ₹199 or more"},
    "PASSKARADO": {"type": "percent", "value": 15, "cap": 60, "min": 299,
                   "desc": "Pass Karado, Sir: 15% off up to ₹60 on orders of ₹299 or more"},
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
    """Validate a coupon and return (discount, delivery fee, message, validity).

    Normalising the code here as well as in the text box makes this helper safer
    if it is reused elsewhere in the app.
    """
    code = code.strip().upper()
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
# 4. APP STATE, NAVIGATION, LOCATION, AND ORDER HISTORY
# ---------------------------------------------------------------------------
from datetime import datetime

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
if "my_orders" not in st.session_state:
    st.session_state.my_orders = []
if "favourites" not in st.session_state:
    st.session_state.favourites = []
if "customer_name" not in st.session_state:
    st.session_state.customer_name = ""
if "customer_phone" not in st.session_state:
    st.session_state.customer_phone = ""
if "delivery_location" not in st.session_state:
    st.session_state.delivery_location = DEFAULT_LOCATION
if "delivery_lat" not in st.session_state:
    st.session_state.delivery_lat = PRESET_LOCATIONS[DEFAULT_LOCATION][0]
if "delivery_lon" not in st.session_state:
    st.session_state.delivery_lon = PRESET_LOCATIONS[DEFAULT_LOCATION][1]
if "location_mode" not in st.session_state:
    st.session_state.location_mode = "Choose an area"

# First visit: the full-screen brand introduction.
if not st.session_state.entered_app:
    # Each slide has its own original campaign-style gradient, emoji art, and cheeky headline.
    # The Home page carousel below is intentionally unchanged.
    welcome_slides = [
        ("🍔", "ATTENTION, HUNGRY HUMAN", "Your stomach called.<br><span>We picked up.</span>", "Your 2 AM cravings have excellent taste. Your attendance? Let's not talk about it."),
        ("🍟", "HOSTEL LIFE, BUT MAKE IT TASTY", "Mess food again?<br><span>That's a plot twist.</span>", "When the mess menu says surprise, we say order something you actually want."),
        ("🍕", "ACADEMIC PRESSURE? MEET CHEESE.", "Deadlines can wait.<br><span>Pizza can't.</span>", "One more assignment, one more slice. We're not saying food solves everything… but have you tried garlic bread?"),
    ]
    welcome_html = '<div class="landing-screen"><div class="welcome-carousel" aria-label="Three colourful welcome campaigns rotating automatically">'
    for sticker, kicker, title, copy in welcome_slides:
        welcome_html += f'<div class="welcome-slide"><div class="welcome-sticker">{sticker}</div></div>'
    welcome_html += '</div><div class="brand-mark">🍜</div>'
    for index, (sticker, kicker, title, copy) in enumerate(welcome_slides):
        welcome_html += f'<div class="welcome-copy welcome-copy-{index+1}"><div class="landing-kicker">{kicker}</div><div class="landing-title">{title}</div><div class="landing-copy">{copy}</div></div>'
    welcome_html += '<div class="landing-perks"><span><span class="perk-icon">✦</span>Local favourites</span><span><span class="perk-icon">⚡</span>Quick delivery</span><span><span class="perk-icon">₹</span>Easy-on-pocket picks</span></div><div class="landing-footer">MADE FOR YOUR CRAVINGS · SONIPAT, HARYANA</div></div>'
    st.markdown(welcome_html, unsafe_allow_html=True)
    if st.button("Explore restaurants  →", type="primary", use_container_width=True, key="enter_ordering_app"):
        st.session_state.entered_app = True
        st.session_state.page = "Home"
        st.rerun()
    st.stop()


def go_to(page_name):
    """Change the current screen without changing the state of a rendered widget."""
    st.session_state.page = page_name
    st.rerun()


def cart_count():
    return sum(st.session_state.cart.values())


def active_restaurant():
    return next(
        (r for r in RESTAURANTS if r["name"] == st.session_state.selected),
        RESTAURANTS[0],
    )


def cart_item_total():
    r = active_restaurant()
    return sum(
        quantity * item[2]
        for item in r["menu"]
        for quantity in [st.session_state.cart.get(item[0], 0)]
    )


def smart_pairing_items(restaurant):
    """Suggest a familiar side based on items already in the current cart."""
    pairings = {
        "Paneer Butter Masala": ["Butter Naan", "Jeera Rice"],
        "Butter Chicken": ["Butter Naan", "Jeera Rice"],
        "Classic Veg Burger": ["Cheese Fries", "Peri Peri Fries"],
        "Crispy Chicken Burger": ["Cheese Fries", "Peri Peri Fries"],
        "Margherita Pizza": ["Garlic Bread", "Choco Lava Cake"],
        "Farmhouse Pizza": ["Garlic Bread", "Choco Lava Cake"],
        "Veg Hakka Noodles": ["Veg Spring Rolls", "Hot and Sour Soup"],
        "Chicken Fried Rice": ["Veg Spring Rolls", "Hot and Sour Soup"],
        "Paneer Wrap": ["Fresh Fruit Bowl", "Cold-Pressed Juice"],
        "Masala Chai": ["Hara Bhara Kebab", "Gulab Jamun (2 pcs)"],
        "Adrak Chai": ["Hara Bhara Kebab", "Gulab Jamun (2 pcs)"],
        "Chocos with Cold Milk": ["Butter Toast", "Fresh Orange Juice"],
        "Masala Dosa": ["Filter Coffee", "Medu Vada (2 pcs)"],
        "Chole Bhature": ["Fresh Orange Juice", "Masala Chai"],
        "Pancakes with Maple Syrup": ["Fresh Orange Juice", "Filter Coffee"],
    }
    menu_names = [item[0] for item in restaurant["menu"]]
    cart_names = [name for name, qty in st.session_state.cart.items() if qty > 0]
    suggestions = []
    for cart_name in cart_names:
        for suggestion in pairings.get(cart_name, []):
            if suggestion in menu_names and suggestion not in cart_names and suggestion not in suggestions:
                suggestions.append(suggestion)
    if not suggestions:
        suggestions = [name for name in menu_names if name not in cart_names]
    return suggestions[:2]


def render_smart_cart(restaurant, key_prefix):
    """Show menu-based pairings and the configured free-delivery milestone."""
    if not st.session_state.cart:
        return
    item_total = cart_item_total()
    if item_total < FREE_DELIVERY_ABOVE:
        remaining = FREE_DELIVERY_ABOVE - item_total
        st.info(f"🚚 Add {inr(remaining)} more to unlock free delivery on orders of {inr(FREE_DELIVERY_ABOVE)} or more!")
        st.progress(min(item_total / FREE_DELIVERY_ABOVE, 1.0), text=f"{inr(item_total)} of {inr(FREE_DELIVERY_ABOVE)} toward free delivery")
    else:
        st.success(f"🎉 You've unlocked free delivery! Your food subtotal is {inr(item_total)}.")
    suggestions = smart_pairing_items(restaurant)
    if suggestions:
        st.markdown("### ✨ Goes great with your order")
        for suggestion in suggestions:
            menu_item = next((item for item in restaurant["menu"] if item[0] == suggestion), None)
            if menu_item:
                item_name, description, price, is_veg = menu_item
                with st.container(border=True):
                    item_col, price_col, add_col = st.columns([3, 1, 1.25])
                    item_col.markdown(f"**{'🟢' if is_veg else '🔴'} {item_name}**")
                    item_col.caption(description)
                    price_col.markdown(f"**{inr(price)}**")
                    if add_col.button("+ Add", key=f"{key_prefix}_{item_name}", use_container_width=True):
                        st.session_state.cart[item_name] = st.session_state.cart.get(item_name, 0) + 1
                        st.rerun()


def set_restaurant(name):
    """Keep one restaurant per cart so prices and menu items stay consistent."""
    if st.session_state.selected != name:
        st.session_state.cart = {}
    st.session_state.selected = name


# Navigation and location controls are buttons rather than a state-controlled
# radio widget. This avoids Streamlit's "widget already instantiated" error.
st.sidebar.markdown("### 🍜 ChaiTapri Eats")
st.sidebar.caption("Your campus food companion")
sidebar_pages = [
    ("🏠", "Home"),
    ("🧭", "Crave Club"),
    ("🍽️", "Menu"),
    ("🛒", "Cart"),
    ("💳", "Checkout"),
    ("📦", "My Orders"),
    ("📍", "Location"),
]
for nav_icon, nav_page in sidebar_pages:
    is_current = st.session_state.page == nav_page
    if st.sidebar.button(
        f"{'● ' if is_current else ''}{nav_icon}  {nav_page}",
        key=f"sidebar_nav_{nav_page}",
        use_container_width=True,
        type="primary" if is_current else "secondary",
    ):
        go_to(nav_page)

if st.sidebar.button("↩ Welcome screen", key="back_to_welcome", use_container_width=True):
    st.session_state.entered_app = False
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("### 📍 Delivery location")
st.sidebar.write(st.session_state.delivery_location)
if st.sidebar.button("Change location →", key="sidebar_change_location", use_container_width=True):
    go_to("Location")
st.sidebar.caption(f"Items in cart: {cart_count()}")

# Calculate distance and delivery estimates using the currently saved location.
user_lat = st.session_state.delivery_lat
user_lon = st.session_state.delivery_lon
location_label = st.session_state.delivery_location
for r in RESTAURANTS:
    r["distance"] = road_distance_km(user_lat, user_lon, r["lat"], r["lon"])
    r["eta"] = estimate_eta(r["prep"], r["distance"], False)
    r["deliverable"] = r["distance"] <= MAX_DELIVERY_KM

ordered = sorted(RESTAURANTS, key=lambda r: r["distance"])
restaurant = active_restaurant()


def shared_header(kicker, title, description, emoji):
    st.markdown(
        f"""
        <div class="branch-hero branch-{st.session_state.page.lower().replace(" ", "-")}">
          <div class="branch-kicker">{emoji} {kicker}</div>
          <div class="branch-title">{title}</div>
          <div class="branch-description">{description}</div>
          <div class="branch-meta"><span>📍 {location_label}</span><span>🛒 {cart_count()} items in cart</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_bill_rows(bill, menu_items, cart, include_tip=True):
    """Build an itemised receipt using the same bill calculation as checkout."""
    rows = ""
    for item_name, description, price, is_veg in menu_items:
        qty = cart.get(item_name, 0)
        if qty > 0:
            rows += (
                f'<div class="bill-row"><span>{qty} × {item_name}</span>'
                f'<span>{inr(qty * price)}</span></div>'
            )
    rows += f'<div class="bill-row"><span>Food subtotal</span><span>{inr(bill["item_total"])}</span></div>'
    if bill["discount"] > 0:
        rows += f'<div class="bill-row saving"><span>Coupon savings</span><span>− {inr(bill["discount"])}</span></div>'
    rows += f'<div class="bill-row"><span>Delivery fee</span><span>{"FREE" if bill["delivery_fee"] == 0 else inr(bill["delivery_fee"])}</span></div>'
    if bill["express_fee"] > 0:
        rows += f'<div class="bill-row"><span>Express delivery</span><span>{inr(bill["express_fee"])}</span></div>'
    rows += f'<div class="bill-row"><span>Packaging</span><span>{inr(bill["packaging"])}</span></div>'
    rows += f'<div class="bill-row"><span>Platform fee</span><span>{inr(bill["platform_fee"])}</span></div>'
    rows += f'<div class="bill-row"><span>GST (5%)</span><span>{inr(bill["gst"])}</span></div>'
    if include_tip and bill["tip"] > 0:
        rows += f'<div class="bill-row"><span>Delivery partner tip</span><span>{inr(bill["tip"])}</span></div>'
    rows += f'<div class="bill-total"><span>Total</span><span>{inr(bill["total"])}</span></div>'
    return rows


# A slim top navigation bar gives each branch a consistent way to move around.
top_cols = st.columns(len(sidebar_pages))
for col, (nav_icon, nav_page) in zip(top_cols, sidebar_pages):
    if col.button(
        f"{nav_icon} {nav_page}" + (f" ({len(st.session_state.my_orders)})" if nav_page == "My Orders" else ""),
        key=f"top_nav_{nav_page}",
        use_container_width=True,
        type="primary" if st.session_state.page == nav_page else "secondary",
    ):
        go_to(nav_page)

st.divider()

# ---------------------------------------------------------------------------
# HOME: restaurant discovery, filters, and food-first cards
# ---------------------------------------------------------------------------
if st.session_state.page == "Home":
    shared_header(
        "DISCOVER YOUR NEXT FAVOURITE",
        "What are we craving today?",
        "Explore campus favourites, compare delivery times, and find something worth looking forward to.",
        "✨",
    )
    # Three-slide automatic carousel: CSS handles the rotation without extra packages.
    carousel_slides = [
        (RESTAURANT_PHOTOS["Sunrise Breakfast Club"], "BREAKFAST, YOUR WAY", "Start the day on a delicious note.", "From chocos and toast to dosa, chole bhature and pancakes."),
        (RESTAURANT_PHOTOS["Spice Route Kitchen"], "COMFORT FOOD CALLING", "Big cravings deserve big flavours.", "Find North Indian favourites, sizzling sides and sweet endings."),
        (RESTAURANT_PHOTOS["Pizza Piazza"], "MAKE TONIGHT A TREAT", "Pizza night is always a good idea.", "Explore pizzas, pasta and sides — then build your perfect order."),
    ]
    slide_html = '<div class="hero-carousel" aria-label="Featured food slides rotating automatically">'
    for photo_url, kicker, title, copy in carousel_slides:
        slide_html += f"""<div class=\"hero-slide\" style=\"background-image:url('{photo_url}')\"><div class=\"hero-slide-content\"><div class=\"hero-slide-kicker\">{kicker}</div><div class=\"hero-slide-title\">{title}</div><div class=\"hero-slide-copy\">{copy}</div></div></div>"""
    slide_html += '</div>'
    st.markdown(slide_html, unsafe_allow_html=True)
    cta_left, cta_right = st.columns([1, 2])
    with cta_left:
        if st.button("🧭 Find my next meal", type="primary", use_container_width=True, key="hero_crave_club"):
            go_to("Crave Club")
    with cta_right:
        st.caption("The featured slides rotate automatically every six seconds. Restaurant images are illustrative; delivery details are simulated.")
    filter_a, filter_b, filter_c = st.columns([1.2, 1.2, 1.6])
    with filter_a:
        veg_only = st.checkbox("🌱 Vegetarian options", key="home_veg_filter")
    with filter_b:
        sort_by = st.selectbox("Sort by", ["Nearest first", "Top rated", "Fastest delivery"], key="home_sort")
    with filter_c:
        restaurant_search = st.text_input("Find a restaurant", placeholder="Try breakfast, pizza, Indian, healthy…", key="home_restaurant_search")
    visible_restaurants = list(RESTAURANTS)
    if restaurant_search.strip():
        visible_restaurants = [r for r in visible_restaurants if restaurant_search.lower() in (r["name"] + " " + r["cuisine"]).lower()]

    if sort_by == "Top rated":
        visible_restaurants = sorted(visible_restaurants, key=lambda r: r["rating"], reverse=True)
    elif sort_by == "Fastest delivery":
        visible_restaurants = sorted(visible_restaurants, key=lambda r: r["eta"])
    else:
        visible_restaurants = sorted(visible_restaurants, key=lambda r: r["distance"])

    st.markdown('<div class="section-title">Made for your cravings</div>', unsafe_allow_html=True)
    card_columns = st.columns(3)
    for i, r in enumerate(visible_restaurants):
        with card_columns[i % 3]:
            status = f"{r['eta']} min" if r["deliverable"] else "Out of range"
            st.markdown(
                f'<img class="restaurant-photo" src="{RESTAURANT_PHOTOS[r["name"]]}" alt="Food from {r["name"]}" loading="lazy">',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="restaurant-tile">
                  <div class="tile-emoji">{r['emoji']}</div>
                  <div class="tile-cuisine">{r['cuisine']}</div>
                  <div class="tile-name">{r['name']}</div>
                  <div class="tile-stats"><span>★ {r['rating']}</span><span>⌁ {r['distance']:.1f} km</span></div>
                  <div class="tile-status">{'⚡' if r['deliverable'] else '📍'} {status} delivery</div>
                  <div class="tile-photo-caption">{'Free delivery above ₹499' if r['deliverable'] else 'Change location to order'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            menu_veg = any(item[3] for item in r["menu"])
            if not veg_only or menu_veg:
                if st.button("Explore menu  →", key=f"home_{r['name']}", use_container_width=True):
                    set_restaurant(r["name"])
                    go_to("Menu")

    with st.expander("🗺️ View restaurant locations"):
        map_rows = [{"lat": user_lat, "lon": user_lon, "color": "#ffc928", "size": 140}]
        for r in RESTAURANTS:
            map_rows.append({"lat": r["lat"], "lon": r["lon"], "color": "#ff5a52", "size": 90})
        st.map(pd.DataFrame(map_rows), latitude="lat", longitude="lon", color="color", size="size")
        st.caption("Gold dot: your saved delivery location. Red dots: demo restaurants.")

    st.markdown(
        '<div class="promo-strip"><span>🍳 Breakfast to dinner</span><span>⚡ Fast delivery estimates</span><span>💛 Easy-to-understand bills</span></div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# CRAVE CLUB: discovery, budget mode, meal builder, breakfast passport, group split
# ---------------------------------------------------------------------------
elif st.session_state.page == "Crave Club":
    shared_header(
        "CHAI TAPI CRAVE CLUB",
        "Your hunger. Your budget. Your rules.",
        "Discover meals, build a combo, explore breakfast traditions and split a group bill — all using simple, transparent rules.",
        "🧭",
    )
    feature_tabs = st.tabs(["🧭 Crave Compass", "💸 Hostel Survival", "🥪 Build a Meal", "🍳 Breakfast Passport", "👥 Group Feast", "🏅 Rewards"])

    # 1. Crave Compass: transparent recommendation logic based on actual menu data.
    with feature_tabs[0]:
        st.markdown("### Find something that fits your mood")
        a, b, c = st.columns(3)
        with a:
            craving = st.selectbox("What are you craving?", ["Anything", "Spicy", "Comfort food", "Light & fresh", "Cheesy", "Breakfast", "Sweet treat"], key="crave_mood")
        with b:
            max_price = st.slider("Maximum price per dish (₹)", 50, 600, 200, 25, key="crave_budget")
        with c:
            veg_pref = st.selectbox("Food preference", ["Any", "Vegetarian only", "Non-vegetarian only"], key="crave_veg")
        keywords = {
            "Spicy": ["spicy", "chilli", "chili", "peri peri", "masala", "arrabbiata", "hot and sour", "peppery"],
            "Comfort food": ["butter", "creamy", "cheese", "naan", "rice", "pasta", "burger", "pancake", "toast", "dal"],
            "Light & fresh": ["salad", "fresh", "fruit", "quinoa", "yoghurt", "juice", "oats", "cucumber", "chickpea"],
            "Cheesy": ["cheese", "cheesy", "mozzarella", "alfredo", "paneer"],
            "Breakfast": ["breakfast", "toast", "cereal", "chocos", "cornflakes", "oats", "dosa", "idli", "paratha", "poha", "upma", "pancake", "waffle", "croissant", "egg", "sandwich", "chole bhature"],
            "Sweet treat": ["chocolate", "dessert", "jam", "gulab", "brownie", "cake", "tiramisu", "waffle", "pancake", "croissant", "mango", "strawberry", "ice cream"],
        }
        matches = []
        for rest in RESTAURANTS:
            for dish in rest["menu"]:
                name, desc, price, is_veg = dish
                text_blob = (name + " " + desc).lower()
                if price > max_price:
                    continue
                if veg_pref == "Vegetarian only" and not is_veg:
                    continue
                if veg_pref == "Non-vegetarian only" and is_veg:
                    continue
                if craving != "Anything" and not any(word in text_blob for word in keywords[craving]):
                    continue
                matches.append((rest, dish))
        matches.sort(key=lambda pair: (pair[1][2], -pair[0]["rating"]))
        st.caption("Recommendations are matched against real menu names, descriptions, prices and vegetarian labels — not generated by an AI model.")
        if matches:
            for idx, (rest, dish) in enumerate(matches[:6]):
                name, desc, price, is_veg = dish
                with st.container(border=True):
                    item_col, price_col, action_col = st.columns([3, 1, 1.25], vertical_alignment="center")
                    item_col.markdown(f"**{rest['emoji']} {name}**")
                    item_col.caption(f"{rest['name']} · {'Vegetarian' if is_veg else 'Non-vegetarian'} · ★ {rest['rating']}")
                    item_col.write(desc)
                    price_col.markdown(f"### {inr(price)}")
                    if action_col.button("Add this", key=f"crave_add_{idx}_{name}", use_container_width=True, disabled=not rest["deliverable"]):
                        if st.session_state.selected != rest["name"]:
                            st.session_state.cart = {}
                        st.session_state.selected = rest["name"]
                        st.session_state.cart[name] = st.session_state.cart.get(name, 0) + 1
                        st.session_state.page = "Cart"
                        st.rerun()
        else:
            st.info("No dishes match every filter. Try increasing your budget or choosing a different craving.")

    # 2. Budget mode: builds small two-item combos within the selected cap.
    with feature_tabs[1]:
        st.markdown("### Hostel Survival Mode")
        st.write("Pick a budget and we'll find a small combo that fits. Prices are for food items only; delivery and taxes appear at checkout.")
        budget = st.slider("My total food budget (₹)", 100, 600, 200, 25, key="hostel_budget")
        veg_budget = st.checkbox("Vegetarian combos only", value=True, key="hostel_veg")
        combos = []
        for rest in RESTAURANTS:
            available = [d for d in rest["menu"] if (d[3] or not veg_budget)]
            for i in range(len(available)):
                for j in range(i + 1, len(available)):
                    combo_total = available[i][2] + available[j][2]
                    if combo_total <= budget:
                        combos.append((combo_total, rest, available[i], available[j]))
        combos.sort(key=lambda x: (abs(budget - x[0]), -x[1]["rating"]))
        if combos:
            for idx, (total, rest, first, second) in enumerate(combos[:5]):
                with st.container(border=True):
                    left, right = st.columns([3, 1])
                    left.markdown(f"**{rest['emoji']} {first[0]} + {second[0]}**")
                    left.caption(f"{rest['name']} · Leaves {inr(budget-total)} from your food budget")
                    right.markdown(f"### {inr(total)}")
                    if left.button("Add this budget combo", key=f"budget_combo_{idx}", use_container_width=True, disabled=not rest["deliverable"]):
                        if st.session_state.selected != rest["name"]:
                            st.session_state.cart = {}
                        st.session_state.selected = rest["name"]
                        st.session_state.cart[first[0]] = st.session_state.cart.get(first[0], 0) + 1
                        st.session_state.cart[second[0]] = st.session_state.cart.get(second[0], 0) + 1
                        st.session_state.page = "Cart"
                        st.rerun()
        else:
            st.info("No two-item combo fits this budget yet. Increase the budget a little.")

    # 3. Build a meal: add-ons are existing menu items, so the cart and bill stay accurate.
    with feature_tabs[2]:
        st.markdown("### Build Your Perfect Meal")
        rest_name = st.selectbox("Choose a restaurant", [r["name"] for r in RESTAURANTS], key="builder_restaurant")
        rest = next(r for r in RESTAURANTS if r["name"] == rest_name)
        menu = rest["menu"]
        base_names = [d[0] for d in menu]
        base_name = st.selectbox("Choose your main item", base_names, key="builder_main")
        base_item = next(d for d in menu if d[0] == base_name)
        add_on_options = [d[0] for d in menu if d[0] != base_name]
        add_ons = st.multiselect("Add up to two sides, drinks or treats", add_on_options, max_selections=2, key="builder_addons")
        item_lookup = {d[0]: d for d in menu}
        combo_total = base_item[2] + sum(item_lookup[n][2] for n in add_ons)
        st.markdown(f'<div class="menu-footer"><span>Your custom meal · {1+len(add_ons)} item(s)</span><strong>{inr(combo_total)}</strong></div>', unsafe_allow_html=True)
        st.caption("To keep the bill accurate, each chosen add-on is an existing item from the same restaurant menu.")
        if st.button("Add my perfect meal to cart →", type="primary", use_container_width=True, disabled=not rest["deliverable"], key="builder_add_cart"):
            if st.session_state.selected != rest_name:
                st.session_state.cart = {}
            st.session_state.selected = rest_name
            for n in [base_name] + add_ons:
                st.session_state.cart[n] = st.session_state.cart.get(n, 0) + 1
            st.session_state.page = "Cart"
            st.rerun()

    # 4. Breakfast Passport: curated exploration of the all-day breakfast menu.
    with feature_tabs[3]:
        st.markdown("### Breakfast Passport")
        breakfast_rest = next(r for r in RESTAURANTS if r["name"] == "Sunrise Breakfast Club")
        passport_categories = ["All breakfasts", "Cereals & Bowls", "Toast & Sandwiches", "South Indian", "Indian Breakfast", "Global Breakfast"]
        passport_category = st.selectbox("Choose a breakfast tradition", passport_categories, key="passport_category")
        breakfast_items = [d for d in breakfast_rest["menu"] if MENU_CATEGORIES.get(d[0], "") in (passport_categories[1:] if passport_category == "All breakfasts" else [passport_category])]
        if breakfast_items:
            st.caption(f"{len(breakfast_items)} choices in this collection. Pick a dish to learn about and add to your order.")
            selected_breakfast = st.selectbox("Explore a dish", [d[0] for d in breakfast_items], key="passport_dish")
            breakfast = next(d for d in breakfast_items if d[0] == selected_breakfast)
            st.markdown(f"**{breakfast[0]} · {inr(breakfast[2])}**")
            st.write(breakfast[1])
            if st.button("Add breakfast to cart", type="primary", use_container_width=True, disabled=not breakfast_rest["deliverable"], key="passport_add"):
                if st.session_state.selected != breakfast_rest["name"]:
                    st.session_state.cart = {}
                st.session_state.selected = breakfast_rest["name"]
                st.session_state.cart[breakfast[0]] = st.session_state.cart.get(breakfast[0], 0) + 1
                st.session_state.page = "Cart"
                st.rerun()
            if st.button("🎲 Surprise me with a breakfast", use_container_width=True, key="passport_surprise"):
                st.session_state.passport_surprise = random.choice(breakfast_items)[0]
                st.rerun()
            if st.session_state.get("passport_surprise"):
                surprise = next((d for d in breakfast_rest["menu"] if d[0] == st.session_state.passport_surprise), None)
                if surprise:
                    st.info(f"Today's breakfast surprise: **{surprise[0]}** — {inr(surprise[2])}. {surprise[1]}")

    # 5. Group Feast: useful bill-splitting calculator, with optional live cart subtotal.
    with feature_tabs[4]:
        st.markdown("### Group Feast")
        st.write("Planning a group order? Estimate what each person would pay. This is a demo calculator; it does not create separate accounts.")
        current_subtotal = cart_item_total()
        use_cart_total = st.checkbox("Use my current cart subtotal", value=bool(st.session_state.cart), key="group_use_cart")
        amount = current_subtotal if use_cart_total else st.number_input("Total bill to split (₹)", min_value=0.0, max_value=100000.0, value=500.0, step=50.0, key="group_manual_amount")
        people = st.number_input("Number of people", min_value=2, max_value=30, value=4, step=1, key="group_people")
        shares = round(float(amount) / int(people), 2)
        st.markdown(f'<div class="menu-footer"><span>Each person pays (equal split)</span><strong>{inr(shares)}</strong></div>', unsafe_allow_html=True)
        st.caption("This splits the entered amount equally. Checkout fees and delivery charges are included only if you enter a full bill total.")

    # 6. Rewards: achievements based on completed demo orders in this session.
    with feature_tabs[5]:
        st.markdown("### ChaiTapri Passport & Rewards")
        orders = st.session_state.my_orders
        unique_restaurants = {o.get("restaurant") for o in orders}
        total_orders = len(orders)
        breakfast_orders = sum(1 for o in orders if o.get("restaurant") == "Sunrise Breakfast Club")
        cuisine_count = len({o.get("cuisine") for o in orders})
        total_spend = sum(float(o.get("total", 0)) for o in orders)
        reward_rules = [
            ("First Bite", "Place your first demo order", total_orders >= 1),
            ("Breakfast Explorer", "Order from Sunrise Breakfast Club", breakfast_orders >= 1),
            ("Cuisine Collector", "Try two different cuisine types", cuisine_count >= 2),
            ("Campus Regular", "Complete three demo orders", total_orders >= 3),
            ("Six-Kitchen Explorer", "Order from three different restaurants", len(unique_restaurants) >= 3),
            ("Treat Yourself", "Spend ₹1,000 total across demo orders", total_spend >= 1000),
        ]
        unlocked = sum(1 for _, _, achieved in reward_rules if achieved)
        st.progress(unlocked / len(reward_rules), text=f"{unlocked} of {len(reward_rules)} badges unlocked")
        badge_cols = st.columns(3)
        for idx, (badge_name, description, achieved) in enumerate(reward_rules):
            with badge_cols[idx % 3]:
                st.markdown(f'<div class="{"badge-unlocked" if achieved else "badge-locked"}"><strong>{"🏅" if achieved else "🔒"} {badge_name}</strong><br><small>{description}</small></div>', unsafe_allow_html=True)
        st.caption("Badges are based on completed demo orders in this active session. They are not linked to a real loyalty account.")

# ---------------------------------------------------------------------------
# MENU: separate menu-focused interface with clear item cards
# ---------------------------------------------------------------------------
elif st.session_state.page == "Menu":
    restaurant = active_restaurant()
    shared_header(
        "THE MENU",
        f"{restaurant['emoji']} {restaurant['name']}",
        f"{restaurant['cuisine']} · ★ {restaurant['rating']} · {restaurant['distance']:.1f} km away · about {restaurant['eta']} min",
        "🍽️",
    )
    selector_col, note_col = st.columns([1.2, 1.8])
    with selector_col:
        chosen_restaurant = st.selectbox(
            "Switch restaurant",
            [r["name"] for r in ordered],
            index=[r["name"] for r in ordered].index(restaurant["name"]),
            key="menu_restaurant_selector",
        )
        if chosen_restaurant != st.session_state.selected:
            set_restaurant(chosen_restaurant)
            st.rerun()
    with note_col:
        st.info("Tip: switching restaurants starts a fresh cart so your bill stays accurate.")

    if not restaurant["deliverable"]:
        st.error(f"We deliver within {MAX_DELIVERY_KM} km. Change your location or choose a closer restaurant.")
    menu_filter_col, menu_fav_col = st.columns([1.6, 1])
    with menu_filter_col:
        dish_search = st.text_input("Search this menu", placeholder="Search dishes or ingredients…", key=f"dish_search_{restaurant['name']}")
    with menu_fav_col:
        veg_only_menu = st.checkbox("🌱 Vegetarian only", key="menu_veg_filter")
    show_favourites = st.checkbox("💛 Show favourites only", key=f"show_favourites_{restaurant['name']}")
    # Group each restaurant's menu into sensible sections, like modern food-ordering apps.
    category_order = [
        "Cereals & Bowls", "Toast & Sandwiches", "South Indian", "Indian Breakfast", "Global Breakfast",
        "Starters", "Starters & Light Bites", "Main Course", "Pizza", "Burgers", "Wraps",
        "Bowls & Mains", "Noodles & Rice", "Pasta", "Soups", "Sides", "Sides & Breads",
        "Sides & Light Bites", "Drinks", "Desserts", "Desserts & Fruit",
    ]
    grouped_menu = {}
    for menu_item in restaurant["menu"]:
        item_name, description, price, is_veg = menu_item
        if veg_only_menu and not is_veg:
            continue
        if dish_search.strip() and dish_search.lower() not in (item_name + " " + description).lower():
            continue
        if show_favourites and item_name not in st.session_state.favourites:
            continue
        category = MENU_CATEGORIES.get(item_name, "More to Enjoy")
        grouped_menu.setdefault(category, []).append(menu_item)

    ordered_categories = [category for category in category_order if category in grouped_menu]
    ordered_categories += [category for category in grouped_menu if category not in ordered_categories]
    if ordered_categories:
        category_tabs = st.tabs([f"{category} · {len(grouped_menu[category])}" for category in ordered_categories])
        for category, category_tab in zip(ordered_categories, category_tabs):
            with category_tab:
                st.caption(f"Explore {category.lower()} at {restaurant['name']}")
                for item_name, description, price, is_veg in grouped_menu[category]:
                    current_qty = st.session_state.cart.get(item_name, 0)
                    with st.container(border=True):
                        item_col, action_col = st.columns([3.4, 1.35], vertical_alignment="center")
                        item_col.markdown(f'<div class="menu-item-title">{item_name}</div>', unsafe_allow_html=True)
                        item_col.markdown(
                            f'<span class="food-badge {"veg" if is_veg else "nonveg"}">{"🟢 Vegetarian" if is_veg else "🔴 Non-vegetarian"}</span>',
                            unsafe_allow_html=True,
                        )
                        item_col.markdown(f'<div class="menu-item-desc">{description}</div>', unsafe_allow_html=True)
                        item_col.markdown(f'<div class="menu-card-price">{inr(price)}</div>', unsafe_allow_html=True)
                        fav_label = "💛 Saved" if item_name in st.session_state.favourites else "♡ Save"
                        if item_col.button(fav_label, key=f"fav_{restaurant['name']}_{item_name}"):
                            if item_name in st.session_state.favourites:
                                st.session_state.favourites.remove(item_name)
                            else:
                                st.session_state.favourites.append(item_name)
                            st.rerun()
                        action_col.caption(f"In cart: **{current_qty}**")
                        if action_col.button("＋ Add to cart", key=f"add_{restaurant['name']}_{item_name}", use_container_width=True, disabled=not restaurant["deliverable"]):
                            st.session_state.cart[item_name] = current_qty + 1
                            st.rerun()
                        if current_qty > 0 and action_col.button("− Remove one", key=f"remove_{restaurant['name']}_{item_name}", use_container_width=True):
                            if current_qty > 1:
                                st.session_state.cart[item_name] = current_qty - 1
                            else:
                                del st.session_state.cart[item_name]
                            st.rerun()
    else:
        st.info("No dishes match this filter at the selected restaurant.")

    st.markdown(
        f'<div class="menu-footer"><span>Current subtotal</span><strong>{inr(cart_item_total())}</strong></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    if left.button("← Keep exploring", use_container_width=True):
        go_to("Home")
    if right.button(f"View cart ({cart_count()}) →", type="primary", use_container_width=True):
        go_to("Cart")

# ---------------------------------------------------------------------------
# CART: basket-style interface with order summary and clear next steps
# ---------------------------------------------------------------------------
elif st.session_state.page == "Cart":
    restaurant = active_restaurant()
    shared_header(
        "YOUR BASKET",
        "A little happiness, coming up.",
        "Review your choices, adjust quantities, and check your subtotal before checkout.",
        "🛒",
    )
    if not st.session_state.cart:
        st.markdown('<div class="empty-state"><div class="empty-emoji">🧺</div><h3>Your cart is waiting for something delicious.</h3><p>Pick a kitchen and add a few favourites to get started.</p></div>', unsafe_allow_html=True)
        if st.button("Browse restaurants →", type="primary", use_container_width=True):
            go_to("Home")
    else:
        st.markdown(f"**Ordering from:** {restaurant['emoji']} {restaurant['name']}")
        st.caption("Your basket is reserved for one restaurant at a time.")
        for item_name, description, price, is_veg in restaurant["menu"]:
            quantity = st.session_state.cart.get(item_name, 0)
            if quantity <= 0:
                continue
            with st.container(border=True):
                row1, row2, row3 = st.columns([4, 1.4, 1.5])
                row1.markdown(f"**{'🟢' if is_veg else '🔴'} {item_name}**")
                row1.caption(description)
                row2.markdown(f"**{inr(price * quantity)}**")
                row3.markdown(f"Quantity: **{quantity}**")
                minus_col, plus_col, remove_col = st.columns([1, 1, 2])
                if minus_col.button("− One", key=f"cart_minus_{item_name}", use_container_width=True):
                    if quantity > 1:
                        st.session_state.cart[item_name] = quantity - 1
                    else:
                        del st.session_state.cart[item_name]
                    st.rerun()
                if plus_col.button("+ One", key=f"cart_plus_{item_name}", use_container_width=True):
                    st.session_state.cart[item_name] = quantity + 1
                    st.rerun()
                if remove_col.button("Remove", key=f"cart_remove_{item_name}", use_container_width=True):
                    del st.session_state.cart[item_name]
                    st.rerun()

        render_smart_cart(restaurant, "cart_pair")

        total_col, action_col = st.columns([1.4, 1])
        with total_col:
            st.markdown(
                f'<div class="cart-total-card"><span>Food subtotal</span><strong>{inr(cart_item_total())}</strong><small>Delivery, GST and fees are calculated at checkout.</small></div>',
                unsafe_allow_html=True,
            )
        with action_col:
            st.write("")
            if st.button("← Back to menu", use_container_width=True):
                go_to("Menu")
            if st.button("Continue to checkout →", type="primary", use_container_width=True):
                go_to("Checkout")

# ---------------------------------------------------------------------------
# CHECKOUT: order details, clear bill, confirmation and final receipt
# ---------------------------------------------------------------------------
elif st.session_state.page == "Checkout":
    restaurant = active_restaurant()
    shared_header(
        "ALMOST THERE",
        "Let's make it official.",
        "Choose your delivery preferences, review every charge, and place your demo order.",
        "💳",
    )
    if not st.session_state.cart:
        st.markdown('<div class="empty-state"><div class="empty-emoji">🛍️</div><h3>Your next meal is just a few clicks away.</h3><p>Add food to your cart before checking out.</p></div>', unsafe_allow_html=True)
        if st.button("Browse the menu →", type="primary"):
            go_to("Menu")
    elif not restaurant["deliverable"]:
        st.error(
            f"{restaurant['name']} is {restaurant['distance']:.1f} km away. "
            f"Delivery is limited to {MAX_DELIVERY_KM} km. Please change your location or choose a closer restaurant."
        )
        if st.button("Change delivery location"):
            go_to("Location")
    else:
        render_smart_cart(restaurant, "checkout_pair")
        details_col, preference_col = st.columns([1.1, 1])
        with details_col:
            st.markdown("### 🍽️ Your order")
            st.markdown(f"**{restaurant['name']}**")
            for item_name, description, price, is_veg in restaurant["menu"]:
                quantity = st.session_state.cart.get(item_name, 0)
                if quantity > 0:
                    st.write(f"{quantity} × {item_name} — **{inr(quantity * price)}**")
            st.caption(f"Delivering to: {location_label}")
        with preference_col:
            st.markdown("### 🚲 Delivery preferences")
            customer_name = st.text_input("Name for the order", key="checkout_customer_name", placeholder="Your name")
            customer_phone = st.text_input("Contact number", key="checkout_customer_phone", placeholder="10-digit mobile number", max_chars=10)
            phone_valid = customer_phone.isdigit() and len(customer_phone) == 10
            if customer_phone and not phone_valid:
                st.warning("Enter a valid 10-digit mobile number for this demo checkout.")
            st.caption("A name and valid 10-digit number are required to place a demo order.")
            delivery_speed = st.radio("Delivery speed", ["Standard", "Express ⚡ (+₹30)"], horizontal=True)
            express = delivery_speed.startswith("Express")
            tip = st.select_slider("Tip for your delivery partner (₹)", options=[0, 10, 20, 30, 50], value=0)
            coupon_code = st.text_input(
                "Coupon code",
                placeholder="Try PRAMODSIRPRO, SIRPLS, PASSKARADO or WELCOME50",
                key="checkout_coupon",
            ).strip().upper()
            st.caption("🎟️ PRAMODSIRPRO — Pramod Sir's Python Perk: 15% off (max ₹75) on ₹249+ orders")
            st.caption("😭 SIRPLS — Sir, Please Save My GPA: 10% off (max ₹50) on ₹199+ orders")
            st.caption("🙏 PASSKARADO — Pass Karado, Sir: 15% off (max ₹60) on ₹299+ orders")
            payment = st.selectbox("Payment method", ["UPI", "Credit / Debit Card", "Cash on Delivery"], key="checkout_payment")
            contactless = st.checkbox("Contactless delivery", key="checkout_contactless")
            instructions = st.text_input("Cooking or delivery note", placeholder="Less spicy, ring the bell...", key="checkout_instructions")

        with st.expander("🎟️ Available coupons"):
            for code, info in COUPONS.items():
                st.markdown(f"**{code}** — {info['desc']}")

        item_total = cart_item_total()
        bill = calculate_bill(item_total, restaurant["packaging"], restaurant["distance"], express, coupon_code, tip)
        eta = estimate_eta(restaurant["prep"], restaurant["distance"], express)
        if bill["coupon_msg"]:
            if bill["coupon_ok"]:
                st.success(bill["coupon_msg"])
            else:
                st.warning(bill["coupon_msg"])

        st.markdown("### 🧾 Your final bill")
        receipt_rows = show_bill_rows(bill, restaurant["menu"], st.session_state.cart)
        st.markdown(f'<div class="bill-box receipt-box">{receipt_rows}</div>', unsafe_allow_html=True)
        st.caption(f"Estimated delivery: about {eta} minutes · Payment: {payment}")

        # Do not let an order be placed with a mistyped/ineligible coupon still entered.
        # The customer can correct the code or clear the field to continue without one.
        if st.button(
            "Place my order  ✨",
            type="primary",
            use_container_width=True,
            disabled=(not bill["coupon_ok"] or not customer_name.strip() or not phone_valid),
        ):
            order_id = "CT" + str(random.randint(10000, 99999))
            partner = random.choice(["Rahul", "Amit", "Sandeep", "Vikram", "Deepak"])
            order_items = []
            for item_name, description, price, is_veg in restaurant["menu"]:
                quantity = st.session_state.cart.get(item_name, 0)
                if quantity > 0:
                    order_items.append({
                        "name": item_name,
                        "quantity": quantity,
                        "unit_price": price,
                        "line_total": quantity * price,
                    })
            order = {
                "order_id": order_id,
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "restaurant": restaurant["name"],
                "emoji": restaurant["emoji"],
                "cuisine": restaurant["cuisine"],
                "items": order_items,
                "item_total": bill["item_total"],
                "discount": bill["discount"],
                "delivery_fee": bill["delivery_fee"],
                "express_fee": bill["express_fee"],
                "packaging": bill["packaging"],
                "platform_fee": bill["platform_fee"],
                "gst": bill["gst"],
                "tip": bill["tip"],
                "total": bill["total"],
                "payment": payment,
                "customer_name": customer_name.strip(),
                "customer_phone": customer_phone,
                "delivery_location": location_label,
                "partner": partner,
                "eta": eta,
                "delivery_speed": delivery_speed,
                "contactless": contactless,
                "instructions": instructions.strip(),
            }
            # Short live demo simulation. This is simulated status, not real tracking.
            st.markdown("### 🚴 Your delivery is coming to life")
            delivery_box = st.empty()
            delivery_progress = st.progress(0, text="Order confirmed")
            stages = [
                (25, "🟢 Step 1 · Kitchen is preparing your order...", "Your food is being freshly prepared."),
                (60, "🚴 Step 2 · Your delivery partner has picked it up!", f"{partner} is on the way to {location_label}."),
                (100, "🎉 Step 3 · Delivered! Enjoy your meal.", "Thanks for ordering with ChaiTapri Eats!"),
            ]
            for progress_value, headline, detail in stages:
                delivery_box.markdown(
                    f'<div class="delivery-stage"><h3>{headline}</h3><p>{detail}</p><small>Order {order_id} · Demo delivery simulation</small></div>',
                    unsafe_allow_html=True,
                )
                delivery_progress.progress(progress_value, text=f"Delivery progress: {progress_value}%")
                time.sleep(0.8)
            order["delivery_status"] = "Delivered (simulated)"
            st.session_state.my_orders.insert(0, order)
            st.session_state.last_order = order
            st.session_state.cart = {}
            st.session_state.page = "My Orders"
            st.balloons()
            time.sleep(0.25)
            st.rerun()

# ---------------------------------------------------------------------------
# LOCATION: a dedicated location-selection experience
# ---------------------------------------------------------------------------
elif st.session_state.page == "Location":
    shared_header(
        "DELIVERY DESTINATION",
        "Where should we bring the good stuff?",
        "Choose a saved demo area or try browser GPS. The sample kitchens are around Sonipat.",
        "📍",
    )
    loc_left, loc_right = st.columns([1.15, 1])
    with loc_left:
        st.markdown("### 🗺️ Choose your area")
        area_choice = st.selectbox(
            "Available demo locations",
            list(PRESET_LOCATIONS.keys()),
            index=list(PRESET_LOCATIONS.keys()).index(
                st.session_state.delivery_location
                if st.session_state.delivery_location in PRESET_LOCATIONS
                else DEFAULT_LOCATION
            ),
            key="location_area_choice",
        )
        lat, lon = PRESET_LOCATIONS[area_choice]
        st.markdown(
            f'<div class="location-preview"><span class="location-pin">📍</span><div><strong>{area_choice}</strong><small>Approx. coordinates: {lat:.4f}, {lon:.4f}</small></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Save this delivery location →", type="primary", use_container_width=True):
            st.session_state.delivery_location = area_choice
            st.session_state.delivery_lat = lat
            st.session_state.delivery_lon = lon
            st.session_state.location_mode = "Choose an area"
            st.success(f"Delivery location updated to {area_choice}.")
            st.rerun()
    with loc_right:
        st.markdown("### 📡 Use browser GPS")
        st.write("If your browser supports location access, you can try detecting your current position.")
        if GPS_AVAILABLE:
            try:
                gps = streamlit_geolocation()
                if gps and gps.get("latitude") is not None and gps.get("longitude") is not None:
                    st.success("GPS coordinates detected.")
                    st.caption(f"{gps['latitude']:.4f}, {gps['longitude']:.4f}")
                    if st.button("Use my GPS coordinates", use_container_width=True):
                        st.session_state.delivery_location = "Live GPS location"
                        st.session_state.delivery_lat = float(gps["latitude"])
                        st.session_state.delivery_lon = float(gps["longitude"])
                        st.session_state.location_mode = "Use my GPS location"
                        st.rerun()
                else:
                    st.info("Allow location access in the browser. If it doesn't respond, choose a demo area on the left.")
            except Exception:
                st.warning("GPS isn't available in this browser right now. Choose a demo area instead.")
        else:
            st.info("The optional GPS package isn't installed. Choosing an area still works.")
        if st.button("← Return to home", use_container_width=True):
            go_to("Home")

    st.markdown("### 🚚 Nearby demo kitchens")
    distance_cols = st.columns(3)
    for i, r in enumerate(sorted(RESTAURANTS, key=lambda x: x["distance"])[:3]):
        with distance_cols[i]:
            st.metric(r["name"], f"{r['distance']:.1f} km", "In delivery range" if r["deliverable"] else "Out of range")

# ---------------------------------------------------------------------------
# MY ORDERS: session-based order history and full itemised receipts
# ---------------------------------------------------------------------------
elif st.session_state.page == "My Orders":
    shared_header(
        "YOUR ORDER JOURNEY",
        "Good choices deserve a receipt.",
        "Your completed demo orders are listed here for this browser session, with the restaurant, items, payment choice and final bill.",
        "📦",
    )
    if not st.session_state.my_orders:
        st.markdown('<div class="empty-state"><div class="empty-emoji">🧾</div><h3>No orders yet — your first favourite is waiting.</h3><p>Once you place a demo order, its receipt will appear here.</p></div>', unsafe_allow_html=True)
        if st.button("Find something delicious →", type="primary", use_container_width=True):
            go_to("Home")
    else:
        st.markdown(f"**{len(st.session_state.my_orders)} order(s) in this session**")
        for order in st.session_state.my_orders:
            with st.expander(f"{order['emoji']} {order['restaurant']}  ·  {order['order_id']}  ·  {inr(order['total'])}"):
                st.markdown(f"**Order ID:** `{order['order_id']}`")
                st.caption(f"{order['date']} · {order['delivery_speed']} · {order['eta']} min estimated")
                st.success(order.get("delivery_status", "Order placed (simulated)"))
                st.markdown('<div class="order-timeline"><span>✓ Order confirmed</span><span>✓ Kitchen prepared</span><span>✓ Partner delivered</span></div>', unsafe_allow_html=True)
                st.markdown(f"**Delivered to:** {order['delivery_location']}")
                if order.get("customer_name"):
                    st.caption(f"Order for {order['customer_name']} · Contact ending {order.get('customer_phone', '')[-4:]}")
                st.markdown("#### Items ordered")
                for item in order["items"]:
                    st.write(f"{item['quantity']} × {item['name']} ({inr(item['unit_price'])} each) — **{inr(item['line_total'])}**")
                old_bill = {
                    "item_total": order["item_total"],
                    "discount": order["discount"],
                    "delivery_fee": order["delivery_fee"],
                    "express_fee": order["express_fee"],
                    "packaging": order["packaging"],
                    "platform_fee": order["platform_fee"],
                    "gst": order["gst"],
                    "tip": order["tip"],
                    "total": order["total"],
                }
                receipt_rows = show_bill_rows(
                    old_bill,
                    [(item["name"], "", item["unit_price"], True) for item in order["items"]],
                    {item["name"]: item["quantity"] for item in order["items"]},
                )
                st.markdown(f'<div class="bill-box receipt-box">{receipt_rows}</div>', unsafe_allow_html=True)
                st.caption(f"Payment: {order['payment']} · Delivery partner: {order['partner']}")
                if order["contactless"]:
                    st.info("Contactless delivery was selected.")
                if order["instructions"]:
                    st.write(f"Order note: {order['instructions']}")
                st.success("Thank you for choosing ChaiTapri Eats!")
                if st.button("↻ Reorder these items", key=f"reorder_{order['order_id']}", use_container_width=True):
                    st.session_state.selected = order["restaurant"]
                    st.session_state.cart = {item["name"]: item["quantity"] for item in order["items"]}
                    st.session_state.page = "Cart"
                    st.rerun()

        if st.button("Order something else →", type="primary", use_container_width=True):
            go_to("Home")

st.divider()
st.markdown(
    '<div class="app-footer"><strong>🍜 ChaiTapri Eats</strong><span>Made for campus cravings · Sonipat, Haryana</span><span>About · Help · Contact · Campus favourites</span><small>Student project demo: photos are illustrative, restaurant listings, delivery partners, payments and order history are simulated. No payment is processed. Order history lasts for this active app session and is not stored in a database.</small></div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# PROJECT NOTES: transparent explanations and quick manual test cases
# ---------------------------------------------------------------------------
with st.expander("🧠 How this project works (for curious customers and project review)"):
    st.markdown(
        """
        - **Lists and dictionaries:** restaurant menus store dish details; the coupon dictionary maps each code to its rules.
        - **Functions:** `base_delivery_fee()`, `apply_coupon()` and `calculate_bill()` keep calculations in reusable places.
        - **Conditionals:** delivery distance, coupon eligibility and delivery charges use `if` / `elif` / `else`.
        - **Loops:** the app loops through restaurant menus to display dishes and build the receipt.
        - **Session state:** the cart, selected restaurant, favourites and order history persist while navigating between pages.
        - **Search and filters:** text matching narrows restaurants and menu items; checkboxes filter vegetarian dishes and saved favourites.
        - **Crave Club:** recommendations and budget combos are built by filtering the actual menu data; the meal builder adds real menu items to the cart.
        - **Group Feast and rewards:** bill splitting uses division; achievement badges are derived from completed demo orders.
        - **Homepage carousel:** three CSS-animated slides rotate every six seconds without JavaScript or additional packages.
        - **Input validation:** checkout requires a name and a 10-digit contact number, while coupon rules are checked before an order can be placed.
        - **Validation:** invalid or ineligible coupon codes show a message and prevent accidental checkout until the code is corrected or cleared.

        **Quick test checklist**
        1. Add one dish and check that the subtotal equals its price.
        2. Enter `SIRPLS` with a subtotal below ₹199: it should be rejected.
        3. Enter `SIRPLS` with a subtotal of ₹199 or more: it should apply 10% off, capped at ₹50.
        4. Enter `PASSKARADO` with a subtotal of ₹299 or more: it should apply 15% off, capped at ₹60.
        5. Enter a made-up coupon: checkout should stay disabled until you fix or clear the code.
        6. Reach a food subtotal of ₹499: standard delivery should become free under the app's pricing rules.
        7. Place a valid demo order with a name and 10-digit number; confirm it appears in **My Orders**.
        8. Save a dish as a favourite, filter favourites, then remove it from favourites.
        9. Use **Reorder these items** from order history and check the cart contents.
        10. In Crave Club, try a vegetarian craving under ₹200 and check that recommendations respect the filters.
        11. Build a custom meal and verify that the cart subtotal equals the sum of selected menu prices.
        12. Check the Group Feast split for ₹500 and four people: each share should be ₹125.
        13. Place a breakfast order and verify that the Breakfast Explorer badge unlocks.
        14. Watch the homepage carousel to confirm that it rotates through three slides automatically.

        *This is a demonstration app: restaurant listings, fees and delivery tracking are simulated, not live services.*
        """
    )
