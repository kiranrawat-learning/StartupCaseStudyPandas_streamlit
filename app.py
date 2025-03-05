import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import re

st.set_page_config(layout="wide", page_title='Start Up Analysis')

st.sidebar.title("🚀 Indian Startup Funding Insights")
st.title('"🚀 Unveiling the Future: In-Depth Startup Investment Analysis"')
startup = pd.read_csv('start_up.csv')

# Little bit cleaning what left

startup['Investor_Name'] = startup['Investor_Name'].str.lstrip(" \"#@0123456789")
startup['Startup_Name']=startup['Startup_Name'].str.lstrip(" \"#@0123456789")
startup['Industry_Vertical'] = startup['Industry_Vertical'].fillna('Unknown')
startup['City'] = startup['City'].fillna('Unknown')
startup['Date'] = pd.to_datetime(startup['Date'], errors='coerce')
startup['month']=startup['Date'].dt.month
startup.set_index('Sr No', inplace=True)
investor_list = [i.strip() for i in sorted(set(startup['Investor_Name'].str.split(',').sum())) if i and i.strip()]


def load_overall_ana():
    st.title('Overall Analysis')
    c1, c2 = st.columns(2)

    with c1:
        total_invested_amount = round(startup['Amount_USD'].sum())
        st.metric('Overall Invested Amount', str(total_invested_amount) + ' CR')

    with c2:
        max_amount_in_startup1 = round(
            startup.groupby('Startup_Name')['Amount_USD'].max().sort_values(ascending=False).head(1).values[0])
        st.metric('Overall Max Invested Amount On Startup', str(max_amount_in_startup1) + ' CR')

    c3, c4 = st.columns(2)

    with c3:
        avg_amount_in_startup1 = round(startup.groupby('Startup_Name')['Amount_USD'].sum().mean())
        st.metric('Average Funding', str(avg_amount_in_startup1) + ' CR')

    with c4:
        total = startup['Startup_Name'].nunique()
        st.metric('Total number of Unique Startups', total)

    # Extract year from Date if not already done
    if 'year' not in startup.columns:
        startup['year'] = startup['Date'].dt.year


# Load investments
def Load_Investor_Details(investor):
    filtered_data = startup[startup['Investor_Name'].str.contains(investor, na=False)]
    if len(filtered_data) == 0:
        st.warning("No data available for this investor.")
    else:
        st.title(investor)
        investor_investment = startup[startup['Investor_Name'].str.contains(investor)][
            ['Date', 'Startup_Name', 'Industry_Vertical', 'City', 'Amount_USD']
        ].sort_values(by='Date', ascending=False).head()

        investor_investment['Sr No'] = range(1, len(investor_investment) + 1)
        investor_investment.set_index('Sr No', inplace=True)
        st.subheader('Most Recent Investments')
        st.dataframe(investor_investment)

        col1, col2, col3 = st.columns(3)

        # Startup-wise investments
        with col1:
            made_investment = startup[startup['Investor_Name'].str.contains(investor)].groupby('Startup_Name')[
                'Amount_USD'].sum().sort_values(ascending=False).head()

            st.title('Investments')
            st.dataframe(made_investment)
            fig, ax = plt.subplots()
            ax.bar(made_investment.index, made_investment.values, color='Purple')
            ax.set_ylim(0, made_investment.values.max() + 10000000)

            def y_format(x, pos):
                return f'${x:,.0f}'

            ax.yaxis.set_major_formatter(FuncFormatter(y_format))
            st.pyplot(fig)

        # Sector-wise investments
        with col2:
            sector_investments = startup[startup['Investor_Name'].str.contains(investor)].groupby('Industry_Vertical')[
                'Amount_USD'].sum().sort_values(ascending=False).head()
            st.title('Sector Investments in')
            st.write(sector_investments)
            fig1, ax1 = plt.subplots(figsize=(15, 10))
            ax1.pie(sector_investments.values, labels=sector_investments.index, autopct='%1.2f%%')
            st.pyplot(fig1)

        # Round-wise investments
        with col3:
            round_investments = startup[startup['Investor_Name'].str.contains(investor)].groupby('Investment_Type')[
                'Amount_USD'].sum().sort_values(ascending=False).head()
            st.title('Stage Invested in ')
            fig2, ax2 = plt.subplots(figsize=(15, 10))
            ax2.pie(round_investments.values, labels=round_investments.index, autopct='%1.2f%%')
            st.pyplot(fig2)

        col11, col22 = st.columns(2)

        # City-wise investments
        with col11:
            city = startup[startup['Investor_Name'].str.contains(investor)].groupby('City')[
                'Amount_USD'].sum().sort_values(ascending=False).head()
            st.title('City Invested in ')
            fig3, ax3 = plt.subplots(figsize=(5, 5))
            ax3.bar(city.index, city.values, color='red')
            ax3.set_ylim(0, city.values.max() + 10000000)

            def yy_format(x, pos):
                return f'${x:,.0f}'

            ax3.yaxis.set_major_formatter(FuncFormatter(yy_format))
            st.pyplot(fig3)

        # Year-wise investments
        with col22:
            year_wise = startup[startup['Investor_Name'].str.contains(investor)].groupby('year')[
                'Amount_USD'].sum()
           
            st.title('Year by Year Investment')
            fig4, ax4 = plt.subplots(figsize=(15, 10))
            ax4.plot(year_wise.index, year_wise.values, marker='o',linewidth=7,color='red')
            ax4.yaxis.set_major_formatter(FuncFormatter(yy_format))
            st.pyplot(fig4)



# Layout
option = st.sidebar.radio("🔎 Choose Analysis Type:", ["📊 Overview", "🏢 Startup Insights", "💰 Investor Analysis"])

if option == "📊 Overview":

    b0=st.sidebar.button('Show Overall Analysis')
    if b0:
        load_overall_ana()

elif option == "🏢 Startup Insights":
    st.sidebar.selectbox('Select Startup', sorted(startup['Startup_Name'].unique().tolist()))
    b1 = st.sidebar.button('Find Startup Details')
    st.title('StartUp Analysis')
else:
    selected_investor = st.sidebar.selectbox('Select Investor', investor_list)
    st.title('Investor Analysis')
    b2 = st.sidebar.button('Find Investor Details')
    if b2:
        Load_Investor_Details(selected_investor)
