import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Millionaire Blueprint", layout="wide")
st.title("🚀 The Millionaire Blueprint")

# --- SIDEBAR: ALL INPUTS ---
st.sidebar.header("👤 Your Profile")

# Personal luck inputs
lucky_string = st.sidebar.text_input("Lucky String", value="3964215")
unit_no = st.sidebar.text_input("Unit No", value="02-73")
carplate = st.sidebar.text_input("Carplate No (optional)", value="")
mobile = st.sidebar.text_input("Mobile No (optional)", value="")

st.sidebar.markdown("---")
st.sidebar.header("💰 Wealth Parameters")
current_savings = st.sidebar.number_input("Current Savings ($)", value=1000, step=500)
monthly_invest = st.sidebar.number_input("Monthly Contribution ($)", value=500, step=100)
annual_return = st.sidebar.slider("Expected Annual Return (%)", 1, 15, 7)

st.sidebar.markdown("---")
st.sidebar.header("📁 Data Source")
uploaded_file_toto = st.sidebar.file_uploader("Upload TOTO results CSV", type=["csv"], key="toto")
uploaded_file_4d = st.sidebar.file_uploader("Upload 4D results CSV", type=["csv"], key="4d")

st.sidebar.markdown("---")
st.sidebar.caption("⚠️ This tool is for entertainment only. No guarantee of winning.")

# --- DEFAULT DATA URLs (replace with your own) ---
TOTO_DATA_URL = "https://raw.githubusercontent.com/yourusername/toto-data/main/toto_results.csv"
FOURD_DATA_URL = "https://raw.githubusercontent.com/yourusername/4d-data/main/4d_results.csv"

# ================= DATA LOADING FUNCTIONS =================
@st.cache_data
def load_toto_data(uploaded_file, url):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv(url)
    return standardise_toto_columns(df)

def standardise_toto_columns(df):
    df = df.copy()
    # Date column
    date_col = None
    for col in df.columns:
        if col.lower() in ['date', 'drawdate', 'draw date']:
            date_col = col
            break
    if date_col is None:
        st.error("TOTO CSV missing Date column.")
        st.stop()
    df.rename(columns={date_col: 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])

    # Number columns N1..N6
    for i in range(1, 7):
        found = False
        for col in df.columns:
            if col.lower() in [f'n{i}', f'number{i}', f'num{i}']:
                df.rename(columns={col: f'N{i}'}, inplace=True)
                found = True
                break
        if not found:
            st.error(f"TOTO CSV missing column N{i}.")
            st.stop()

    # Additional number
    add_col = None
    for col in df.columns:
        if col.lower() in ['add', 'additional', 'add1']:
            add_col = col
            break
    if add_col:
        df.rename(columns={add_col: 'Add'}, inplace=True)
    else:
        df['Add'] = np.nan

    df = df.sort_values('Date', ascending=False).reset_index(drop=True)
    return df

@st.cache_data
def load_4d_data(uploaded_file, url):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv(url)
    return standardise_4d_columns(df)

def standardise_4d_columns(df):
    df = df.copy()
    date_col = None
    for col in df.columns:
        if col.lower() in ['date', 'drawdate', 'draw date']:
            date_col = col
            break
    if date_col is None:
        st.error("4D CSV missing Date column.")
        st.stop()
    df.rename(columns={date_col: 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])

    # All other columns are winning numbers
    number_cols = [col for col in df.columns if col != 'Date']
    df.attrs['number_columns'] = number_cols

    df = df.sort_values('Date', ascending=False).reset_index(drop=True)
    return df

# --- Load TOTO data (with fallback) ---
try:
    df_toto = load_toto_data(uploaded_file_toto, TOTO_DATA_URL)
    st.sidebar.success(f"TOTO: {len(df_toto)} draws loaded")
except Exception as e:
    st.warning("TOTO data not available. Using sample data (last 4 draws).")
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
    df_toto = pd.DataFrame(data)
    df_toto['Date'] = pd.to_datetime(df_toto['Date'])

# --- Load 4D data (with fallback) ---
try:
    df_4d = load_4d_data(uploaded_file_4d, FOURD_DATA_URL)
    st.sidebar.success(f"4D: {len(df_4d)} draws loaded")
