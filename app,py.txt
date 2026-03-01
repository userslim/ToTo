import streamlit as st
import pandas as pd
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="TOTO Analytics Hub", layout="wide")
st.title("🎰 TOTO Personal Strategy Dashboard")

# --- MOCK DATA (In production, load this from your GitHub CSV) ---
# Based on your recent Feb 2026 results
data = {
    'Date': ['2026-02-27', '2026-02-23', '2026-02-19', '2026-02-16'],
    'N1': [5, 24, 8, 13],
    'N2': [9, 26, 16, 24],
    'N3': [20, 30, 17, 28],
    'N4': [23, 32, 34, 34],
    'N5': [45, 37, 38, 37],
    'N6': [46, 47, 48, 44],
    'Add': [7, 2, 25, 29]
}
df = pd.DataFrame(data)

# --- SIDEBAR: PERSONAL INPUTS ---
st.sidebar.header("Your Lucky Profile")
lucky_string = st.sidebar.text_input("Enter Lucky String", value="3964215")
unit_no = st.sidebar.text_input("Unit No", value="02-73")

# --- MAIN TAB 1: HISTORICAL ANALYSIS ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Frequency Analysis")
    all_numbers = df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
    freq_df = pd.Series(all_numbers).value_counts().reset_index()
    freq_df.columns = ['Number', 'Count']
    
    fig = px.bar(freq_df, x='Number', y='Count', color='Count', title="Hot Numbers (Last 4 Draws)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Latest Result")
    latest = df.iloc[0]
    st.success(f"Numbers: {latest['N1']}, {latest['N2']}, {latest['N3']}, {latest['N4']}, {latest['N5']}, {latest['N6']}")
    st.warning(f"Additional: {latest['Add']}")

# --- MAIN TAB 2: SMART GENERATOR ---
st.divider()
st.subheader("💡 AI-Powered Recommendations")

if st.button("Generate Set from My Profile"):
    # Logic mixing your string '3964215' and '02-73'
    # This is a simplified example of the logic we discussed
    set_1 = [1, 6, 11, 24, 39, 43] # Logic: 1 (Aug), 6 (string), 11 (Nov), 24 (2024), 39 (string), 43 (unit sum)
    st.write("### Recommended Set for Monday:")
    st.code(" , ".join(map(str, set_1)), language="python")
    st.info("Strategy: Targeting 'Quiet' 10s and 30s zones based on Hong Bao results.")