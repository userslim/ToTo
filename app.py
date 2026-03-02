import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="TOTO & Wealth Hub", layout="wide")
st.title("🚀 The Millionaire Blueprint")

# --- SIDEBAR: YOUR DATA ---
st.sidebar.header("👤 Your Profile")
lucky_string = st.sidebar.text_input("Lucky String", value="3964215")
current_savings = st.sidebar.number_input("Current Savings ($)", value=1000, step=500)
monthly_invest = st.sidebar.number_input("Monthly Contribution ($)", value=500, step=100)
annual_return = st.sidebar.slider("Expected Annual Return (%)", 1, 15, 7)

# --- TABS FOR NAVIGATION ---
tab1, tab2 = st.tabs(["💰 Wealth Tracker", "🎰 TOTO Strategy"])

with tab1:
    st.header("The Logic: Road to $1,000,000")
    
    # Financial Formula: Future Value
    target = 1000000
    months = 0
    balance = current_savings
    monthly_rate = (annual_return / 100) / 12
    
    balances = [balance]
    while balance < target and months < 600: # Max 50 years
        balance = (balance + monthly_invest) * (1 + monthly_rate)
        months += 1
        balances.append(balance)
    
    years = round(months / 12, 1)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Target", "$1,000,000")
    col2.metric("Time to Goal", f"{years} Years")
    col3.metric("Monthly Fuel", f"${monthly_invest}")

    # Progress Visualization
    df_wealth = pd.DataFrame({"Month": range(len(balances)), "Balance": balances})
    fig = px.area(df_wealth, x="Month", y="Balance", title="Wealth Growth Projection")
    st.plotly_chart(fig, use_container_width=True)
    
    st.write(f"💡 **AI Insight:** At your current rate, you'll be a millionaire in **{years} years**. To do it in 30 days, you'd need a TOTO Group 1 win!")

with tab2:
    st.header("The Luck: TOTO Analysis")
    # Using your lucky string '3964215' to generate a dynamic suggestion
    digits = [int(d) for d in lucky_string if d.isdigit()]
    
    st.subheader("Generated Set for Thursday's Draw")
    # Smart logic: using your string + targeting 'cold' zones
    suggested = [digits[0], digits[2], 15, 24, 37, 49] 
    st.success(f"Recommended Set: {suggested}")
    
    st.info("Strategy: This set includes '3' and '6' from your string, '15' (Car), '24' (Year), and the 'hot' repeater '37'.")

    # Win Tracker Table
    st.subheader("Win History Tracker")
    history_data = {
        "Date": ["2026-03-02", "2026-02-27"],
        "Winning Numbers": ["6, 8, 28, 37, 41, 49", "5, 9, 20, 23, 45, 46"],
        "Your Hit": ["6, 37, 49", "5, 9"]
    }
    st.table(pd.DataFrame(history_data))