except Exception as e:
    st.warning("4D data not available. Using sample data (last 4 draws with 23 numbers).")
    np.random.seed(42)
    dates = pd.date_range(end='2026-02-27', periods=4, freq='4D')
    data = {'Date': dates}
    for i in range(1, 24):
        data[f'N{i}'] = np.random.randint(0, 10000, size=4)
    df_4d = pd.DataFrame(data)
    df_4d['Date'] = pd.to_datetime(df_4d['Date'])
    df_4d.attrs['number_columns'] = [f'N{i}' for i in range(1, 24)]

# ================= HELPER FUNCTIONS =================
def fmt_4d(num):
    return f"{int(num):04d}"

# TOTO helpers
all_toto_nums = df_toto[['N1','N2','N3','N4','N5','N6']].values.flatten()
freq_toto = pd.Series(all_toto_nums).value_counts().sort_index()
hot_toto = freq_toto.nlargest(10).index.tolist()
cold_toto = freq_toto.nsmallest(10).index.tolist()

def numbers_from_profile_toto(lucky_str, unit_str, carplate_str, mobile_str, freq_series):
    all_digits = []
    for s in [lucky_str, unit_str, carplate_str, mobile_str]:
        if s:
            all_digits.extend([int(ch) for ch in s if ch.isdigit()])
    if not all_digits:
        all_digits = [3,9,6,4,2,1,5,0,2,7,3]
    base = sum(all_digits) % 45 + 1
    offset_base = sum(all_digits[:5]) % 20 if len(all_digits) >= 5 else sum(all_digits) % 20
    numbers = []
    for i in range(10):
        num = (base + i * offset_base + (i+1)*7) % 49
        if num == 0:
            num = 49
        numbers.append(num)
    unique_nums = []
    for n in numbers:
        if n not in unique_nums:
            unique_nums.append(n)
        if len(unique_nums) == 6:
            break
    hot_list = hot_toto
    i = 0
    while len(unique_nums) < 6 and i < len(hot_list):
        if hot_list[i] not in unique_nums:
            unique_nums.append(hot_list[i])
        i += 1
    return sorted(unique_nums[:6])

def weighted_random_toto(freq_series, n=6):
    probs = freq_series / freq_series.sum()
    return np.random.choice(freq_series.index, size=n, replace=False, p=probs).tolist()

# 4D helpers
all_4d_nums = df_4d[df_4d.attrs['number_columns']].values.flatten().astype(int)
freq_4d = pd.Series(all_4d_nums).value_counts().sort_index()
hot_4d = freq_4d.nlargest(10).index.tolist()
cold_4d = freq_4d.nsmallest(10).index.tolist()

def numbers_from_profile_4d(lucky_str, unit_str, carplate_str, mobile_str, freq_series):
    all_digits = []
    for s in [lucky_str, unit_str, carplate_str, mobile_str]:
        if s:
            all_digits.extend([int(ch) for ch in s if ch.isdigit()])
    if not all_digits:
        all_digits = [3,9,6,4,2,1,5,0,2,7,3]
    seed = 0
    for d in all_digits:
        seed = (seed * 10 + d) % 10000
    if seed == 0:
        seed = 1
    offset = sum(all_digits) % 100
    num = (seed + offset) % 10000
    if num == 0:
        num = 1
    return num

def weighted_random_4d(freq_series, n=1):
    probs = freq_series / freq_series.sum()
    n = min(n, len(freq_series))
    return np.random.choice(freq_series.index, size=n, replace=False, p=probs).tolist()

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(["💰 Wealth Tracker", "🎰 TOTO Analytics", "🔢 4D Predictor"])

