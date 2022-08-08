from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title='Aave Dashboard', layout='wide', page_icon=':dollar:')
st.title("Aave v2 and v3 Dashboard - Supply/TVL")
st.sidebar.title('Supply/TVL')
st.sidebar.markdown("this page Contains the Aave version 2 and 3 Supply/TVL for all chains supported by Aave 🎈")


@st.cache(ttl=6 * 60 * 60)  # 6 hours
def fetch_data(url: str):
    first = 1000
    block_number = 0
    raw_data = []
    while True:
        payload = {
            "query": "query{ marketDailySnapshots(first:%s, orderBy: blockNumber, orderDirection: asc, where:{blockNumber_gt: %d}){ dailyBorrowUSD dailyLiquidateUSD dailyRepayUSD blockNumber timestamp totalValueLockedUSD dailyDepositUSD dailyWithdrawUSD market { id name } } } " % (
                first, block_number),
        }
        res = requests.post(url=url,
                            json=payload).json()

        if not res['data']['marketDailySnapshots']:
            break
        raw_data.extend(res['data']['marketDailySnapshots'])
        block_number = max([int(b['blockNumber']) for b in raw_data])

    for item in raw_data:
        item['Day'] = datetime.fromtimestamp(int(item['timestamp'])).date()
        item['Asset'] = item['market']['name']
        item['TVL'] = int(float(item['totalValueLockedUSD']))
        item['dailyDepositUSD'] = int(float(item['dailyDepositUSD']))
        item['dailyWithdrawUSD'] = int(float(item['dailyWithdrawUSD']))

        item['dailyBorrowUSD'] = int(float(item['dailyBorrowUSD']))
        item['dailyLiquidateUSD'] = int(float(item['dailyLiquidateUSD']))
        item['dailyRepayUSD'] = int(float(item['dailyRepayUSD']))
    # st.json(raw_data)
    return pd.DataFrame(
        raw_data,
        columns=["Day", "TVL", 'dailyDepositUSD', 'dailyWithdrawUSD', "Asset", "dailyBorrowUSD", "dailyLiquidateUSD", "dailyRepayUSD"])


def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


def get_delta_color(from_num, to_num):
    return 'inverse' if from_num > to_num else 'normal'


def generate_supply_charts(chart_data):
    today_tvls = chart_data.sort_values("Day", ascending=False).groupby("Asset").head(1)
    one_month_ago_tvls = chart_data.loc[chart_data['Day'] == datetime.now().date() - timedelta(days=30)]
    one_month_ago_tvl = one_month_ago_tvls['TVL'].sum()
    today_tvl = today_tvls['TVL'].sum()

    # Metrics
    c1, c2, c3, c4 = st.columns(4, gap="small")
    c2.metric("Current USD TVL", "{:,}".format(today_tvl))
    c3.metric("USD TVL Changes(1 month)", "{:,}".format(today_tvl - one_month_ago_tvl),
              f"{round(get_change(today_tvl, one_month_ago_tvl), 2)}%",
              delta_color=get_delta_color(one_month_ago_tvl, today_tvl))
    st.markdown("""---""")

    # end metrics

    col1, col2 = st.columns(2, gap="small")

    fig = px.pie(today_tvls, values='TVL', names='Asset',
                 title='TVL Distribution', template='seaborn')
    fig.update_traces(textposition='inside', textinfo='value+label', insidetextorientation='radial')
    fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
    col1.plotly_chart(fig, use_container_width=True)

    fig = px.pie(one_month_ago_tvls, values='TVL', names='Asset', title='One Month ago TVL Distribution',
                 template='seaborn')
    fig.update_traces(textposition='inside', textinfo='value+label', insidetextorientation='radial')
    fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
    col2.plotly_chart(fig, use_container_width=True)

    st.markdown("""---""")

    fig = px.area(chart_data, x='Day', y='TVL', color='Asset', title="TVL/Supply Locked over time",
                  template='seaborn')
    fig.update_traces(mode="lines", hovertemplate=None)
    fig.update_layout(hovermode="x unified")
    fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    fig = px.bar(chart_data, x='Day', y='dailyDepositUSD', color='Asset', title="Daily Deposit in USD",
                 template='seaborn')
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x unified")
    fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)

    col1.plotly_chart(fig, use_container_width=True)

    fig = px.bar(chart_data, x='Day', y='dailyWithdrawUSD', color='Asset', title="Daily Withdraw in USD",
                 template='seaborn')
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x unified")
    fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
    col2.plotly_chart(fig, use_container_width=True)



    fig = px.bar(chart_data, x='Day', y='dailyBorrowUSD', color='Asset', title="Daily Borrow in USD",
                  template='seaborn')
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(chart_data, x='Day', y='dailyLiquidateUSD', color='Asset', title="Daily Liquidate in USD",
                  template='seaborn')
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(chart_data, x='Day', y='dailyRepayUSD', color='Asset', title="Daily Repay in USD",
                  template='seaborn')
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_layout(title_x=0, margin=dict(l=0, r=10, b=30, t=30), yaxis_title=None, xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

with st.spinner('Updating Report...'):
    activation_function = st.selectbox('Choose a Chain',
                                       ['Avalanche v2', 'Avalanche v3', 'Ethereum', 'Optimism', 'Fantom', 'Arbitrum',
                                        'Harmony', 'Polygon v2', 'Polygon v3'])

    if activation_function == 'Avalanche v2':
        chart_data = fetch_data('https://api.thegraph.com/subgraphs/name/messari/aave-v2-avalanche-extended')
        generate_supply_charts(chart_data)

    if activation_function == 'Avalanche v3':
        chart_data = fetch_data('https://api.thegraph.com/subgraphs/name/messari/aave-v3-avalanche')
        generate_supply_charts(chart_data)

    if activation_function == 'Ethereum':
        chart_data = fetch_data('https://api.thegraph.com/subgraphs/name/messari/aave-v2-ethereum-extended')
        generate_supply_charts(chart_data)

    if activation_function == 'Optimism':
        chart_data = fetch_data('https://api.thegraph.com/subgraphs/name/messari/aave-v3-optimism-extended')
        generate_supply_charts(chart_data)

    if activation_function == 'Polygon v3':
        chart_data = fetch_data('https://api.thegraph.com/subgraphs/name/messari/aave-v3-polygon-extended')
        generate_supply_charts(chart_data)

    if activation_function == 'Polygon v2':
        st.write('Lack of Data (database is updating and is not fully backfill yet)')
        chart_data = fetch_data('https://api.thegraph.com/subgraphs/name/messari/aave-v2-polygon-extended')
        generate_supply_charts(chart_data)

    if activation_function == 'Harmony':
        chart_data = fetch_data('https://api.thegraph.com/subgraphs/name/messari/aave-v3-harmony-extended')
        generate_supply_charts(chart_data)

    if activation_function == 'Fantom':
        chart_data = fetch_data('https://api.thegraph.com/subgraphs/name/messari/aave-v3-fantom-extended')
        generate_supply_charts(chart_data)

    if activation_function == 'Arbitrum':
        chart_data = fetch_data('https://api.thegraph.com/subgraphs/name/messari/aave-v3-arbitrum-extended')
        generate_supply_charts(chart_data)
