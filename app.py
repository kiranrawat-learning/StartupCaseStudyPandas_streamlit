import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import re
def clean_text(text):
    if isinstance(text, str):
        text = text.encode("ascii", "ignore").decode()  # Remove weird symbols
        return text.strip().upper()  # Remove spaces & make uppercase
    return text

st.set_page_config(layout="wide", page_title='Start Up Analysis')

st.sidebar.title("🚀 Indian Startup Funding Insights")
st.title('"🚀 Unveiling the Future: In-Depth Startup Investment Analysis"')
startup = pd.read_csv('start_up.csv', encoding='utf-8')

# Clean Startup Names & Investor Names
startup['Startup_Name'] = startup['Startup_Name'].apply(clean_text)
startup['Investor_Name'] = startup['Investor_Name'].apply(clean_text)
# Function to clean investor names
def clean_investor_names(name):
    if isinstance(name, str):
        name = name.encode("ascii", "ignore").decode()  # Remove weird characters
        name = name.replace(" Pvt Ltd", "").replace(" Limited", "").replace(" LLP", "")  # Remove legal suffixes
        name = re.sub(r'[^A-Za-z0-9& ]+', '', name)  # Remove special characters
        return name.strip().upper()  # Standardize case
    return name

# Apply the cleaning function
startup['Investor_Name'] = startup['Investor_Name'].apply(clean_investor_names)

# Split multiple investors and create a unique sorted list
investor_list = sorted(set(sum([i.split(",") for i in startup['Investor_Name'].dropna()], [])))
investor_list = [i.strip() for i in investor_list if i]  # Remove extra spaces


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
        st.metric('Overall Invested Amount', f"${total_invested_amount:,.0f}")

    with c2:
        max_amount_in_startup1 = round(
            startup.groupby('Startup_Name')['Amount_USD'].max().sort_values(ascending=False).head(1).values[0])
        st.metric('Overall Max Invested Amount On Startup', f'${max_amount_in_startup1:,.0f}')

    c3, c4 = st.columns(2)

    with c3:
        avg_amount_in_startup1 = round(startup.groupby('Startup_Name')['Amount_USD'].sum().mean())
        st.metric('Average Funding', f'${avg_amount_in_startup1:,.0f}')

    #Startup Funding Analysis:Total Funding Amount Over Time
    st.subheader("📊 Startup Funding Analysis:Total Funding Amount Over Time")
    num_of_amount = startup.groupby(['year', 'month'])['Amount_USD'].sum().reset_index()

    # Create x-axis labels (Month-Year format)
    num_of_amount['x-axis'] = num_of_amount['month'].astype(str) + "-" + num_of_amount['year'].astype(str)
    fig, ax = plt.subplots(figsize=(19, 10))
    ax.plot(num_of_amount['x-axis'], num_of_amount['Amount_USD'], marker='o', linestyle='-', color='b')
    ax.set_title("Total Funding Amount Over Time")
    ax.set_ylabel("Total Investment (USD)")
    def yy_format(x, pos):
      return f'${x:,.0f}'
    ax.yaxis.set_major_formatter(FuncFormatter(yy_format))
    plt.xticks(rotation=90)
    ax.legend()
    st.pyplot(fig)

    # Startup Funding Analysis:Number of Fundings Over Time

    st.subheader("📊 Startup Funding Analysis:Number of Fundings Over Time")
    num_of_funding = startup.groupby(['year', 'month'])['Startup_Name'].count().reset_index()
    num_of_funding['x-axis'] = num_of_funding['month'].astype(str) + "-" + num_of_funding['year'].astype(str)
    fig, ax = plt.subplots(figsize=(19, 10))
    ax.plot(num_of_funding['x-axis'], num_of_funding['Startup_Name'], marker='s', linestyle='-', color='g')
    ax.set_title("Number of Fundings Over Time")
    ax.set_ylabel("Number of Fundings")

    ax.set_xlabel("Month-Year")
    plt.xticks(rotation=90)  # Rotate labels for better visibility
    ax.legend()
    st.pyplot(fig)

