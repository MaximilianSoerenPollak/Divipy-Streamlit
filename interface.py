#%%
import pandas as pd
import streamlit as st
import sys
import matplotlib.pyplot as plt
import seaborn as sns
# %%
pd.options.mode.chained_assignment = None
sys.setrecursionlimit(4000)

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
    g = div_df_final[div_df_final["Sector"] == "Financial"].index.tolist()
    div_df_final.drop(index=g, inplace=True)
    div_df_final = div_df_final.drop_duplicates(subset='Long_name', keep="last")
    div_df_final = div_df_final.drop_duplicates(subset='Symbol', keep="last")
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


def get_sorted_filtered_df(df,sectors,max_stock_sector,max_stocks, excluded_tickers):
    try:
        empty_list = []
        df = df.sort_values("Dividend Yield", ascending=False)
        for i in sectors:
            a = df[df["Sector"] == i].index[:max_stock_sector].to_list()
            empty_list.append(a)
        flat_list = [item for sublist in empty_list for item in sublist]
        df = df[~df["Symbol"].isin(excluded_tickers)]
        Filter_df  = df[df.index.isin(flat_list)][:max_stocks]
        return Filter_df
    except:
        st.info("Please press the search button.")
        st.stop()

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
    df_first_25 = df[:-(df_25_len*3)]
    df_middle_50 = df[-(df_25_len*3):-df_25_len]
    df_last_25 = df[-df_25_len:]
    return df_first_25, df_middle_50, df_last_25

def calc_inv_per_share(first_25_invest, middle_50_invest, last_25_invest, df_first_25, df_middle_50, df_last_25):
    try:
        ips_first_25 = first_25_invest / len(df_first_25)
        ips_middle_50 = middle_50_invest / len(df_middle_50)
        ips_last_25 = last_25_invest / len(df_last_25)
        return ips_first_25, ips_middle_50, ips_last_25
    except:
        st.info("Please select sectors at the sidebar. Thank you")
        st.stop()
    

def add_div_to_df_first(df_first_25, df_middle_50, df_last_25, invest_goal, invest_strat, monthly_invest):
    first_25_invest, middle_50_invest, last_25_invest = calc_invest_per_part(invest_strat, monthly_invest)
    ips_first_25, ips_middle_50, ips_last_25 = calc_inv_per_share(first_25_invest, middle_50_invest, last_25_invest, df_first_25, df_middle_50, df_last_25)
    df_list = [df_last_25, df_middle_50, df_first_25]   
    ips_list = [ips_first_25, ips_middle_50, ips_last_25]
    for a,b in zip(df_list, ips_list):
        a["Shares"] = (b / a.loc[:,"Price p. Share"]).round(4)
        a["Value of Shares"] = b
        a["Total Dividends"] = ((a.loc[:,"Shares"] * a.loc[:,"Dividend Rate"])/12).round(4)
        a["% Contribution to Goal"] = ((a.loc[:,"Total Dividends"] / invest_goal)*100).round(3)
    df_final = pd.concat([df_last_25, df_middle_50, df_first_25], ignore_index=True)
    return df_final

def add_div_to_df_after(df_first_25, df_middle_50, df_last_25, total_div, invest_monthly, invest_strat):
    invest_monthly_new = invest_monthly + total_div
    first_25_invest, middle_50_invest, last_25_invest = calc_invest_per_part(invest_strat, invest_monthly_new)
    ips_first_25, ips_middle_50, ips_last_25 = calc_inv_per_share(first_25_invest, middle_50_invest, last_25_invest, df_first_25, df_middle_50, df_last_25)
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

def get_frequency_details(column, df):
    df_info = df[column].value_counts()
    my_info = dict(df_info)
    df_info_dict = { key:[value] for key, value in my_info.items() }    
    return df_info_dict

def calc_total_div(df_no_max, df_max):
    if type(df_max) == int:  
        total_div = df_no_max["Total Dividends"].sum()
    else:
        total_div = df_no_max["Total Dividends"].sum() + df_max["Total Dividends"].sum()
    return total_div

def combine_df(df_nomax, df_max):
    if type(df_max) == int:
        return df_nomax
    else:
        df_final = pd.concat([df_nomax, df_max])
        df_final = df_final.sort_values("Dividend Yield", ascending=False)
        return df_final