# ---------- TAB 1: WEALTH TRACKER ----------
with tab1:
    st.header("The Logic: Road to $1,000,000")
    
    target = 1_000_000
    months = 0
    balance = current_savings
    monthly_rate = (annual_return / 100) / 12
    
    balances = [balance]
    while balance < target and months < 600:  # 50 years max
        balance = (balance + monthly_invest) * (1 + monthly_rate)
        months += 1
        balances.append(balance)
    
    years = round(months / 12, 1)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Target", "$1,000,000")
    col2.metric("Time to Goal", f"{years} Years")
    col3.metric("Monthly Fuel", f"${monthly_invest}")

    df_wealth = pd.DataFrame({"Month": range(len(balances)), "Balance": balances})
    fig = px.area(df_wealth, x="Month", y="Balance", title="Wealth Growth Projection")
    st.plotly_chart(fig, use_container_width=True)
    
    st.write(f"💡 **AI Insight:** At your current rate, you'll be a millionaire in **{years} years**. To do it in 30 days, you'd need a TOTO Group 1 win!")

# ---------- TAB 2: TOTO ANALYTICS ----------
with tab2:
    st.header("🎰 TOTO Analysis & Smart Generator")
    
    sub_tab_a, sub_tab_b, sub_tab_c = st.tabs(["📊 Historical Analysis", "🧠 Smart Generator", "📈 Trends"])
    
    with sub_tab_a:
        col1, col2 = st.columns([2,1])
        with col1:
            freq_df = freq_toto.reset_index()
            freq_df.columns = ['Number', 'Count']
            fig = px.bar(freq_df, x='Number', y='Count', color='Count',
                         title="Number Frequencies (All Draws)", color_continuous_scale='blues')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Latest Result")
            latest = df_toto.iloc[0]
            st.success(f"Numbers: {latest['N1']}, {latest['N2']}, {latest['N3']}, {latest['N4']}, {latest['N5']}, {latest['N6']}")
            add = latest['Add'] if pd.notna(latest['Add']) else 'N/A'
            st.warning(f"Additional: {add}")
        
        st.subheader("🔥 Hot & Cold Numbers")
        colA, colB = st.columns(2)
        with colA:
            st.write("**Top 10 Hot**")
            st.dataframe(pd.DataFrame({'Number': hot_toto, 'Frequency': [freq_toto[n] for n in hot_toto]}))
        with colB:
            st.write("**Top 10 Cold**")
            st.dataframe(pd.DataFrame({'Number': cold_toto, 'Frequency': [freq_toto[n] for n in cold_toto]}))

    with sub_tab_b:
        st.subheader("💡 AI-Powered Recommendations")
        strategy = st.selectbox("Choose strategy", 
            ["Profile + Hot Mix", "Most Frequent (Hot)", "Least Frequent (Cold)", "Random Weighted", "Simple Lucky (from snippet)"])
        
        if st.button("Generate TOTO Set"):
            if strategy == "Profile + Hot Mix":
                rec = numbers_from_profile_toto(lucky_string, unit_no, carplate, mobile, freq_toto)
                expl = "Derived from your lucky inputs, blended with hot numbers."
            elif strategy == "Most Frequent (Hot)":
                rec = hot_toto[:6]
                expl = "Top 6 most frequent numbers."
            elif strategy == "Least Frequent (Cold)":
                rec = cold_toto[:6]
                expl = "Top 6 least frequent numbers."
            elif strategy == "Random Weighted":
                rec = weighted_random_toto(freq_toto, 6)
                expl = "Random weighted by frequency."
            else:  # Simple Lucky
                digits = [int(d) for d in lucky_string if d.isdigit()]
                rec = [digits[0], digits[2], 15, 24, 37, 49]  # from original snippet
                expl = "Simple strategy using your string + cold zones."
            
            st.code(" , ".join(map(str, rec)), language="python")
            st.info(expl)

    with sub_tab_c:
        st.subheader("Number Trends")
        draw_numbers = df_toto.melt(id_vars=['Date'], value_vars=['N1','N2','N3','N4','N5','N6'],
                                    var_name='Position', value_name='Number')
        fig = px.scatter(draw_numbers, x='Date', y='Number', color='Position',
                         title="All Numbers by Draw Date")
        st.plotly_chart(fig, use_container_width=True)

        df_toto['Sum'] = df_toto[['N1','N2','N3','N4','N5','N6']].sum(axis=1)
        fig_hist = px.histogram(df_toto, x='Sum', nbins=20, title="Distribution of Sums")
        st.plotly_chart(fig_hist, use_container_width=True)

