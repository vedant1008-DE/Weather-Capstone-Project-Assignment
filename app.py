import streamlit as st
import plotly.express as px
from transformer import load_last_30_hours
st.set_page_config(page_title='Weather — Last 30 days - Vedant', layout='wide')
st.title('Weather — Last 30 Days (City) - Vedant Sasane')
city = st.text_input('City', 'Mumbai')
if st.button('Load data'):
    df = load_last_30_hours(city)
    if df.empty:
        st.error('No data found. Run fetcher backfill first.')
    else:
        st.subheader('Temperature (hourly)')
        df['rolling_24'] = df['temp_c'].rolling(24).mean()
        fig = px.line(df.reset_index(), x='obs_time', y='temp_c', labels={'obs_time':'Time','temp_c':'Temperature (C)'})
        fig.add_scatter(x=df.index, y=df['rolling_24'], mode='lines', name='24h rolling')
        st.plotly_chart(fig, use_container_width=True)
        st.subheader('Humidity')
        fig2 = px.line(df.reset_index(), x='obs_time', y='humidity_pct', labels={'humidity_pct':'Humidity (%)'})
        st.plotly_chart(fig2, use_container_width=True)
        st.subheader('Daily precipitation (sum)')
        daily_precip = df['precipitation_mm'].resample('D').sum().reset_index()
        fig3 = px.bar(daily_precip, x='obs_time', y='precipitation_mm', labels={'precipitation_mm':'Precipitation (mm)','obs_time':'Date'})
        st.plotly_chart(fig3, use_container_width=True)