def calc_everything(max_stock_sector, max_stocks, sectors, invest_strat, monthly_invest, max_per_stock, invest_goal, years_wanted=None, df=None, total_div=0, execution=0, excluded_tickers=[]):
    if df is None:
        df_initial = get_df()
        df_sorted = get_sorted_filtered_df(df_initial,sectors,max_stock_sector,max_stocks, excluded_tickers)
        df_final = drop_cols(df_sorted)
    else:
        df_final = df
    df_first_25, df_middle_50, df_last_25 = split_df(df_final)
    if execution == 0:
        df_div_final = add_div_to_df_first(df_first_25, df_middle_50, df_last_25, invest_goal, invest_strat, monthly_invest)
    else:
        df_div_final = add_div_to_df_after(df_first_25, df_middle_50, df_last_25, total_div, monthly_invest, invest_strat)
    df_no_max, df_max = check_if_max_percent_reached(df_div_final, max_per_stock) 
    total_div = calc_total_div(df_no_max, df_max)
    df_recombined = combine_df(df_no_max, df_max)
    execution = execution + 1
    years_calc = execution / 12
    if check_if_goal_reached(df_recombined, invest_goal):
        df_recombined["Monthly Dividends"] = df_recombined["Total Dividends"]
        df_recombined["Total Dividends"] = df_recombined["Total Dividends"] * 12
        return df_recombined, years_calc
    if years_wanted is None:
        pass
    elif execution == (years_wanted*12):
        df_recombined["Monthly Dividends"] = df_recombined["Total Dividends"]
        df_recombined["Total Dividends"] = df_recombined["Total Dividends"] * 12
        return df_recombined, years_wanted
    return calc_everything(df=df_recombined ,max_stock_sector=max_stock_sector,sectors=sectors, max_stocks=max_stocks, invest_strat=invest_strat, monthly_invest=monthly_invest, total_div=total_div, years_wanted=years_wanted, execution=execution, invest_goal=invest_goal, max_per_stock=max_per_stock)
# %%

# %%
df = get_df()
st.title("Welcome to the Dividens investment Helper or so.")
# %%
sidebar = st.sidebar
with sidebar:
    invest_goal = st.number_input(label="Monthly investment Goal.", min_value=100, step=50, help="How much money you want to have before taxes each month through dividends")
    max_per_ps = st.number_input(label="Max. percent a single stock can contribute towards the goal.", min_value=0, max_value=100, step=10, help="Once a stock reaches this number, it will be no longer invested into, and other stocks will recieve more funds. If put at 100 or very high, it wont stop investing into certain stocks, untill it reached the goal.")
    nr_of_stocks = st.number_input(label="Nr. of stocks.", min_value=10, max_value=100, step=10,  help="Input the number of stocks you want to recieve as reccomendations.")
    container1 = st.beta_container()
    all_sectors = st.checkbox("Select all", key="sectors")
    if all_sectors:
        sectors = container1.multiselect("Select all the sectors which you want to include.",
            df["Sector"].unique().tolist(),df["Sector"].unique().tolist(), help="If you want to de-select all just press the button below again.")
    else:
        sectors =  container1.multiselect("Select all the sectors which you want to include.",
            df["Sector"].unique().tolist(),help="If you want to select all just press the button below.")
    max_sec = st.number_input(label="Max. Nr. of stocks per sector.", min_value=get_min_sec_stocks(nr_of_stocks,sectors), max_value=int(nr_of_stocks), step=1, help="Input the maximum number of stocks that you want from each sector. If you do not care put the maxiumum value, to let it always choose the best stock, regardless of sector.")
    invest_strat = st.selectbox(label="Select your investment strategy", options=["Equal(25%|50%|25%)", "Conservative(30%|50%|20%)","Moderate(40%|40%|20%)", "Aggresive(55%|35%|10%)", "Very Aggresive(75%|20%|5%)"], help="Divides your investment into 3 parts. Top25% | Middle50% | Lower25% of the stocks.")
    monthly_invest = st.number_input(label="Monthly investment", min_value=calc_min_invest(nr_of_stocks,invest_strat), step=10, help="How much money you want to invest into stocks each month.")
    search = st.button("Search")
st.subheader("You can see your filters and choices below.")
st.write("---")
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

