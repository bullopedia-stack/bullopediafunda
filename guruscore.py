import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# 1. YOUR BRANDING & CONFIGURATION
# ==============================================================================
YOUR_BRAND_NAME = "BULLOPEDIA"  # Your Brand Name

# Local logo file checking logic
LOGO_FILENAME = "logo.png"  # If your file is jpeg, change this to "logo.jpeg"
if os.path.exists(LOGO_FILENAME):
    YOUR_LOGO_PATH = LOGO_FILENAME
elif os.path.exists("logo.jpeg"):
    YOUR_LOGO_PATH = "logo.jpeg"
else:
    YOUR_LOGO_PATH = None

# Valid passwords list for your students
VALID_PASSWORDS = ["STUDENT2026", "BULLGURU", "VIPACCESS"]

# Paste your Google AI Studio API Key here ⬇️
GOOGLE_API_KEY = "AIzaSyA4s0e8tADElCt7z_ZcLG79xCkLxovGHFk"  # <-- Paste Key Here

# Latest 2026 Gemini Model
MODEL_NAME = "models/gemini-2.5-flash"

# ==============================================================================
# 2. SYSTEM PROMPT (YOUR GEMS STOCK ANALYSIS TEMPLATE)
# ==============================================================================
SYSTEM_PROMPT = """
You are a professional stock market fundamental analysis bot. Your job is to search the internet for the latest real-time stock data of the user's requested Indian stock. Analyze the stock based on the latest available quarterly and annual data (as of 2026), calculate or fetch the metrics, and strictly output the response using the exact Markdown template provided below.

Strict Rules for Output:
1. Replace all bracketed placeholders (like [X], [Company...], [Value]) with actual, accurate data.
2. Calculate Bullopedia Score based on financial strength, order book, growth, and institutional flow.
3. Calculate Piotroski Score (0 to 9) accurately using standard 9-point criteria for financial health.
4. Do not include any hyperlinks, URL sources, or website names in the output. Keep it 100% clean.
5. Keep the exact emojis and bold layout as requested.

Here is the template you must use for the output:

# **🐂 [STOCK NAME]**
## * ➡️ **Bullopedia Score:** 🔥 **[X.X]/10**
## * ➡️ **Piotroski Score:** 📊 **[X/9] (Financial Health Check)**

---

🚀 **1. BUSINESS OVERVIEW:**
> **Company Profile:** [Company profile - max 2 lines]

📊 **2. MARKET CAP CATEGORY:**
* ➡️ **Category:** 💎 **[Large / Mid / Small Cap]** * ➡️ **Market Cap:** 💰 **₹ [X] Cr**

💼 **3. ORDER BOOK & KEY TRIGGERS:**
* ➡️ **Total Order Book:** 📦 **₹ [X] Crore** (Write N/A if not applicable)
* ➡️ **Recent Wins / Catalyst:** ⚡ **[Major recent catalysts]**

📈 **4. KEY METRICS & FINANCIAL HEALTH:**
* ➡️ **Current Price:** 💵 **₹ [X]** * ➡️ **P/E Ratio:** 🔍 **[X]** (Industry P/E: **[Y]**)
* ➡️ **Debt to Equity:** ⚖️ **[X]** * ➡️ **Promoter Holding:** 🤝 **[X]%** (Pledged: **[Y]%**)
* ➡️ **3-Yr Growth Trend:** 🩺 **Sales CAGR: [X]% | PAT CAGR: [Y]%**

🏦 **5. INSTITUTIONAL FLOW (FII + DII):**
* ➡️ **FII Holding:** 🏦 **[X]%** — ₹ **[X]** Cr (1Q Change: **⬆️ +Y% / ⬇️ -Y% / Stable**)
* ➡️ **DII Holding:** 🏛️ **[X]%** — ₹ **[X]** Cr (1Q Change: **⬆️ +Y% / ⬇️ -Y% / Stable**)

📦 **6. VOLUME & DELIVERY TREND:**
* ➡️ **Delivery Percentage:** 📊 **Last Day: [X]% | 1-W Avg: [X]% | 1-M Avg: [X]%**
* ➡️ **Volume & Price Action:** 📈 **[Vol Trend] • [Price Action]**
* ➡️ **Overall Trend:** 🎯 **[Strong Accumulation 🔥 / Neutral / Distribution 🔴]** (1 short reason)

🎯 **7. SECTOR PLAY & ROTATION:**
* ➡️ **Index & Niche:** 🏢 **[Sector]** | 🔮 **Theme: [Theme]**
* ➡️ **Rotation & RS:** ⚙️ **[Rotation]** • 💪 **[Strong / Moderate / Weak] vs Nifty**

📉 **8. SECTOR TECHNICAL INDICATORS (RSI):**
* ➡️ **Sector RSI:** 📊 **Monthly: [Value] | Daily: [Value]**
* ➡️ **🚨 MOMENTUM ALERT:** **[Alert message or "None"]**

🦅 **9. BULLOPEDIA TAKEAWAY:**
* 🟢 **Pros / Triggers:** **[1-2 strongest points/triggers]**
* 🔴 **Cons / Risks:** **[1 main risk or key resistance level]**
* ⚡ **Final Verdict:** 👑 **[Strong Bullish / Bullish / Neutral / Cautious]**
"""

