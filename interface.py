#%%
from logging import Filter
from re import L
import string
from altair.vegalite.v4.schema.channels import StrokeOpacity

import numpy as np
import pandas as pd
import streamlit as st
from altair.vegalite.v4.schema.core import Month
from numpy.core.fromnumeric import sort

# %%

# %%
# div_df_final
# # %%
# div_goal = 3000
# yearly_goal = div_goal * 12
# monthly_invest = 300
# max_percent = 0.2
# min_stocks = 100/(100*max_percent)
# max_invest_p_share = max_percent * monthly_invest
# max_per_sec = 2
# # %%
# sample_10 = div_df_final.sample(20)
# # %%
# sectors = sample_10["Sector"].unique().tolist()
# # %%
# sorted_20 = sample_10.sort_values("Dividend Yield", ascending=False)
# # %%
# len(Filter_df)
# # %%
# 3000 * 0.2
# # %%
# 600*12 / 0.04
# # %%
# 300/12
# # %%
# 25/0.5225
# # %%
# (0.04/12)*47.9
# per = int(len(Filter_df) / 4)
# top_25 = Filter_df[:per]
# middle_50 = Filter_df[per:per*3]
# lower_25 = Filter_df[per*3:]

# middle_50
#  # %%
# min_stocks
# %%-
# """
# Starting from here we will build the website.
# """
# %%
#-----------FUNCTIONS---------------------
def get_df():
    """
    Reads and cleans the final DataFrame which all our future calculations will be working with.

    Returns:
        DataFrame: It's the final cleaned DataFrame.
    """
    div_df_final = pd.read_csv("/Users/m.soren/Desktop/Ironhack/Project5/Final_stock_csv")
    div_df_final.drop("Unnamed: 0", inplace=True, axis=1)
    b = div_df_final[div_df_final["Dividend Yield"] > 0.2].index.tolist()
    div_df_final.drop(index=b, inplace=True)
    c = div_df_final[div_df_final["Sector"].isna()].index.tolist()
    div_df_final.drop(index=c, inplace=True)
    return div_df_final


def calc_min_invest(nr_stocks,strat):
    """
    Calculates the minimum Investment money needed to have atleast 1€ per stock.
    It takes the lowest % of each Strategy divides 100 by it and that is the value in the dictionary.
    What is important to note is that 25% of stocks will recieve the lowest % of the investment strategy.(The last one).
    So 25% of stocks could recieve just 5% of the Investment.

    Args:
        nr_stocks (int): Integer entered into the 'nr_of_stocks' input box. It's the number of stocks you want to get back.
        strat (str): The strategy recieved from the 'invest_strat' selection box. The lowest % is the important one here.

    Returns:
        min_invest (int):   This is the minium amount of € the User has to invest in order to gurantee atleast 1€ per stock 
                            with the given investment strategy.
    """
    min_per_dict = {"Equal(25%|50%|25%)": 4, "Conservative(30%|50%|20%)": 5, "Moderate(40%|40%|20%)": 5, "Aggresive(55%|35%|10%)": 10, "Very Aggresive(75%|20%|5%)": 20}
    min_percent_invest = min_per_dict.get(strat)
    stocks_quart = round(nr_stocks / 4)
    min_invest = stocks_quart * min_percent_invest
    return min_invest


def get_sorted_filtered_df(df,sectors,max_stock_sector,max_stocks):
    empty_list = []
    df = df.sort_values("Dividend Yield", ascending=False)
    for i in sectors:
        a = df[df["Sector"] == i].index[:max_stock_sector].to_list()
        empty_list.append(a)
    flat_list = [item for sublist in empty_list for item in sublist]
    Filter_df  = df[df.index.isin(flat_list)][:max_stocks]
    return Filter_df


def get_min_sec_stocks(nr_of_stocks, sectors):
    """
    Returns the Number of minimum stocks per sector requiered to get to the nr_of_stocks with the selected sectors

    Args:
        nr_of_stocks (ind): Readout of the 'nr_of_stocks' input in the interface.
        sectors (list): List that is returned from the 'sectors' selectionbox in the interface

    Returns:
        mss (int): NUmber of minimum stocks per sector
        10 (int): If no sectors are selected it returns 10 as a default argument.
    """
    try:
        mss = int(round((nr_of_stocks / len(sectors)+0.5)))
        return mss
    except ZeroDivisionError:
        return 10
# %%
df = get_df()
# %%
st.subheader("Welcome to the Dividens investment Helper or so.")
# %%
sidebar = st.sidebar
with sidebar:
    invest_goal = st.number_input(label="Monthly investment Goal.", min_value=100, step=50, help="How much money you want to have before taxes each month through dividends")
    max_per_ps = st.number_input(label="Max. percent a single stock can contribute towards the goal.", min_value=0, max_value=100, step=10, help="Once a stock reaches this number, it will be no longer invested into, and other stocks will recieve more funds. If put at 100 or very high, it wont stop investing into certain stocks, untill it reached the goal.")
    nr_of_stocks = st.number_input(label="Nr. of stocks.", min_value=10, max_value=100, step=10,  help="Input the number of stocks you want to recieve as reccomendations.")
    container = st.beta_container()
    all = st.checkbox("Select all")
    if all:
        sectors = container.multiselect("Select all the sectors which you want to include.",
            df["Sector"].unique().tolist(),df["Sector"].unique().tolist(), help="If you want to de-select all just press the button below again.")
    else:
        sectors =  container.multiselect("Select all the sectors which you want to include.",
            df["Sector"].unique().tolist(),help="If you want to select all just press the button below.")
    max_sec = st.number_input(label="Max. Nr. of stocks per sector.", min_value=get_min_sec_stocks(nr_of_stocks,sectors), max_value=nr_of_stocks, step=1, help="Input the maximum number of stocks that you want from each sector. If you do not care put the maxiumum value, to let it always choose the best stock, regardless of sector.")
    invest_strat = st.selectbox(label="Select your investment strategy", options=["Equal(25%|50%|25%)", "Conservative(30%|50%|20%)","Moderate(40%|40%|20%)", "Aggresive(55%|35%|10%)", "Very Aggresive(75%|20%|5%)"], help="Divides your investment into 3 parts. Top25% | Middle50% | Lower25% of the stocks.")
    monthly_invest = st.number_input(label="Monthly investment", min_value=calc_min_invest(nr_of_stocks,invest_strat), step=10, help="How much money you want to invest into stocks each month.")
st.write("You can see your filters and choices below.")
st.write("---")
st.write("wup")
col1, col2, col3 = st.beta_columns(3)
with col1:
    st.write(f"Monthly dividends goal: {invest_goal}€")
    st.write(f"Nr. of stocks: {nr_of_stocks}")
with col2:
    st.write(f"Monthly investment: {monthly_invest}€")
    st.write(f"Max. Nr. of stocks per sector: {max_sec}")
with col3:
    st.write(f"Max. contribution per share: {max_per_ps} %")
    st.write(f"Selected investment strategy: {invest_strat}")
# %%
test_df = get_sorted_filtered_df(df,["Financial Services", "Healthcare", "Energy", "Industrials"], 26, 70)
# test_df.shape
# %%
