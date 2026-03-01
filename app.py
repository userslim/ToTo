import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="TOTO Analytics Hub", layout="wide")
st.title("🎰 TOTO Personal Strategy Dashboard")

# --- SIDEBAR: USER INPUTS ---
st.sidebar.header("Your Lucky Profile")
lucky_string = st.sidebar.text_input("Enter Lucky String", value="3964215")
unit_no = st.sidebar.text_input("Unit No", value="02-73")

st.sidebar.markdown("---")
st.sidebar.caption("⚠️ This tool is for entertainment only. No guarantee of winning.")

# --- DATA LOADING (with caching and fallback) ---
DATA_URL = "https://raw.githubusercontent.com/yourusername/toto-data/main/toto_results.csv"  # Replace with your actual URL

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_URL)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date', ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        st.warning("Could not load remote data. Using sample data (last 4 draws).")
        # Fallback mock data
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
        df['Date'] = pd.to_datetime(df['Date'])
        return df

with st.spinner("Loading historical data..."):
    df = load_data()

# --- PREPARE FREQUENCY DATA ---
all_numbers = df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
freq_all = pd.Series(all_numbers).value_counts().sort_index()
hot_numbers = freq_all.nlargest(10).index.tolist()
cold_numbers = freq_all.nsmallest(10).index.tolist()

# --- HELPER FUNCTIONS FOR NUMBER GENERATION ---
def numbers_from_profile(lucky_str, unit_str, freq_series):
    """
    Generate 6 numbers based on lucky string, unit number, and hot numbers.
    """
    # Extract digits from lucky string
    lucky_digits = [int(ch) for ch in lucky_str if ch.isdigit()]
    if not lucky_digits:
        lucky_digits = [3, 9, 6, 4, 2, 1, 5]  # fallback
    base = sum(lucky_digits) % 45 + 1  # 1..45

    # Extract digits from unit number
    unit_digits = [int(ch) for ch in unit_str if ch.isdigit()]
    if not unit_digits:
        unit_digits = [0, 2, 7, 3]  # fallback
    unit_sum = sum(unit_digits) % 20

    # Generate candidate numbers
    numbers = []
    for i in range(10):  # generate extra to ensure uniqueness
        num = (base + i * unit_sum + (i+1)*7) % 49
        if num == 0:
            num = 49
        numbers.append(num)

    # Remove duplicates and keep first 6
    unique_nums = []
    for n in numbers:
        if n not in unique_nums:
            unique_nums.append(n)
        if len(unique_nums) == 6:
            break

    # If we don't have 6, fill with hottest numbers (ensuring they aren't already chosen)
    hot_list = hot_numbers  # use global hot_numbers
    i = 0
    while len(unique_nums) < 6 and i < len(hot_list):
        if hot_list[i] not in unique_nums:
            unique_nums.append(hot_list[i])
        i += 1

    return sorted(unique_nums[:6])

def weighted_random_selection(freq_series, n=6):
    """Pick n numbers weighted by historical frequency."""
    probs = freq_series / freq_series.sum()
    return np.random.choice(freq_series.index, size=n, replace=False, p=probs).tolist()

# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Historical Analysis", "🧠 Smart Generator", "📈 Trends & Patterns"])

# ================= TAB 1: HISTORICAL ANALYSIS =================
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Frequency Analysis (All Numbers)")
        freq_df = freq_all.reset_index()
        freq_df.columns = ['Number', 'Count']
        fig = px.bar(freq_df, x='Number', y='Count', color='Count',
                     title="Number Frequencies in All Draws",
                     color_continuous_scale='blues')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Latest Result")
        latest = df.iloc[0]
        st.success(f"Numbers: {latest['N1']}, {latest['N2']}, {latest['N3']}, {latest['N4']}, {latest['N5']}, {latest['N6']}")
        st.warning(f"Additional: {latest['Add']}")

    # Hot & Cold tables
    st.subheader("🔥 Hot & Cold Numbers")
    colA, colB = st.columns(2)
    with colA:
        st.write("**Top 10 Hot Numbers**")
        st.dataframe(pd.DataFrame({'Number': hot_numbers, 'Frequency': [freq_all[n] for n in hot_numbers]}))
    with colB:
        st.write("**Top 10 Cold Numbers**")
        st.dataframe(pd.DataFrame({'Number': cold_numbers, 'Frequency': [freq_all[n] for n in cold_numbers]}))

# ================= TAB 2: SMART GENERATOR =================
with tab2:
    st.subheader("💡 AI-Powered Recommendations")

    strategy = st.selectbox("Choose prediction strategy",
        ["Profile + Hot Mix", "Most Frequent (Hot)", "Least Frequent (Cold)", "Random Weighted"])

    if st.button("Generate Set"):
        if strategy == "Profile + Hot Mix":
            rec_set = numbers_from_profile(lucky_string, unit_no, freq_all)
            explanation = "Derived from your lucky string + unit number, blended with historical hot numbers."
        elif strategy == "Most Frequent (Hot)":
            rec_set = hot_numbers[:6]
            explanation = "Top 6 most frequently drawn numbers overall."
        elif strategy == "Least Frequent (Cold)":
            rec_set = cold_numbers[:6]
            explanation = "Top 6 least frequently drawn numbers (cold numbers)."
        else:  # Random Weighted
            rec_set = weighted_random_selection(freq_all, 6)
            explanation = "Random selection weighted by historical frequency."

        st.code(" , ".join(map(str, rec_set)), language="python")
        st.info(explanation)

# ================= TAB 3: TRENDS & PATTERNS =================
with tab3:
    st.subheader("Number Trends Over Time")
    # Scatter plot of all numbers drawn per draw
    draw_numbers = df.melt(id_vars=['Date'], value_vars=['N1','N2','N3','N4','N5','N6'],
                           var_name='Position', value_name='Number')
    fig_scatter = px.scatter(draw_numbers, x='Date', y='Number', color='Position',
                             title="All Numbers by Draw Date",
                             hover_data=['Position'])
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Position-wise Frequency Heatmap")
    # Frequency of each number in each position
    pos_counts = df[['N1','N2','N3','N4','N5','N6']].apply(pd.Series.value_counts).fillna(0)
    fig_heatmap = px.imshow(pos_counts.T, text_auto=True, aspect="auto",
                            title="Number Frequency by Draw Position",
                            color_continuous_scale='viridis')
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.subheader("Distribution of Sums")
    df['Sum'] = df[['N1','N2','N3','N4','N5','N6']].sum(axis=1)
    fig_hist = px.histogram(df, x='Sum', nbins=20, title="Histogram of Total Sums (6 numbers)")
    st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("Odd/Even Ratio Over Time")
    df['Odd_Count'] = df[['N1','N2','N3','N4','N5','N6']].apply(lambda row: sum(x%2==1 for x in row), axis=1)
    df['Even_Count'] = 6 - df['Odd_Count']
    fig_odd_even = go.Figure()
    fig_odd_even.add_trace(go.Scatter(x=df['Date'], y=df['Odd_Count'], mode='lines+markers', name='Odd Count'))
    fig_odd_even.add_trace(go.Scatter(x=df['Date'], y=df['Even_Count'], mode='lines+markers', name='Even Count'))  # Fixed typo here
    fig_odd_even.update_layout(title='Odd vs Even Numbers per Draw', xaxis_title='Date', yaxis_title='Count')
    st.plotly_chart(fig_odd_even, use_container_width=True)
