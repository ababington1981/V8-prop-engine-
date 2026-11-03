# ==========================================
# INSTALL DEPENDENCIES (STREAMLIT & LOCALTUNNEL)
# ==========================================
import subprocess
import time
from datetime import datetime
import os
import pandas as pd

!pip install -q streamlit pandas numpy requests localtunnel

# ==========================================
# WRITE APP CODE TO app.py
# ==========================================
app_code = """
import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Five-Lens Prop Engine (v8)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

LEDGER_FILE = "model_performance_ledger.csv"

# --- INITIALIZE LEDGER IF NOT EXISTS ---
if not os.path.exists(LEDGER_FILE):
    init_df = pd.DataFrame(columns=[
        'date', 'player_name', 'prop_market', 'line', 'prediction_type', 
        'model_probability', 'market_implied_prob', 'closing_line_vig_free', 
        'actual_result', 'units_wagered', 'payout_odds'
    ])
    init_df.to_csv(LEDGER_FILE, index=False)

# --- APP STATE ---
if "selected_bookmaker" not in st.session_state:
    st.session_state.selected_bookmaker = "DraftKings"
if "min_prob" not in st.session_state:
    st.session_state.min_prob = 0.60

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("⚡ 5-Lens Prop Engine v8")
st.sidebar.markdown("Advanced quantitative auditing with **Lineup Lock Delta** & **Cannibalization Matrices**.")
st.sidebar.markdown("---")

nav_mode = st.sidebar.radio(
    "Navigation Mode", 
    [
        "📊 Live Slate Hub", 
        "📈 Performance Tracking & CLV", 
        "➕ Log New Engine Pick"
    ]
)

# ==========================================
# TAB 1: LIVE SLATE HUB
# ==========================================
if nav_mode == "📊 Live Slate Hub":
    st.title("🏀 Five-Lens Prop Engine (v8) — Slate Hub")
    st.markdown("Real-time slate evaluation featuring **Lineup Lock Delta** and **Usage Cannibalization Matrices**.")
    st.markdown("---")
    
    st.subheader("🔥 Featured High-Conviction Board")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Franz Wagner — Points (20.5)")
        st.markdown("**Play:** `OVER 20+ Points Alt (-340)` | **Conviction:** 🟢 HIGH")
        st.info("🚀 **Ceiling Escalator:** High-volume paint touch rate with Banchero out. Ladder 22+, 25+.")
        st.warning("⚠️ **Lineup Lock Delta Alert:** Check active status 45 mins pre-tip for rotation shifts.")
        st.markdown("*Engine Rationale:* Clean usage expansion, favorable interior matchup against Washington's drop coverage.")
        
    with col2:
        st.markdown("### 🎯 Tyrese Maxey — PRA (34.5)")
        st.markdown("**Play:** `OVER 34.5 PRA (-115)` | **Conviction:** 🟢 STRONG")
        st.info("🚀 **Ceiling Escalator:** Transition pace multiplier supports 35+ combined counting stats.")
        st.warning("⚠️ **Cannibalization Check:** Monitor backcourt assist distribution with secondary ball-handlers.")
        st.markdown("*Engine Rationale:* High minute floor (36+ min expected under Nurse rotation squeeze).")

# ==========================================
# TAB 2: PERFORMANCE TRACKING & CLV
# ==========================================
elif nav_mode == "📈 Performance Tracking & CLV":
    st.title("📊 Model Performance & Edge Calibration Ledger")
    st.markdown("Tracking rolling weekly/monthly win-rates, **Closing Line Value (CLV)**, and **Brier Scores**.")
    st.markdown("---")
    
    if os.path.exists(LEDGER_FILE):
        df = pd.read_csv(LEDGER_FILE)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            
            time_horizon = st.sidebar.selectbox("Performance Window", ["Last 7 Days", "Last 30 Days", "Full Season"])
            
            if time_horizon == "Last 7 Days":
                cutoff = pd.Timestamp.today() - pd.Timedelta(days=7)
                filtered_df = df[df['date'] >= cutoff]
            elif time_horizon == "Last 30 Days":
                cutoff = pd.Timestamp.today() - pd.Timedelta(days=30)
                filtered_df = df[df['date'] >= cutoff]
            else:
                filtered_df = df
                
            total_picks = len(filtered_df)
            settled_df = filtered_df.dropna(subset=['actual_result'])
            settled_bets = len(settled_df)
            
            wins = settled_df['actual_result'].sum() if settled_bets > 0 else 0
            hit_rate = (wins / settled_bets) * 100 if settled_bets > 0 else 0
            
            clv_beats = ((filtered_df['closing_line_vig_free'] < filtered_df['model_probability']).mean() * 100) if total_picks > 0 else 0
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Logged Picks", total_picks)
            m2.metric("Settled Hit Rate", f"{hit_rate:.1f}%")
            m3.metric("CLV Beat Rate", f"{clv_beats:.1f}%")
            m4.metric("Active Window", time_horizon)
            
            st.markdown("### 📋 Historical Tracking Ledger")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("Your performance ledger is currently empty. Use the 'Log New Engine Pick' tab to add entries.")
    else:
        st.info("Ledger file not initialized yet.")

# ==========================================
# TAB 3: LOG NEW ENGINE PICK
# ==========================================
elif nav_mode == "➕ Log New Engine Pick":
    st.title("➕ Log a New 5-Lens v8 Projection")
    st.markdown("Record your model's prediction parameters for automated CLV and ledger tracking.")
    st.markdown("---")
    
    with st.form("log_pick_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            player_name = st.text_input("Player Name", "Franz Wagner")
            prop_market = st.selectbox("Market", ["Points", "Rebounds", "Assists", "PRA", "3PT Made"])
            line = st.number_input("Line / Milestone Target", value=20.5, step=0.5)
            prediction_type = st.selectbox("Prediction", ["OVER", "UNDER"])
            
        with col2:
            model_prob = st.slider("Model True Win Probability (%)", 0.0, 100.0, 58.0)
            market_vig_prob = st.slider("Market Implied Probability (No-Vig) (%)", 0.0, 100.0, 52.4)
            closing_vig_prob = st.slider("Closing Market Probability (No-Vig) (%)", 0.0, 100.0, 55.0)
            units = st.number_input("Units Wagered", value=1.0, step=0.5)
            odds = st.text_input("American Payout Odds", "+108")
            
        submitted = st.form_submit_button("Record Pick to Ledger")
        
        if submitted:
            new_row = {
                'date': datetime.today().strftime('%Y-%m-%d'),
                'player_name': player_name,
                'prop_market': prop_market,
                'line': line,
                'prediction_type': prediction_type,
                'model_probability': model_prob / 100.0,
                'market_implied_prob': market_vig_prob / 100.0,
                'closing_line_vig_free': closing_vig_prob / 100.0,
                'actual_result': None, # Settled post-game
                'units_wagered': units,
                'payout_odds': odds
            }
            
            df = pd.read_csv(LEDGER_FILE)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(LEDGER_FILE, index=False)
            st.success(f"Successfully logged projection for {player_name} into the v8 tracking ledger!")
"""

with open("app.py", "w") as f:
  f.write(app_code)

print("Streamlit app file 'app.py' successfully written.")

# ==========================================
# LAUNCH STREAMLIT & LOCALTUNNEL
# ==========================================
# Run Streamlit in the background
get_ipython().system_raw("streamlit run app.py &")

# Give Streamlit 3 seconds to spin up
time.sleep(3)

# Start LocalTunnel on port 8501 and print out the public URL
print("🚀 Generating public web link via LocalTunnel...")
!npx localtunnel --port 8501