df_1, y1 = calc_everything(max_stock_sector=max_sec, max_stocks=nr_of_stocks, sectors=sectors, invest_strat=invest_strat, monthly_invest=monthly_invest, max_per_stock=max_per_ps, invest_goal=invest_goal, years_wanted=1)
df_2, y2 = calc_everything(max_stock_sector=max_sec, max_stocks=nr_of_stocks, sectors=sectors, invest_strat=invest_strat, monthly_invest=monthly_invest, max_per_stock=max_per_ps, invest_goal=invest_goal, years_wanted=2)
df_5, y5 = calc_everything(max_stock_sector=max_sec, max_stocks=nr_of_stocks, sectors=sectors, invest_strat=invest_strat, monthly_invest=monthly_invest, max_per_stock=max_per_ps, invest_goal=invest_goal, years_wanted=5)
df_ye, ye = calc_everything(max_stock_sector=max_sec, max_stocks=nr_of_stocks, sectors=sectors, invest_strat=invest_strat, monthly_invest=monthly_invest, max_per_stock=max_per_ps, invest_goal=invest_goal)

st.write("---")
container2 = st.beta_container()
select_all_button = st.empty()
exclude = st.empty()
st.subheader("With your selected filters, these are the numbers:")
st.write("---")
cola, colb, colc = st.beta_columns(3)
with cola:
    money_no_div_end = st.empty()
    money_div_end =st.empty()
    div_rein_end = st.empty()
with colb:
    div_year_end = st.empty()
    div_month_end = st.empty()
with colc:
    return_year_end = st.empty()
    years_end = st.empty()
    
st.subheader("Check out more information below, like all the stocks you should invest in.")
st.write("---")

with st.beta_expander("Stocks after 1 Years"):
    df_1_place = st.empty()
    col1, col2, col3, col4, col5, col6 = st.beta_columns((1,1.5,1.5,1.5,1.5,1))
    with col1:
        val1_nodye = st.empty()
    with col2:
        value1 = st.empty()
    with col3:
        div1_py = st.empty()
    with col4:
        div1 = st.empty()
    with col5:
        div1m = st.empty()
    with col6:
        ret1 = st.empty()
with st.beta_expander("Stocks after 2 Years"):
    df_2_place = st.empty()
    col1, col2, col3, col4, col5, col6 = st.beta_columns((1,1.5,1.5,1.5,1.5,1))
    with col1:
        val2_nodye = st.empty()
    with col2:
        value2 = st.empty()
    with col3:
        div2_py = st.empty()
    with col4:
        div2 = st.empty()
    with col5:
        div2m = st.empty()
    with col6:
        ret2 = st.empty()
with st.beta_expander("Stocks after 5 Years"):
    df_5_place = st.empty()
    col1, col2, col3, col4, col5, col6 = st.beta_columns((1,1.5,1.5,1.5,1.5,1))
    with col1:
        val5_nodye = st.empty()
    with col2:
        value5 = st.empty()
    with col3:
        div5_py = st.empty()
    with col4:
        div5 = st.empty()
    with col5:
        divm5 = st.empty()
    with col6:
        ret5 = st.empty()
    
with st.beta_expander("Stocks when your goal is reached"):
    df_ye_place = st.empty()
    col1, col2, col3, col4, col5, col6, col7 = st.beta_columns((1,1.5,1,1,1,1,1.5))
    with col1:
        val_nodye = st.empty()
    with col2:
        valueye = st.empty()
    with col3:
        divye_py = st.empty()
    with col4:
        divye = st.empty()
    with col5:
        divmye = st.empty()
    with col6:
        retye = st.empty()
    with col7:
        yearsye = st.empty()
