#%%
import numpy as np
import pandas as pd
import streamlit as st
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
    div_yield = (div_df_final["Dividend Rate"] / div_df_final["Current Price"]).round(4)
    div_df_final["Dividend Yield"] = div_yield
    b = div_df_final[div_df_final["Dividend Yield"] > 0.2].index.tolist()
    div_df_final.drop(index=b, inplace=True)
    e = div_df_final[div_df_final["Dividend Yield"] == 0].index.tolist()
    div_df_final.drop(index=e, inplace=True)
    f = div_df_final[div_df_final["Dividend Yield"].isna() == True].index.tolist()
    div_df_final.drop(index=f, inplace=True)
    c = div_df_final[div_df_final["Sector"].isna()].index.tolist()
    div_df_final.drop(index=c, inplace=True)
    div_df_final["Dividend Yield"].dropna(inplace=True)
    div_df_final = div_df_final.drop_duplicates(subset='Long_name', keep="last")
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

def drop_cols(df):
    cols_drop = ['52 Week low', '52 Week high',
       '5y. Avg.Div. yield', 'Website',
       'Market Cap', 'Reccomendation', 'Profit Margin', "Long Business Summary","Beta"]
    df_new = df.drop(cols_drop, axis=1)
    df_new = df_new[["Long_name","Symbol","Sector","Industry","Current Price", "Dividend Rate", "Dividend Yield","Payout Ratio"]].reset_index()
    df_new = df_new.rename({"Long_name": "Name", "Symbol": "Ticker", "Current Price": "Price p. Share"}, axis=1)
    df_new.drop("index", axis=1, inplace=True)
    return df_new

def get_min_sec_stocks(nr_of_stocks, sectors):
    """
    Returns the Number of minimum stocks per sector requiered to get to the nr_of_stocks with the selected sectors

    Args:
        nr_of_stocks (ind): Readout of the 'nr_of_stocks' input in the interface.
        sectors (list): List that is returned from the 'sectors' selectionbox in the interface

    Returns:
        mss (int): Number of minimum stocks per sector
        10 (int): If no sectors are selected it returns 10 as a default argument.
    """
    try:
        mss = int(round((nr_of_stocks / len(sectors)+0.5)))
        return mss
    except ZeroDivisionError:
        return 10

def calc_invest_per_part(invest_strat, monthly_invest):
    per_dict = {"Equal(25%|50%|25%)": [0.25,0.5,0.25], "Conservative(30%|50%|20%)": [0.3,0.5,0.2], "Moderate(40%|40%|20%)": [0.4,0.4,0.2], "Aggresive(55%|35%|10%)": [0.55,0.35,0.1], "Very Aggresive(75%|20%|5%)": [0.75,0.20,0.05]}
    percentage_distribution = per_dict.get(invest_strat)
    first_25_invest = monthly_invest * percentage_distribution[0]
    middle_50_invest = monthly_invest * percentage_distribution[1]
    last_25_invest = monthly_invest * percentage_distribution[2]
    return first_25_invest, middle_50_invest, last_25_invest

def split_df(df):
    df_25_len = round(len(df) / 4)
    df_first_25 = df[-df_25_len:]
    df_middle_50 = df[-(df_25_len*3):-df_25_len]
    df_last_25 = df[-df_25_len:]
    return df_first_25, df_middle_50, df_last_25

def calc_inv_per_share(first_25_invest, middle_50_invest, last_25_invest, df_first_25, df_middle_50, df_last_25):
    ips_first_25 = first_25_invest / len(df_first_25)
    ips_middle_50 = middle_50_invest / len(df_middle_50)
    ips_last_25 = last_25_invest / len(df_last_25)
    return ips_first_25, ips_middle_50, ips_last_25

def add_div_to_df_first(ips_first_25, ips_middle_50, ips_last_25, df_first_25, df_middle_50, df_last_25, invest_goal):
    df_list = [df_last_25, df_middle_50, df_first_25]
    ips_list = [ips_first_25, ips_middle_50, ips_last_25]
    for a,b in zip(df_list, ips_list):
        a["Shares"] = (b / a.loc[:,"Price p. Share"]).round(4)
        a["Value of Shares"] = b
        a["Total Dividends"] = ((a.loc[:,"Shares"] * a.loc[:,"Dividend Rate"])/12).round(4)
        a["% Contribution to Goal"] = ((a.loc[:,"Total Dividends"] / invest_goal)*100).round(3)
    df_final = pd.concat([df_last_25, df_middle_50, df_first_25], ignore_index=True)
    return df_final

def add_div_to_df_after(ips_first_25, ips_middle_50, ips_last_25, df_first_25, df_middle_50, df_last_25, total_div, invest_monthly, invest_strat):
    invest_monthly_new = invest_monthly + total_div
    ips_first_25, ips_middle_50, ips_last_25 = calc_inv_per_share(invest_strat, invest_monthly_new)
    df_list = [df_last_25, df_middle_50, df_first_25]
    ips_list = [ips_first_25, ips_middle_50, ips_last_25]
    for a,b in zip(df_list, ips_list):
        a["Shares"] = a["Shares"] + (b / a.loc[:,"Price p. Share"]).round(4)
        a["Value of Shares"] = a["Value of Shares"] + b
        a["Total Dividends"] = ((a.loc[:,"Shares"] * a.loc[:,"Dividend Rate"])/12).round(4)
        a["% Contribution to Goal"] = ((a.loc[:,"Total Dividends"] / 300)*100).round(3)
    df_final = pd.concat([df_last_25, df_middle_50, df_first_25], ignore_index=True)
    return df_final

def check_if_goal_reached(df, invest_goal):
    total_div = df["Total Dividends"].sum()
    if total_div >= invest_goal:
        return True
    else:
        return False

