###########################################################################################################
###########################################################################################################
######## author = Misagh Lotfi
######## website = https://www.linkedin.com/in/misagh-lotfi/
######## version = 1.0
###########################################################################################################
###########################################################################################################
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title='Aave Dashboard', layout='wide', page_icon=':dollar:')
st.sidebar.title('Insights')
st.sidebar.markdown("this page Contains some insights about charts and data 🎈")


@st.cache(ttl=72 * 60 * 60)  # 6 hours
def fetch_current_tvl(url: str):
    first = 100
    raw_data = []
    payload = {
        "query": "query{ marketDailySnapshots(first:%s, orderBy: blockNumber, orderDirection: desc, where:{timestamp_gte: 1659815794}){ blockNumber timestamp totalValueLockedUSD dailyDepositUSD dailyWithdrawUSD market { id name } } } " % (
            first),
    }
    res = requests.post(url=url,
                        json=payload).json()
    raw_data.extend(res['data']['marketDailySnapshots'])

    for item in raw_data:
        item['Day'] = datetime.fromtimestamp(int(item['timestamp'])).date()
        item['Asset'] = item['market']['name']
        item['TVL'] = int(float(item['totalValueLockedUSD']))
    dp = pd.DataFrame(
        raw_data,
        columns=["Day", "TVL", 'dailyDepositUSD', 'dailyWithdrawUSD', "Asset"])
    today_tvls = dp.sort_values("Day", ascending=False).groupby("Asset").head(1)
    return today_tvls['TVL'].sum()


row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('Aave Dashboard')
with row0_2:
    st.text("")
    st.subheader('written by [Misagh Lotfi](https://www.linkedin.com/in/misagh-lotfi/)')
row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
with row3_1:
    st.markdown(
        "Hello there! this dashboard contains the Aave platform stats by different metrics such as Supply/TVL and Staking.")
    st.markdown(
        "You can find the source code in the [GitHub Repository](https://github.com/Misaghlb/aave_dashboard/)")
    st.markdown("### Overview:\n"
                "- Total Supply and Locked value in all Aave markets\n"
                "- Deposits and Withdraws from Aave platform\n"
                "- Share of each asset in Aave Markets\n"
                "- Staking stkAave over time\n"
                )
    st.markdown("### Introduction:\n"
                "in this page, we will look at the data and charts provided on other pages. in the Supply and Staking pages you can follow the updated data from Aave in all chains, so you have access to these data with a short delay.\n"
                )

    st.markdown("### Supply/TVL:\n"
                "TVL is the total value locked and available in Aave, it's the sum of deposits, withdrawals, borrows, repays, etc. by looking at the chart in all chains we can see that Ethereum has the highest TVL with \$6.6 Billion, Harmony with \$1.3 Milion has the lowest TVL."
                )

# Metrics
st.markdown("""---""")

c1, c2, c3, c4 = st.columns(4, gap="small")
today_tvl = fetch_current_tvl('https://api.thegraph.com/subgraphs/name/messari/aave-v2-avalanche-extended')
c1.metric("Avalanche v2 USD TVL", "{:,}".format(today_tvl))

today_tvl = fetch_current_tvl('https://api.thegraph.com/subgraphs/name/messari/aave-v2-ethereum-extended')
c2.metric("Ethereum USD TVL", "{:,}".format(today_tvl))

today_tvl = fetch_current_tvl('https://api.thegraph.com/subgraphs/name/messari/aave-v3-optimism-extended')
c3.metric("Optimism USD TVL", "{:,}".format(today_tvl))

today_tvl = fetch_current_tvl('https://api.thegraph.com/subgraphs/name/messari/aave-v3-polygon-extended')
c4.metric("Polygon(v3) USD TVL", "{:,}".format(today_tvl))

c1, c2, c3, c4 = st.columns(4, gap="small")

today_tvl = fetch_current_tvl('https://api.thegraph.com/subgraphs/name/messari/aave-v3-harmony-extended')
c1.metric("Harmony USD TVL", "{:,}".format(today_tvl))

today_tvl = fetch_current_tvl('https://api.thegraph.com/subgraphs/name/messari/aave-v3-fantom-extended')
c2.metric("Fantom USD TVL", "{:,}".format(today_tvl))

today_tvl = fetch_current_tvl('https://api.thegraph.com/subgraphs/name/messari/aave-v3-arbitrum-extended')
c3.metric("Arbitrum USD TVL", "{:,}".format(today_tvl))

today_tvl = fetch_current_tvl('https://api.thegraph.com/subgraphs/name/messari/aave-v3-avalanche-extended')
c4.metric("Avalanche v3 USD TVL", "{:,}".format(today_tvl))

st.markdown("""---""")

# end metrics

st.markdown("##### Optimism TVL Growth:\n"
            "as the optimism Supply/TVL show, it spiked and increased hugely in August 2022, why?\n"
            "https://twitter.com/AaveAave/status/1555230478394966018\n"
            "As part of its OP Summer program, Optimism has allocated 5 million OP tokens Aave for distribution to its users. since this announcement users have bridged millions of USD to deposit into aave and earn rewards.\n"
            )

st.markdown("##### Arbitrum:\n"
            "the layer 2 networks also is growing, arbitrum experiencing 22 percent growth since one month ago.\n"
            )

st.markdown("##### Avalanche:\n"
            "The Avalanche in aave v2 TVL peak was \$7B in November 2021, but by April 2022 it had fallen to \$153M as of today.\n"
            "the v2 capitals shifted from v2 to v3 by starting version 3 market on 20th April 2021"
            )

st.markdown("##### Harmony:\n"
            "A bear market has caused Harmony Token's (\$ONE) value to drop about 10x, and because most of Harmony's supply is $ONE, the TVL USD value has decreased significantly.\n"
            )

st.markdown("##### Polygon:\n"
            "Polygon v3 is doing great and TVL is growing day by day.\n"
            "The TVL growth 49 percent since one month ago which is about 28.8M dollars."
            )

st.markdown("### Staking:\n"
            "in the Aave platform users can stake their AAVE token to earn rewards. with depositing and staking AAVE, users get back stkAave which is equivalent to Aave.\n"
            "total staking volume was increasing in Bull markets, but after crashing market in March 2021 and also with starting the recent crash, the staking volume deceased and the redeems increased."
            )

st.markdown("### Conclusion:\n"
            "- Ethereum Mainnet has the highest Supply with 6.6 billion dollars\n"
            "- Optimism supply spiked to 2 billion dollars with announcing new Liquidity Mining program on Aave v3\n"
            )


st.markdown("#### Method and Sources:\n"
            "The flipsidecrypto data are not fully backfilled yet for all chains supported by Aave, so I decided to use the Messari Graphql databases that contain all the data and transactions from all the chains.\n"
            "Using this approach we can access the most updated data, fast and Accurate, because the messari databases are fully synced with the main blockchain data, and we can access this data through https://thegraph.com/ platform. \n"
            "for staking stkAAVE I'm using the flipsidecrypto data, and the data is auto-updating.\n"
            ""
            "1. Messari data: https://thegraph.com/hosted-service \n"
            "2. FlipsideCrypto Staking Query: https://app.flipsidecrypto.com/velocity/queries/60316905-bca9-4ebc-8459-ac7a20e8eb5c \n"
            "3. App source code: https://github.com/Misaghlb/aave_dashboard \n"
            )

st.markdown("---")
st.markdown("##### Contact:\n"
            "- https://twitter.com/misaghlb \n"
            "- misaghlb@live.com\n"
            )