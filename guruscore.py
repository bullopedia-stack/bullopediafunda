import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# 🚨 SECURE API KEY LOADING
# ==============================================================================
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    GOOGLE_API_KEY = ""

# पोर्टल का पासवर्ड
VALID_PASSWORDS = ["STUDENT2026", "BULLGURU", "VIPACCESS"]
YOUR_BRAND_NAME = "BULLOPEDIA"  
MODEL_NAME = "models/gemini-2.5-flash"

# ==============================================================================
# 2. 💎 GEMS MANAGER EXACT COMPATIBLE PROMPT (With strict grounding rules)
# ==============================================================================
SYSTEM_PROMPT = """
You are a professional stock market fundamental analysis expert bot with real-time web browsing capabilities, exactly like the Gemini Gems Manager system.

CRITICAL INSTRUCTIONS FOR LIVE DATA (GROUNDING):
1. You MUST use the Google Search tool to find the most recent, real-time live data for the requested Indian stock for the current year 2026. Do NOT use your internal pre-trained knowledge for numbers.
2. Search for: "[Stock Name] share price", "[Stock Name] market cap, PE ratio, debt to equity, promoter holding", "[Stock Name] latest quarterly results 2026", "[Stock Name] order book", and "[Stock Name] FII DII holding".
3. Extract the exact numbers from the search results and strictly replace all bracketed placeholders like [X], [Value], [Company...] with these real statistics.
4. Calculate the Bullopedia Score (out of 10) and Piotroski Score (0 to 9) dynamically based strictly on the fetched 2026 financial strength.
5. Do NOT print the instruction hints (like "Company क्या करता है" or "स्टॉक को भगाने वाला") in the final response. Replace them fully with actual factual descriptions in English.
6. Absolute Rule: Do not include any hyperlinks, URL sources, markdown links, or website names in the output. Keep it 100% clean.

You MUST output the response using the exact Markdown template below:

# **🐂 [STOCK NAME]**
## * ➡️ **Bullopedia Score:** 🔥 **[X.X]/10**
## * ➡️ **Piotroski Score:** 📊 **[X/9] (Financial Health Check)**

---

🚀 **1. BUSINESS OVERVIEW:**
> **Company Profile:** [Company profile and core revenue sources based on latest search data - max 2 lines]

📊 **2. MARKET CAP CATEGORY:**
* ➡️ **Category:** 💎 **[Large / Mid / Small Cap]** * ➡️ **Market Cap:** 💰 **₹ [X] Cr**

💼 **3. ORDER BOOK & KEY TRIGGERS:**
* ➡️ **Total Order Book:** 📦 **₹ [X] Crore** (Write N/A if not applicable)
* ➡️ **Recent Wins / Catalyst:** ⚡ **[Major recent orders or core growth triggers fetched from news]**

📈 **4. KEY METRICS & FINANCIAL HEALTH:**
* ➡️ **Current Price:** 💵 **₹ [X]** * ➡️ **P/E Ratio:** 🔍 **[X]** (Industry P/E: **[Y]**)
* ➡️ **Debt to Equity:** ⚖️ **[X]** * ➡️ **Promoter Holding:** 🤝 **[X]%** (Pledged: **[Y]%**)
* ➡️ **3-Yr Growth Trend:** 🩺 **Sales CAGR: [X]% | PAT CAGR: [Y]%**

🏦 **5. INSTITUTIONAL FLOW (FII + DII):**
* ➡️ **FII Holding:** 🏦 **[X]%** — ₹ **[X]** Cr (1Q Change: **⬆️ +Y% / ⬇️ -Y% / Stable**)
* ➡️ **DII Holding:** 🏛️ **[X]%** — ₹ **[X]** Cr (1Q Change: **⬆️ +Y% / ⬇️ -Y% / Stable**)

📦 **6. VOLUME & DELIVERY TREND:**
* ➡️ **Delivery Percentage:** 📊 **Last Day: [X]% | 1-W Avg: [X]% | 1-M Avg: [X]%**
* ➡️ **Volume & Price Action:** 📈 **[Vol Trend] • [Price Tightness / Breakout Status]**
* ➡️ **Overall Trend:** 🎯 **[Strong Accumulation 🔥 / Neutral / Strong Distribution 🔴]** (1 short reason)

🎯 **7. SECTOR PLAY & ROTATION:**
* ➡️ **Index & Niche:** 🏢 **[Sector Index]** | 🔮 **Theme: [EV, Defence, Railway, etc.]**
* ➡️ **Rotation & RS:** ⚙️ **[Rotation Phase]** • 💪 **[Strong / Moderate / Weak] vs Nifty**

📉 **8. SECTOR TECHNICAL INDICATORS (RSI):**
* ➡️ **Sector RSI:** 📊 **Monthly: [Value] | Daily: [Value]**
* ➡️ **🚨 MOMENTUM ALERT:** **[If Monthly RSI crossed 60 from below? FLASH: "🔥 Sector entering Super-Bullish zone!" Else "None"]**

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
[data-testid="stAppViewContainer"] { background-color: #0d0d0d; color: #ffffff; }
.orange-text { color: #ff7700; font-weight: bold; }
#MainMenu, header, footer {visibility: hidden;}
div.stButton > button:first-child {
    background-color: #ff7700; color: #ffffff; font-size: 1.1rem; font-weight: bold;
    border-radius: 8px; border: none; padding: 12px 24px; width: 100%;
}
div.stButton > button:first-child:hover { background-color: #e06600; }
div.markdown-container-markdownContainer {
    background-color: #161616; padding: 25px; border-radius: 12px; border: 1px solid #262626;
}
p, h1, h2, h3, li, blockquote, span { color: #ffffff !important; }
div.markdown-container-markdownContainer h1, div.markdown-container-markdownContainer strong { color: #ff7700 !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. LOGO AND HEADER DISPLAY FUNCTION
# ==============================================================================
def show_header():
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=90)
    with col2:
        st.markdown(f"<h1 style='color: #ff7700; margin-top: 5px; font-size: 2.8rem;'>{YOUR_BRAND_NAME}</h1>", unsafe_allow_html=True)

# ==============================================================================
# 5. SECURE PORTAL ACCESS GATEWAY
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.write("")
    st.write("")
    show_header()
    st.markdown(f"<h3 style='text-align: center; color: #ffffff; margin-top: 0;'>Welcome to <span class='orange-text'>{YOUR_BRAND_NAME}</span></h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #ff7700;'>🔐 Secure Student Portal Access</p>", unsafe_allow_html=True)
    st.write("")
    
    password_input = st.text_input("Enter your Access Code (Password) to login:", type="password")
    login_button = st.button("Access Portal")
    
    if login_button:
        if password_input in VALID_PASSWORDS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied! Invalid password code typed.")
else:
    if GOOGLE_API_KEY == "":
        st.error("API Key missing! Please set GOOGLE_API_KEY in Streamlit Secrets.")
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # 🚨 ADVANCED GROUNDING WITH SEARCH ENABLED 🚨
        model = genai.GenerativeModel(
            model_name=MODEL_NAME, 
            system_instruction=SYSTEM_PROMPT,
            tools=[{"google_search": {}}]  # This triggers live Google Search filtering
        )

        col_h1, col_h2 = st.columns([4, 1])
        with col_h1: show_header()
                
        with col_h2:
            st.write("")
            if st.button("Log Out"):
                st.session_state.logged_in = False
                st.rerun()
                
        st.markdown("<hr style='border: 1px solid #262626;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #ff7700;'>📊 Live Fundamental Analysis Bot</h3>", unsafe_allow_html=True)

        stock_name = st.text_input("Enter Stock Name (e.g., TATA MOTORS, GMDC):", placeholder="Type stock code ticker here...")
        analyze_button = st.button("Run Analysis")

        if analyze_button:
            if stock_name.strip() == "":
                st.warning("Please specify a valid Indian stock name first.")
            else:
                with st.spinner(f"🔍 Crawling live data streams and analyzing {stock_name}, please hold..."):
                    try:
                        # Force the model to strict template completion
                        user_message = f"Fetch the latest 2026 real-time data for '{stock_name}' from Google Search. Completely fill out every bracketed placeholder in the template structure. Do not output any instructions."
                        response = model.generate_content(user_message)
                        
                        st.success("Analysis Completed Successfully!")
                        st.markdown(f"### 📋 Analysis Report: <span class='orange-text'>{stock_name.upper()}</span>", unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown(response.text, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Execution Error: {str(e)}\nMake sure your Google Gemini API Key is working fine.")