def check_if_max_percent_reached(df, max_per_stock):
    a = df[df["% Contribution to Goal"] >= max_per_stock].index.tolist()
    if len(a) == 0:
        return df, 0
    else:
        df_no_max_per = df[~df.index.isin(a)]
        df_max_per = df[df.index.isin(a)]
    return df_no_max_per, df_max_per

def calc_total_div(df_no_max, df_max):
    if df_max == 0:
        total_div = df_no_max["Total Dividends"].sum()
    else:
        total_div = df_no_max["Total Dividends"].sum() + df_max["Total Dividends"].sum()
    return total_div

def combine_df(df_nomax, df_max):
    if df_max == 0:
        return df_nomax
    else:
        df_final = pd.concat([df_nomax, df_max])
        return df_final

def calc_everything(max_stock_sector, max_stocks, invest_strat, monthly_invest, max_per_stock, invest_goal, years_wanted, df=None):
    execution = 0
    if df == None:
        df_initial = get_df()
        df_sorted = get_sorted_filtered_df(df_initial,sectors,max_stock_sector,max_stocks)
        df_final = drop_cols(df_sorted)
    while True:
        first_25_invest, middle_50_invest, last_25_invest = calc_invest_per_part(invest_strat, monthly_invest)
        df_first_25, df_middle_50, df_last_25 = split_df(df_final)
        ips_first_25, ips_middle_50, ips_last_25 = calc_inv_per_share(first_25_invest, middle_50_invest, last_25_invest, df_first_25, df_middle_50, df_last_25)
        if execution == 0:
            df_div_final = add_div_to_df_first(ips_first_25, ips_middle_50, ips_last_25, df_first_25, df_middle_50, df_last_25, invest_goal)
            df_no_max, df_max = check_if_max_percent_reached(df, max_per_stock)
            total_div = calc_total_div(df_no_max, df_max)
        else:
            df_div_final = add_div_to_df_after(ips_first_25, ips_middle_50, ips_last_25, df_first_25, df_middle_50, df_last_25, total_div, monthly_invest, invest_strat)
            df_no_max, df_max = check_if_max_percent_reached(df, max_per_stock)
            total_div = calc_total_div(df_no_max, df_max)
        execution += 1
        years_calc = execution / 12
        if check_if_goal_reached:
            return df_div_final, years_calc
        if execution == (years_wanted*12):
            return df_div_final
        calc_everything(max_stock_sector=max_stock_sector, max_stocks=max_stocks, invest_strat=invest_strat, monthly_invest=)   
# %%
def test():
    int_ = 1
    while True:
        int_ += 1
        print("Bob")
        if int_ == 100:
            return int_
# %%
test()
# %%
# %%
df = get_df()
# %%
pd.options.mode.chained_assignment = None 
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
    max_sec = st.number_input(label="Max. Nr. of stocks per sector.", min_value=get_min_sec_stocks(nr_of_stocks,sectors), max_value=int(nr_of_stocks), step=1, help="Input the maximum number of stocks that you want from each sector. If you do not care put the maxiumum value, to let it always choose the best stock, regardless of sector.")
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
# %%
# df1 = drop_cols(get_sorted_filtered_df(df,["Financial Services", "Healthcare", "Energy", "Industrials"], 26, 100))

# # %%
# df1 = df1.sort_values("Dividend Yield", ascending=False)
# df_25 = df1[round((-len(df1)/4)):]
# df_50 = df1[(round((-len(df1)/4)))*3:round((-len(df1)/4))]
# df_75 = df1[:(round((-len(df1)/4)))*3]
# # %%
# df_25["Shares"] = (25.0 / df_25.loc[:,"Price p. Share"]).round(4)
# df_25["Value of Shares"] = (df_25.loc[:,"Shares"] * df_25.loc[:,"Price p. Share"]).round(4)
# df_25["Total Dividends"] = (df_25.loc[:,"Shares"] * df_25.loc[:,"Dividend Rate"]).round(4)
# df_25["Contribution to Goal"] = ((df_25.loc[:,"Total Dividends"] / 3)*100).round(2)

#  # %%
# df_25
# # %%
# df_list = [df_75, df_50, df_25]
# ips_list = [25,14,5]
# for a,b in zip(df_list, ips_list):
#     a["Shares"] = a["Shares"] + (b / a.loc[:,"Price p. Share"]).round(4)
#     a["Value of Shares"] = a["Value of Shares"] + b
#     a["Total Dividends"] = ((a.loc[:,"Shares"] * a.loc[:,"Dividend Rate"])/12).round(4)
#     a["% Contribution to Goal"] = ((a.loc[:,"Total Dividends"] / 3)*100).round(3)
# df_final = pd.concat([df_75, df_50, df_25], ignore_index=True)
# total_div = df_final["Total Dividends"].sum()
# value = df_final["Value of Shares"].sum()
# df_final
# # %%
# df_final.sort_values("% Contribution to Goal", ascending=False)
# # %%
# df1
# # %%
# 625 + 700 + 125
# # %%
# df_final
# # %%
# df_test = get_df()
# df_test1 = drop_cols(df_test)
# df_test1.sort_values("Dividend Yield", ascending=False)
# # %%
# df_test1.sort_values("Dividend Yield", ascending=False)
# # %%
# l = [("test1",2), ("test2",3)]
# d = dict(l)
# d
# # %%
# a = df_final[df_final["% Contribution to Goal"] >= 40].index.tolist()
# t = df_final[~df_final.index.isin(a)]
# s = df_final[df_final.index.isin(a)]
# t.sort_values("% Contribution to Goal", ascending=False)
# s
# %%
