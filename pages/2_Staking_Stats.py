from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title='Aave Dashboard', layout='wide', page_icon=':dollar:')
st.title("Aave Staking(stkAAVE) Dashboard")
st.sidebar.title('Aave Staking')
st.sidebar.markdown("this page Contains the Aave Staking information 🎈")


@st.cache(ttl=6 * 60 * 60)  # 6 hours
def fetch_data(url: str):
    res = requests.get(url=url).json()
    for item in res:
        item['Day'] = datetime.strptime(item['DATE'], '%Y-%m-%d').date()
        item['COLOR'] = item['COLOR']
        item['TOTAL_STAKED_USD'] = int(float(item['TOTAL_STAKED_USD']))
        item['TOTAL_STAKED_AAVE'] = int(float(item['TOTAL_STAKED_AAVE']))
        item['STAKED_CUMU'] = int(float(item['STAKED_CUMU']))
        item['AAVE_STAKED_CUMU'] = int(float(item['AAVE_STAKED_CUMU']))

    return pd.DataFrame(
        res,
        columns=["Day", "TOTAL_STAKED_USD", 'TOTAL_STAKED_AAVE', 'STAKED_CUMU', 'AAVE_STAKED_CUMU', "COLOR"])


def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


def get_delta_color(from_num, to_num):
    return 'inverse' if from_num > to_num else 'normal'


chart_data = fetch_data(
    'https://node-api.flipsidecrypto.com/api/v2/queries/60316905-bca9-4ebc-8459-ac7a20e8eb5c/data/latest')

today_stakes_usd = chart_data.sort_values("Day", ascending=False).head(1)
one_month_ago_stakes = chart_data.loc[chart_data['Day'] == datetime.now().date() - timedelta(days=30)]
one_month_ago_staked_usd = one_month_ago_stakes['STAKED_CUMU'].sum()
today_staked_usd = today_stakes_usd['STAKED_CUMU'].sum()

today_stakes_aave = chart_data.sort_values("Day", ascending=False).head(1)
one_month_ago_stakes_aave = chart_data.loc[chart_data['Day'] == datetime.now().date() - timedelta(days=30)]
one_month_ago_staked_aave = one_month_ago_stakes_aave['AAVE_STAKED_CUMU'].sum()
today_staked_aave = today_stakes_aave['AAVE_STAKED_CUMU'].sum()

# Metrics
c1, c2, c3, c4 = st.columns(4, gap="small")
c1.metric("Current Staked in Aave", "{:,}".format(today_staked_aave))
c2.metric("Aave Staked Changes(1 month)", "{:,}".format(today_staked_aave - one_month_ago_staked_aave),
          f"{round(get_change(today_staked_aave, one_month_ago_staked_aave), 2)}%",
          delta_color=get_delta_color(one_month_ago_staked_aave, today_staked_aave))
c3.metric("Current Staked in USD", "{:,}".format(today_staked_usd))
c4.metric("USD Staked Changes(1 month)", "{:,}".format(today_staked_usd - one_month_ago_staked_usd),
          f"{round(get_change(today_staked_usd, one_month_ago_staked_usd), 2)}%",
          delta_color=get_delta_color(one_month_ago_staked_usd, today_staked_usd))
st.markdown("""---""")
# end metrics

fig = px.area(chart_data, x='Day', y='STAKED_CUMU', title="Aave USD Value Staked over time",
              template='seaborn')
fig.update_traces(mode="lines", hovertemplate=None)
fig.update_layout(hovermode="x unified")
fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=10, t=30), yaxis_title=None, xaxis_title=None)
st.plotly_chart(fig, use_container_width=True)

fig = px.area(chart_data, x='Day', y='AAVE_STAKED_CUMU', title="Aave Amount Staked over time",
              )
fig.update_traces(mode="lines", hovertemplate=None)
fig.update_layout(hovermode="x unified")
fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=10, t=30), yaxis_title=None, xaxis_title=None)
st.plotly_chart(fig, use_container_width=True)

fig = px.bar(chart_data, x='Day', y='TOTAL_STAKED_USD', color='COLOR', title="Daily Deposit in USD",
             template='seaborn')
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode="x unified")
fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=10, t=30), yaxis_title=None, xaxis_title=None)

st.plotly_chart(fig, use_container_width=True)