df_1_place.write(df_1)
df_2_place.write(df_2)
df_5_place.write(df_5)
df_ye_place.write(df_ye)
df_1_place.write(df_1)
value1.write(f"Money Invested with reeinvesting: {df_1['Value of Shares'].sum():.2f}€")
val1_nodye.write(f"Money Invested: {y1*(monthly_invest*12):.2f}€")
div1_py.write(f"Dividends Reinvested: {(df_1['Value of Shares'].sum()-y1*(monthly_invest*12)):.2f}€")
div1.write(f"Dividends per Year: {df_1['Total Dividends'].sum():.3f}€")
div1m.write(f"Dividends per Month: {df_1['Monthly Dividends'].sum():.3f}€")
ret_1 = df_1["Total Dividends"].sum() / df_1["Value of Shares"].sum()
ret1.write(f"Return: {ret_1*100:.2f}%")
df_2_place.write(df_2)
value2.write(f"Money Invested with reeinvesting: {df_2['Value of Shares'].sum():.2f}€")
val2_nodye.write(f"Money Invested: {y2*(monthly_invest*12):.2f}€")
div2_py.write(f"Dividends Reinvested: {(df_2['Value of Shares'].sum()-y2*(monthly_invest*12)):.2f}€")
div2.write(f"Dividends per Year: {df_2['Total Dividends'].sum():.3f}€")
div2m.write(f"Dividends per Month: {df_2['Monthly Dividends'].sum():.3f}€")
ret_2 = df_2["Total Dividends"].sum() / df_2["Value of Shares"].sum()
ret2.write(f"Return: {ret_2*100:.2f}%")
df_5_place.write(df_5)
value5.write(f"Money Invested with reeinvesting: {df_5['Value of Shares'].sum():.2f}€")
div5_py.write(f"Dividends Reinvested: {(df_5['Value of Shares'].sum()-y5*(monthly_invest*12)):.2f}€")
val5_nodye.write(f"Money Invested: {y5*(monthly_invest*12):.2f}€")
div5.write(f"Dividends per Year: {df_5['Total Dividends'].sum():.3f}€")
divm5.write(f"Dividends per Month: {df_5['Monthly Dividends'].sum():.3f}€")
ret_5 = df_5["Total Dividends"].sum() / df_5["Value of Shares"].sum()
ret5.write(f"Return per year: {ret_5*100:.2f}%")
df_ye_place.write(df_ye)
valueye.write(f"Money Invested with reeinvesting: {df_ye['Value of Shares'].sum():.2f}€")
divye_py.write(f"Dividends Reinvested: {(df_ye['Value of Shares'].sum()-ye*(monthly_invest*12)):.2f}€")
val_nodye.write(f"Money Invested: {ye*(monthly_invest*12):.2f}€")
divye.write(f"Dividends per Year: {df_ye['Total Dividends'].sum():.3f}€")
divmye.write(f"Dividends per Month: {df_ye['Monthly Dividends'].sum():.3f}€")
ret_ye = df_ye["Total Dividends"].sum() / df_ye["Value of Shares"].sum()
retye.write(f"Return: {ret_ye*100:.2f}%")
yearsye.write(f"It takes you {ye:.1f} Years to reach your goal.")
money_div_end.write(f"Money Invested with reeinvesting: {df_ye['Value of Shares'].sum():.2f}€")
div_rein_end.write(f"Dividends Reinvested: {(df_ye['Value of Shares'].sum()-ye*(monthly_invest*12)):.2f}€")
money_no_div_end.write(f"Money Invested: {ye*(monthly_invest*12):.2f}€")
div_year_end.write(f"Dividends per Year: {df_ye['Total Dividends'].sum():.3f}€")
div_month_end.write(f"Dividends per Month: {df_ye['Monthly Dividends'].sum():.3f}€")
ret_ye = df_ye["Total Dividends"].sum() / df_ye["Value of Shares"].sum()
return_year_end.write(f"Return: {ret_ye*100:.2f}%")
years_end.write(f"{ye:.1f} Years.")
all_tickers = select_all_button.checkbox("Select all", key="tickers")
if all_tickers :
    exluded_tickers = container2.multiselect("Select all the Tickers which you want to include.",
        df_1["Ticker"].unique().tolist(),df_1["Ticker"].unique().tolist(), help="If you want to de-select all just press the button below again.")
else:
    exluded_tickers =  container2.multiselect("Select all the Tickers which you want to include.",
        df_1["Ticker"].unique().tolist(),help="If you want to select all just press the button below.")
