import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# Set Page Config
st.set_page_config(layout="wide", page_title="Indian Startup Funding Insights")


# Load dataset with caching
@st.cache_data
def load_data():
    df = pd.read_csv('start_up.csv')
    df['Investor_Name'] = df['Investor_Name'].str.lstrip(" \"#@0123456789")
    df['year'] = df['year'].astype(str).str.replace(',', '', regex=True).astype(int)
    df['Industry_Vertical'] = df['Industry_Vertical'].fillna('Unknown')
    df['City'] = df['City'].fillna('Unknown')
    df.set_index('Sr No', inplace=True)
    return df


startup = load_data()

# Sidebar Title
st.sidebar.title("🚀 Indian Startup Funding Insights")

# Investor List Cleanup
investor_list = [i.strip() for i in sorted(set(startup['Investor_Name'].str.split(',').sum())) if i and i.strip()]


# Investor Analysis Function
def Load_Investor_Details(investor):
    filtered_data = startup[startup['Investor_Name'].str.contains(investor, na=False)]
    if filtered_data.empty:
        st.warning("No data available for this investor.")
        return

    st.header(f"💰 Investor Analysis: {investor}")

    # Recent Investments
    st.subheader("Most Recent Investments")
    investor_investment = filtered_data[
        ['Date', 'Startup_Name', 'Industry_Vertical', 'City', 'Amount_USD']].sort_values(by='Date',
                                                                                         ascending=False).head(5)
    st.dataframe(investor_investment)

    col1, col2, col3 = st.columns(3)

    # Startup-wise Investments
    with col1:
        startup_investment = filtered_data.groupby('Startup_Name')['Amount_USD'].sum().sort_values(
            ascending=False).head()
        st.subheader("Top Funded Startups")
        st.bar_chart(startup_investment)

    # Sector-wise Investments
    with col2:
        sector_investments = filtered_data.groupby('Industry_Vertical')['Amount_USD'].sum().sort_values(
            ascending=False).head()
        st.subheader("Sector-wise Investment")
        fig, ax = plt.subplots()
        ax.pie(sector_investments, labels=sector_investments.index, autopct='%1.2f%%',
               colors=sns.color_palette("pastel"))
        st.pyplot(fig)

    # Round-wise Investments
    with col3:
        round_investments = filtered_data.groupby('Investment_Type')['Amount_USD'].sum().sort_values(
            ascending=False).head()
        st.subheader("Funding Rounds Investment")
        fig, ax = plt.subplots()
        ax.pie(round_investments, labels=round_investments.index, autopct='%1.2f%%',
               colors=sns.color_palette("coolwarm"))
        st.pyplot(fig)

    col4, col5 = st.columns(2)

    # City-wise Investments
    with col4:
        city_investments = filtered_data.groupby('City')['Amount_USD'].sum().sort_values(ascending=False).head()
        st.subheader("Top Cities for Investment")
        st.bar_chart(city_investments)

    # Year-wise Investments
    with col5:
        year_wise = filtered_data.groupby('year')['Amount_USD'].sum()
        st.subheader("Yearly Investment Trend")
        st.line_chart(year_wise)


# Sidebar Menu
option = st.sidebar.radio("🔎 Choose Analysis Type:", ["📊 Overview", "🏢 Startup Insights", "💰 Investor Analysis"])

if option == "📊 Overview":
    st.title("📊 Indian Startup Funding Overview")

    # Top Funded Startups
    st.subheader("Top 10 Funded Startups")
    top_funded = startup.groupby("Startup_Name")["Amount_USD"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_funded)

    # Funding Trends Over Time
    st.subheader("Funding Trends Over Time")
    yearly_funding = startup.groupby("year")["Amount_USD"].sum()
    st.line_chart(yearly_funding)

elif option == "🏢 Startup Insights":
    startup_selected = st.sidebar.selectbox('Select Startup', sorted(startup['Startup_Name'].unique().tolist()))
    st.title(f"🏢 {startup_selected} Analysis")
    st.dataframe(startup[startup['Startup_Name'] == startup_selected])

elif option == "💰 Investor Analysis":
    selected_investor = st.sidebar.selectbox("Select Investor", investor_list)
    if st.sidebar.button("Find Investor Details"):
        Load_Investor_Details(selected_investor)

