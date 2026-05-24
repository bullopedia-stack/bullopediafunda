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
# PREMIUM THEME & LOGO SETUP
# ==============================================================================
st.set_page_config(page_title=YOUR_BRAND_NAME, page_icon="📈", layout="centered")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0d0d0d; color: #ffffff; }
.orange-text { color: #ff7700; font-weight: bold; }
#MainMenu, header, footer {visibility: hidden;}
div.stButton > button:first-child {
    background-color: #ff7700; color: #ffffff; font-weight: bold;
    border-radius: 8px; border: none; padding: 12px 24px; width: 100%;
}
div.markdown-container-markdownContainer {
    background-color: #161616; padding: 25px; border-radius: 12px; border: 1px solid #262626;
}
p, h1, h2, h3, li, blockquote, span { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. UI WITH LOGO
# ==============================================================================
def show_header():
    col1, col2 = st.columns([1, 4])
    with col1:
        # यहाँ हम 'logo.png' नाम की फाइल ढूंढेंगे जो आप गिटहब पर अपलोड करेंगे
        if os.path.exists("logo.png"):
            st.image("logo.png", width=100)
    with col2:
        st.markdown(f"<h1 style='color: #ff7700; margin-top: 10px;'>{YOUR_BRAND_NAME}</h1>", unsafe_allow_html=True)

# --- LOGIN GATEWAY ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_header()
    st.markdown("<p style='color: #ff7700;'>🔐 Secure Student Portal Access</p>", unsafe_allow_html=True)
    password_input = st.text_input("Enter Access Code:", type="password")
    if st.button("Access Portal"):
        if password_input in VALID_PASSWORDS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Password!")
else:
    # --- MAIN APP ---
    if GOOGLE_API_KEY == "":
        st.error("API Key Missing in Streamlit Secrets!")
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(model_name=MODEL_NAME)

        col_h1, col_h2 = st.columns([4, 1])
        with col_h1: show_header()
        with col_h2: 
            if st.button("Log Out"):
                st.session_state.logged_in = False
                st.rerun()
        
        st.markdown("<hr style='border: 1px solid #262626;'>", unsafe_allow_html=True)
        stock_name = st.text_input("Enter Stock Name:", placeholder="e.g. TATA MOTORS")
        
        if st.button("Run Analysis"):
            with st.spinner("Analyzing..."):
                try:
                    # (यहाँ आपका पुराना SYSTEM_PROMPT इस्तेमाल होगा, मैंने छोटा रखने के लिए यहाँ नहीं लिखा)
                    response = model.generate_content(f"Analyze {stock_name}")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")