exlude = exclude.button("Exclude")
if exlude:
    df_1_e, y1_e = calc_everything(max_stock_sector=max_sec, max_stocks=nr_of_stocks, sectors=sectors, invest_strat=invest_strat, monthly_invest=monthly_invest, max_per_stock=max_per_ps, invest_goal=invest_goal, years_wanted=1, excluded_tickers=exluded_tickers)
    df_2_e, y2_e = calc_everything(max_stock_sector=max_sec, max_stocks=nr_of_stocks, sectors=sectors, invest_strat=invest_strat, monthly_invest=monthly_invest, max_per_stock=max_per_ps, invest_goal=invest_goal, years_wanted=2, excluded_tickers=exluded_tickers)
    df_5_e, y5_e = calc_everything(max_stock_sector=max_sec, max_stocks=nr_of_stocks, sectors=sectors, invest_strat=invest_strat, monthly_invest=monthly_invest, max_per_stock=max_per_ps, invest_goal=invest_goal, years_wanted=5, excluded_tickers=exluded_tickers)
    df_ye_e, ye_e = calc_everything(max_stock_sector=max_sec, max_stocks=nr_of_stocks, sectors=sectors, invest_strat=invest_strat, monthly_invest=monthly_invest, max_per_stock=max_per_ps, invest_goal=invest_goal, excluded_tickers=exluded_tickers)
    df_1_place.write(df_1_e)
    value1.write(f"Money Invested with reeinvesting: {df_1_e['Value of Shares'].sum():.2f}€")
    div1_py.write(f"Dividends Reinvested: {(df_1['Value of Shares'].sum()-y1_e*(monthly_invest*12)):.2f}€")
    val1_nodye.write(f"Money Invested: {y1_e*(monthly_invest*12):.2f}€")
    div1.write(f"Dividends per Year: {df_1_e['Total Dividends'].sum():.3f}€")
    div1m.write(f"Dividends per Month: {df_1_e['Monthly Dividends'].sum():.3f}€")
    ret_1 = df_1_e["Total Dividends"].sum() / df_1_e["Value of Shares"].sum()
    ret1.write(f"Return: {ret_1*100:.2f}%")
    df_2_place.write(df_2_e)
    value2.write(f"Money Invested with reeinvesting: {df_2_e['Value of Shares'].sum():.2f}€")
    div2_py.write(f"Dividends Reinvested: {(df_2_e['Value of Shares'].sum()-y2_e*(monthly_invest*12)):.2f}€")
    val2_nodye.write(f"Money Invested: {y2_e*(monthly_invest*12):.2f}€")
    div2.write(f"Dividends per Year: {df_2_e['Total Dividends'].sum():.3f}€")
    div2m.write(f"Dividends per Month: {df_2_e['Monthly Dividends'].sum():.3f}€")
    ret_2 = df_2_e["Total Dividends"].sum() / df_2_e["Value of Shares"].sum()
    ret2.write(f"Return: {ret_2*100:.2f}%")
    df_5_place.write(df_5_e)
    value5.write(f"Money Invested with reeinvesting: {df_5_e['Value of Shares'].sum():.2f}€")
    div5_py.write(f"Dividends Reinvested: {(df_5_e['Value of Shares'].sum()-y5_e*(monthly_invest*12)):.2f}€")
    val5_nodye.write(f"Money Invested: {y5_e*(monthly_invest*12):.2f}€")
    div5.write(f"Dividends per Year: {df_5_e['Total Dividends'].sum():.3f}€")
    divm5.write(f"Dividends per Month: {df_5_e['Monthly Dividends'].sum():.3f}€")
    ret_5 = df_5_e["Total Dividends"].sum() / df_5_e["Value of Shares"].sum()
    ret5.write(f"Return per year: {ret_5*100:.2f}%")
    df_ye_place.write(df_ye_e)
    valueye.write(f"Money Invested with reinvesting: {df_ye_e['Value of Shares'].sum():.2f}€")
    div5_py.write(f"Dividends Reinvested: {(df_ye_e['Value of Shares'].sum()-ye_e*(monthly_invest*12)):.2f}€")
    val_nodye.write(f"Money Invested: {ye_e*(monthly_invest*12):.2f}€")
    divye.write(f"Dividends per Year: {df_ye_e['Total Dividends'].sum():.3f}€")
    divmye.write(f"Dividends per Month: {df_ye_e['Monthly Dividends'].sum():.3f}€")
    ret_ye = df_ye_e["Total Dividends"].sum() / df_ye_e["Value of Shares"].sum()
    retye.write(f"Return: {ret_ye*100:.2f}%")
    yearsye.write(f"It takes you {ye_e:.1f} Years to reach your goal.")
graphs = st.beta_expander("Click here to see a graph.")
with graphs:
    col1, col2 = st.beta_columns(2)
    with col1:
        df_info_dict = get_frequency_details("Sector", df)
        keys = list(df_info_dict.keys())
        vals = [float(df_info_dict[k][0]) for k in keys]
        fig4, ax4 = plt.subplots(figsize=(12,8))
        plt.style.use("dark_background")
        sns.set(style="darkgrid")
        ax4.set_title("Distribution of Stocks in Sectors", size='16', fontweight='bold')
        chart = sns.barplot(x=keys,y=vals, ax=ax4)
        chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
        st.pyplot(fig4)