# ---------- TAB 3: 4D PREDICTOR ----------
with tab3:
    st.header("🔢 4D Analysis & Predictor")
    
    sub_4d_a, sub_4d_b, sub_4d_c = st.tabs(["📊 Historical Analysis", "🧠 Smart Generator", "📈 Trends"])
    
    with sub_4d_a:
        col1, col2 = st.columns([2,1])
        with col1:
            freq_df_4d = freq_4d.reset_index()
            freq_df_4d.columns = ['Number', 'Count']
            freq_df_4d['Number'] = freq_df_4d['Number'].apply(fmt_4d)
            fig = px.bar(freq_df_4d, x='Number', y='Count', color='Count',
                         title="4D Number Frequencies", color_continuous_scale='blues')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Latest Draw")
            latest = df_4d.iloc[0]
            num_cols = df_4d.attrs['number_columns']
            st.success(f"1st: {fmt_4d(latest[num_cols[0]])}")
            st.success(f"2nd: {fmt_4d(latest[num_cols[1]])}")
            st.success(f"3rd: {fmt_4d(latest[num_cols[2]])}")
        
        st.subheader("🔥 Hot & Cold 4D")
        colA, colB = st.columns(2)
        with colA:
            st.write("**Top 10 Hot**")
            hot_df = pd.DataFrame({'Number': [fmt_4d(n) for n in hot_4d], 'Frequency': [freq_4d[n] for n in hot_4d]})
            st.dataframe(hot_df)
        with colB:
            st.write("**Top 10 Cold**")
            cold_df = pd.DataFrame({'Number': [fmt_4d(n) for n in cold_4d], 'Frequency': [freq_4d[n] for n in cold_4d]})
            st.dataframe(cold_df)

    with sub_4d_b:
        st.subheader("💡 Generate Your 4D Numbers")
        strategy_4d = st.selectbox("Choose 4D strategy", 
            ["Profile + Hot Mix", "Most Frequent (Hot)", "Least Frequent (Cold)", "Random Weighted"])
        num_sets = st.slider("Number of sets", 1, 10, 1)
        
        if st.button("Generate 4D Sets"):
            if strategy_4d == "Profile + Hot Mix":
                base = numbers_from_profile_4d(lucky_string, unit_no, carplate, mobile, freq_4d)
                # For multiple sets, add small variations
                recs = [(base + i) % 10000 for i in range(num_sets)]
                if any(r == 0 for r in recs):  # avoid 0 if desired
                    recs = [1 if r==0 else r for r in recs]
                expl = "Derived from your lucky inputs, with variations."
            elif strategy_4d == "Most Frequent (Hot)":
                recs = hot_4d[:num_sets]
                expl = f"Top {num_sets} hot numbers."
            elif strategy_4d == "Least Frequent (Cold)":
                recs = cold_4d[:num_sets]
                expl = f"Top {num_sets} cold numbers."
            else:  # Random Weighted
                recs = weighted_random_4d(freq_4d, num_sets)
                expl = f"{num_sets} random weighted numbers."
            
            for i, n in enumerate(recs, 1):
                st.code(f"Set {i}: {fmt_4d(n)}", language="python")
            st.info(expl)

    with sub_4d_c:
        st.subheader("4D Trends")
        num_cols = df_4d.attrs['number_columns']
        draw_numbers_4d = df_4d.melt(id_vars=['Date'], value_vars=num_cols,
                                     var_name='Position', value_name='Number')
        draw_numbers_4d['Number'] = draw_numbers_4d['Number'].astype(int)
        fig = px.scatter(draw_numbers_4d, x='Date', y='Number', color='Position',
                         title="All 4D Numbers by Draw Date", opacity=0.6)
        st.plotly_chart(fig, use_container_width=True)

        fig_hist = px.histogram(draw_numbers_4d, x='Number', nbins=50, title="Distribution of 4D Numbers")
        st.plotly_chart(fig_hist, use_container_width=True)

        # First digit distribution
        first_digits = draw_numbers_4d['Number'].astype(str).str[0].fillna('0').astype(int)
        fig_digit = px.histogram(x=first_digits, nbins=10, title="First Digit Frequency")
        st.plotly_chart(fig_digit, use_container_width=True)
