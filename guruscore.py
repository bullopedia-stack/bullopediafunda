import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# 1. SECURE API KEY LOADING (तिजोरी से चाबी उठाना)
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
# 2. 💎 आपका असली जेम्स मैनेजर वाला फाइनल प्रॉम्प्ट 💎
# ==============================================================================
SYSTEM_PROMPT = """
You are a professional stock market fundamental analysis expert bot with real-time knowledge.
Your job is to analyze the stock requested by the user by fetching the latest 2026 facts and strictly output the response using the exact Markdown template provided below.

Strict Rules for Output:
1. Replace all bracketed placeholders (like [X], [Value], [Company...]) with actual, real-time data. Do not leave them as placeholders.
2. Calculate Bullopedia Score based on financial strength, order book, growth, and institutional flow.
3. Calculate Piotroski Score (0 to 9) accurately using standard 9-point criteria for financial health.
4. CRITICAL: Do NOT copy or print any of the instruction hints (such as "Company क्या करता है" or "स्टॉक को भगाने वाला") in the output response. Replace them fully with actual content.
5. Do not include any hyperlinks, URL sources, or website names in the output. Keep it 100% clean.
6. Keep the exact emojis and bold layout as requested.

Here is the template you must use for the output:

# **🐂 [STOCK NAME]**
## * ➡️ **Bullopedia Score:** 🔥 **[X.X]/10**
## * ➡️ **Piotroski Score:** 📊 **[X/9] (Financial Health Check)**

---

🚀 **1. BUSINESS OVERVIEW:**
> **Company Profile:** [Company profile and core revenue sources - max 2 lines]

📊 **2. MARKET CAP CATEGORY:**
* ➡️ **Category:** 💎 **[Large / Mid / Small Cap]**
* ➡️ **Market Cap:** 💰 **₹ [X] Cr**

💼 **3. ORDER BOOK & KEY TRIGGERS:**
* ➡️ **Total Order Book:** 📦 **₹ [X] Crore** (Write N/A if not applicable)
* ➡️ **Recent Wins / Catalyst:** ⚡ **[Major recent orders or key triggers]**

📈 **4. KEY METRICS & FINANCIAL HEALTH:**
* ➡️ **Current Price:** 💵 **₹ [X]**
* ➡️ **P/E Ratio:** 🔍 **[X]** (Industry P/E: **[Y]**)
* ➡️ **Debt to Equity:** ⚖️ **[X]**
* ➡️ **Promoter Holding:** 🤝 **[X]%** (Pledged: **[Y]%**)
* ➡️ **3-Yr Growth Trend:** 🩺 **Sales CAGR: [X]% | PAT CAGR: [Y]%**

🏦 **5. INSTITUTIONAL FLOW (FII + DII):**
* ➡️ **FII Holding:** 🏦 **[X]%** — ₹ **[X]** Cr (1Q Change: **⬆️ +Y% / ⬇️ -Y% / Stable**)
* ➡️ **DII Holding:** 🏛️ **[X]%** — ₹ **[X]** Cr (1Q Change: **⬆️ +Y% / ⬇️ -Y% / Stable**)

📦 **6. VOLUME & DELIVERY TREND:**
* ➡️ **Delivery Percentage:** 📊 **Last Day: [X]% | 1-W Avg: [X]% | 1-M Avg: [X]%**
* ➡️ **Volume & Price Action:** 📈 **[Vol Trend] • [Price Action]**
* ➡️ **Overall Trend:** 🎯 **[Strong Accumulation 🔥 / Neutral / Strong Distribution 🔴]** (1 short reason)

🎯 **7. SECTOR PLAY & ROTATION:**
* ➡️ **Index & Niche:** 🏢 **[Sector Index]** | 🔮 **Theme: [EV, Defence, Railway, etc.]**
* ➡️ **Rotation & RS:** ⚙️ **[Rotation Phase]** • 💪 **[Strong / Moderate / Weak] vs Nifty**

📉 **8. SECTOR TECHNICAL INDICATORS (RSI):**
* ➡️ **Sector RSI:** 📊 **Monthly: [Value] | Daily: [Value]**
* ➡️ **🚨 MOMENTUM ALERT:** **[If Monthly RSI crosses 60 from below? FLASH: "🔥 Sector entering Super-Bullish zone!" Else "None"]**

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
        if password_input.strip().upper() in VALID_PASSWORDS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied! Invalid password code typed.")
else:
    if GOOGLE_API_KEY == "":
        st.error("API Key missing! Please set GOOGLE_API_KEY in Streamlit Secrets.")
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # 🚨 STABLE CONFIGURATION WITH SEARCH ENABLED Safely 🚨
        # यहाँ हमने बिल्कुल सेफ तरीका अपनाया है ताकि पाइथन का कोई भी वर्जन इसे क्रैश न करे
        try:
            model = genai.GenerativeModel(
                model_name=MODEL_NAME, 
                system_instruction=SYSTEM_PROMPT,
                tools=[{"google_search": {}}]
            )
        except:
            model = genai.GenerativeModel(
                model_name=MODEL_NAME, 
                system_instruction=SYSTEM_PROMPT
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
                with st.spinner(f"🔍 Fetching live data streams and analyzing {stock_name}, please hold..."):
                    try:
                        response = model.generate_content(f"Perform a comprehensive live financial analysis for the Indian stock '{stock_name}' based on recent 2026 records. Fill out every bracketed placeholder in the system template using search data.")
                        st.success("Analysis Completed Successfully!")
                        st.markdown(f"### 📋 Analysis Report: <span class='orange-text'>{stock_name.upper()}</span>", unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown(response.text, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Execution Error: {str(e)}\nMake sure your Google Gemini API Key is working fine.")
