import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(layout="wide",page_title='Start Up Analysis')

st.sidebar.title("🚀 Indian Startup Funding Insights")
startup = pd.read_csv("cleaned_Indian_Startup_Funding.csv")

#littlebit cleaning what left
startup['Investor_Name'] = startup['Investor_Name'].str.lstrip(" \"#@0123456789")
startup.drop(columns=['Remarks'],inplace=True)
startup.set_index('Sr No',inplace=True)
startup['Date']=pd.to_datetime(startup['Date'])
startup['Year']=startup['Date'].dt.year

# load investments
def Load_Investor_Details(investor):
    st.title(investor)
    investor_investment =startup[startup['Investor_Name'].str.contains(investor)][['Date','Startup_Name','Industry_Vertical','City','Amount_USD']].sort_values(by='Date',ascending=False).head()
    investor_investment['Sr No']=range(1,len(investor_investment)+1)
    investor_investment.set_index('Sr No',inplace=True)
    st.subheader('Most Recent Investments')
    st.dataframe(investor_investment)


#investmenets amount
    col1,col2,col3=st.columns(3)
    #start up wise
    with col1:
        made_investment=startup[startup['Investor_Name'].str.contains(investor)].groupby('Startup_Name')[
        'Amount_USD'].sum().sort_values(ascending=False).head()
        st.title('Investments')
        st.dataframe(made_investment)
        fig, ax = plt.subplots()
        ax.bar(made_investment.index, made_investment.values, color='Purple')
        ax.set_ylim(0,made_investment.values.max()+10000000)
        def y_format(x,pos):
         return f'${x:,.0f}'
        ax.yaxis.set_major_formatter(FuncFormatter(y_format))
        st.pyplot(fig)
# sector wise
    with col2:
        sector_investments = startup[startup['Investor_Name'].str.contains(investor)].groupby('Industry_Vertical')[
            'Amount_USD'].sum().sort_values(ascending=False).head()
        st.title('Sector Investments in')
        fig1, ax1 = plt.subplots(figsize=(15,10))
        ax1.pie(sector_investments.values,labels=sector_investments.index,autopct='%1.2f%%')
        st.pyplot(fig1)
#round wise
    with col3:
        round_investments = startup[startup['Investor_Name'].str.contains(investor)].groupby('Investment_Type')[
            'Amount_USD'].sum().sort_values(ascending=False).head()
        st.title('Stage Invested in ')
        fig2, ax2 = plt.subplots(figsize=(15, 10))
        ax2.pie(round_investments.values, labels=round_investments.index, autopct='%1.2f%%')
        st.pyplot(fig2)
#city wise
    city = startup[startup['Investor_Name'].str.contains(investor)].groupby('City')[
        'Amount_USD'].sum().sort_values(ascending=False).head()
    st.title('City Invested in ')
    fig3, ax3 = plt.subplots(figsize=(5,5))
    ax3.bar(city.index,city.values,color='red')
    ax3.set_ylim(0, city.values.max() + 10000000)
    def yy_format(x, pos):
        return f'${x:,.0f}'

    ax3.yaxis.set_major_formatter(FuncFormatter(yy_format))

    st.pyplot(fig3)


#layout

option = st.sidebar.radio("🔎 Choose Analysis Type:",
                          ["📊 Overview", "🏢 Startup Insights", "💰 Investor Analysis"])
if option=="📊 Overview":
    st.title("Overall Analysis")
elif option=="🏢 Startup Insights":
    st.sidebar.selectbox('Select Startup', sorted(startup['Startup_Name'].unique().tolist()))
    b1=st.sidebar.button('Find Startup Details')
    st.title('StartUp Analysis')

else :
    selected_investor=st.sidebar.selectbox('Select Investor', sorted(set(startup['Investor_Name'].str.split(',').sum())))
    st.title('Investor Analysis')
    b2=st.sidebar.button('Find Investor Details')
    if b2:
        Load_Investor_Details(selected_investor)