#startup insights
def load_startup_details(selected_startup):
    st.title(f'📊 Startup Insights: {selected_startup}')

    # Filter data for the selected startup
    startup_data = startup[startup['Startup_Name'] == selected_startup]

    if startup_data.empty:
        st.warning("No data available for this startup.")
    else:
        st.subheader("📝 Startup Details")
        st.dataframe(
            startup_data[['Date', 'Industry_Vertical', 'City', 'Investment_Type', 'Amount_USD']]
            .sort_values(by='Date', ascending=False))

        # Total Investment in the Startup

        total_funding = startup_data['Amount_USD'].sum()
        st.metric("💰 Total Funding Received", f"${total_funding:,.0f}")

        #Top 5 Investors
        st.subheader("💼 Top Investors")
        top_investors = startup_data['Investor_Name'].value_counts().head(5)
        st.write(top_investors)

        # Yearly Funding Trend
        st.subheader("📈 Yearly Funding Trend")
        yearly_funding = startup_data.groupby(startup_data['Date'].dt.year)['Amount_USD'].sum()
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(yearly_funding.index, yearly_funding.values, marker='o', linestyle='-', color='b')
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Total Investment (USD)")
        ax1.set_title("Total Investment Over Years")
        st.pyplot(fig1)

        # City-wise Investment Distribution
        st.subheader("🏙️ City-wise Investment Distribution")
        city_investment = startup_data.groupby('City')['Amount_USD'].sum().sort_values(ascending=False).head(5)
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.bar(city_investment.index, city_investment.values, color='g')
        ax2.set_ylabel("Total Investment (USD)")
        ax2.set_title("Top 5 Cities for Investment")
        st.pyplot(fig2)

        #Investment Round Distribution
        st.subheader("🏦 Investment Round Distribution")
        round_distribution = startup_data['Investment_Type'].value_counts()
        fig3, ax3 = plt.subplots(figsize=(8, 8))
        ax3.pie(round_distribution.values, labels=round_distribution.index, autopct='%1.1f%%',
                colors=['red', 'blue', 'green', 'purple'])
        ax3.set_title("Investment Rounds Breakdown")
        st.pyplot(fig3)

    # Extract year from Date if not already done
if 'year' not in startup.columns:
    startup['year'] = startup['Date'].dt.year


# Load investments
def Load_Investor_Details(investor):
    st.title(f'💼Investor Analysis : {investor}')
    filtered_data = startup[startup['Investor_Name'].str.contains(investor, na=False)]
    if filtered_data.empty:
        st.warning("No data available for this startup.")

    else:

        investor_investment = startup[startup['Investor_Name'].str.contains(investor)][
            ['Date', 'Startup_Name', 'Industry_Vertical', 'City', 'Amount_USD']
        ].sort_values(by='Date', ascending=False).head()

        investor_investment['Sr No'] = range(1, len(investor_investment) + 1)
        investor_investment.set_index('Sr No', inplace=True)
        st.subheader('📝Most Recent Investments')
        st.dataframe(investor_investment)

        col1, col2, col3 = st.columns(3)

        # Startup-wise investments
        with col1:
            made_investment = startup[startup['Investor_Name'].str.contains(investor)].groupby('Startup_Name')[
                'Amount_USD'].sum().sort_values(ascending=False).head()

            st.title('💼Investments')
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
            st.title('🏦 Stage Invested in ')
            fig2, ax2 = plt.subplots(figsize=(15, 10))
            ax2.pie(round_investments.values, labels=round_investments.index, autopct='%1.2f%%')
            st.pyplot(fig2)

        col11, col22 = st.columns(2)

        # City-wise investments
        with col11:
            city = startup[startup['Investor_Name'].str.contains(investor)].groupby('City')[
                'Amount_USD'].sum().sort_values(ascending=False).head()
            st.title('🏙️ City Invested in ')
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

            st.title('📈Year by Year Investment')
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
    selected_startup=st.sidebar.selectbox('Select Startup', sorted(startup['Startup_Name'].unique().tolist()))
    b1 = st.sidebar.button('Find Startup Details')
    if b1:
        load_startup_details(selected_startup)


else:
    selected_investor = st.sidebar.selectbox('Select Investor', investor_list)

    b2 = st.sidebar.button('Find Investor Details')
    if b2:
        Load_Investor_Details(selected_investor)