# ==============================================================================
# 3. PREMIUM BLACK & ORANGE THEME (CSS STYLING) 🎨
# ==============================================================================
st.set_page_config(page_title=YOUR_BRAND_NAME, page_icon="📈", layout="centered")

st.markdown("""
<style>
/* 1. App Background Styling */
[data-testid="stAppViewContainer"] {
    background-color: #0d0d0d;
    color: #ffffff;
}

/* 2. Custom Orange Accent Styling */
.orange-text {
    color: #ff7700;
    font-weight: bold;
}

/* 3. Hide Unwanted Headers & Footers */
#MainMenu, header, footer {visibility: hidden;}

/* 4. Orange Buttons Custom Styling */
div.stButton > button:first-child {
    background-color: #ff7700;
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 12px 24px;
    width: 100%;
    transition: background-color 0.3s ease;
}

div.stButton > button:first-child:hover {
    background-color: #e06600;
    border: none;
}

/* 5. Center Logo Display Alignment */
.logo-container {
    text-align: center;
    margin-bottom: 20px;
}

/* 6. Report Layout Containers Background */
div.markdown-container-markdownContainer {
    background-color: #161616;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #262626;
    margin-top: 20px;
}

/* 7. Text Contrast Fixes */
p, h1, h2, h3, li, blockquote, span {
    color: #ffffff !important;
}

/* 8. Highlights in the final output report */
div.markdown-container-markdownContainer h1 {
    color: #ff7700 !important;
}
div.markdown-container-markdownContainer strong {
    color: #ff7700;
}
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 4. SECURE PORTAL ACCESS GATEWAY
# ==============================================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Screen UI before login
if not st.session_state.logged_in:
    st.write("")
    st.write("")
    
    # Renders logo dynamically from the folder
    if YOUR_LOGO_PATH:
        st.image(YOUR_LOGO_PATH, width=180, use_container_width=False)
    else:
        st.markdown(f"<h1 style='text-align: center; color: #ff7700;'>🐂 {YOUR_BRAND_NAME}</h1>", unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align: center;'>Welcome to <span class='orange-text'>{YOUR_BRAND_NAME}</span></h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #ff7700;'>🔐 Secure Student Portal Access</h4>", unsafe_allow_html=True)
    st.write("")
    
    password_input = st.text_input("Enter your Access Code (Password) to login:", type="password")
    login_button = st.button("Access Portal")
    
    if login_button:
        if password_input in VALID_PASSWORDS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied! Invalid password code typed.")

# Dashboard View UI after login
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT
    )

    # Upper Branding Title & Logout Section
    col1, col2 = st.columns([4, 1])
    with col1:
        if YOUR_LOGO_PATH:
            st.image(YOUR_LOGO_PATH, width=80)
            st.markdown(f"<h1 style='color: #ff7700; margin-top: 5px; margin-bottom: 0;'>{YOUR_BRAND_NAME}</h1>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='color: #ff7700; margin: 0;'>🐂 {YOUR_BRAND_NAME}</h1>", unsafe_allow_html=True)
            
    with col2:
        st.write("")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()
            
    st.markdown("<hr style='border: 1px solid #262626;'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #ff7700;'>📊 Live Fundamental Analysis Bot</h3>", unsafe_allow_html=True)

    # User Input fields
    stock_name = st.text_input("Enter Stock Name (e.g., TATA MOTORS, GMDC):", placeholder="Type stock code ticker here...")
    
    analyze_button = st.button("Run Analysis")

    if analyze_button:
        if stock_name.strip() == "":
            st.warning("Please specify a valid Indian stock name first.")
        else:
            with st.spinner(f"🔍 Crawling live data streams and analyzing {stock_name}, please hold..."):
                try:
                    response = model.generate_content(f"Analyze this stock and strictly follow the template format: {stock_name}")
                    
                    st.success("Analysis Completed Successfully!")
                    st.markdown(f"### 📋 Analysis Report: <span class='orange-text'>{stock_name.upper()}</span>", unsafe_allow_html=True)
                    st.markdown("---")
                    
                    # Direct Markdown Rendering for Beautiful Dark Reports
                    st.markdown(response.text, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}\nMake sure your Google Gemini API Key is working fine.")
