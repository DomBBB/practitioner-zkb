import pandas as pd
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#########################################################################################################################
# This class is used to generate objects for each asset
class Asset:

    # This function is automatically called when a new Asset() object is generated
    def __init__(self, name, category):

        # Ensure that name is a string
        assert isinstance(name, str), f"name '{name}' is not a string"
        # Ensure that category is a string
        assert isinstance(category, str), f"category '{category}' is not a string"
        # Store name as object attribute
        self.__name = name
        # Store category as object attribute
        self.__category = category

        # For-loop through the 'assets' folder and check each file
        for file in os.listdir(os.path.join("data","assets")):
            # If the file name starts with name (i.e. the file corresponds to the asset
            # object that is currently generated)
            if file.startswith(name):
                # Construct the full name of the asset (incl. folder structure)
                self.__full_name = os.path.join(os.path.join("data","assets"), file)
                # Find the asset's currency from the file's name
                self.__currency  = self.__full_name.split("_")[-1].split(".")[0]
                # Read the asset .csv into Python (in a Pandas DataFrame)
                df = pd.read_csv(self.__full_name)
                # Convert the date column to a date format (instead of string)
                df["date"] = pd.to_datetime(df["date"])
                # DONE
                print("success", self.__full_name)
                # Store the dataframe, such that we can access it later
                self.__prices = df

    # Getter function
    def get_name(self):
        return self.__name

    # Getter function
    def get_category(self):
        return self.__category

    # Getter function
    def get_full_name(self):
        return self.__full_name

    # Getter function
    def get_currency(self):
        return self.__currency

    # Getter function
    def get_prices(self):
        return self.__prices

# These are lists of all asset names (strings).
bonds_assets = ['FB1_Comdty', 'TU1_Comdty', 'FV1_Comdty', 'TY1_Comdty', 'WN1_Comdty', 'CV1_Comdty',
                        'XQ1_Comdty', 'CN1_Comdty', 'LGB1_Comdty', 'WB1_Comdty', 'WX1_Comdty', 'G 1_Comdty',
                        'UGL1_Comdty', 'DU1_Comdty', 'OE1_Comdty', 'RX1_Comdty', 'UB1_Comdty', 'IK1_Comdty',
                        'OAT1_Comdty', 'XM1_Comdty', 'JB1_Comdty', 'KAA1_Comdty', 'TFT1_Comdty']
equity_assets = ['SM1_Index', 'ES1_Index', 'PT1_Index', 'VG1_Index', 'Z 1_Index', 'GX1_Index', 'ST1_Index',
                        'CF1_Index', 'OI1_Index', 'QC1_Index', 'ATT1_Index', 'BE1_Index', 'EO1_Index', 'OT1_Index',
                        'XP1_Index', 'TP1_Index', 'NI1_Index', 'HI1_Index', 'IH1_Index', 'MES1_Index', 'BZ1_Index']
commodity_assets = ['CL1_Comdty', 'QS1_Comdty', 'XB1_Comdty', 'HO1_Comdty', 'NG1_Comdty',
                                'LMAHDS03 LME_Comdty', 'LMCADS03_Comdty', 'LMNIDS03_Comdty', 'GC1_Comdty', 'SI1_Comdty',
                                'LC1_Comdty', 'KC1_Comdty', 'C 1_Comdty', 'CT1_Comdty', 'S 1_Comdty', 'SB1_Comdty', 'W 1_Comdty']

# These initialize asset objects for each asset
all_assets = {"bonds": [Asset(x, "bonds") for x in bonds_assets],
                    "equity": [Asset(x, "equity") for x in equity_assets],
                    "commodity": [Asset(x, "commodity") for x in commodity_assets]}

class AssetNone:

    # This function is automatically called when a new Asset() object is generated
    def __init__(self, name):

        # Ensure that name is a string
        assert isinstance(name, str), f"name '{name}' is not a string"
        # Store name as object attribute
        self.__name = name

        # For-loop through the 'assets' folder and check each file
        for file in os.listdir(os.path.join("data","assets_none")):
            # If the file name starts with name (i.e. the file corresponds to the asset
            # object that is currently generated)
            if file.startswith(name):
                # Construct the full name of the asset (incl. folder structure)
                self.__full_name = os.path.join(os.path.join("data","assets_none"), file)
                # Read the asset .csv into Python (in a Pandas DataFrame)
                df = pd.read_csv(self.__full_name)
                # Convert the date column to a date format (instead of string)
                df["date"] = pd.to_datetime(df["date"])
                # DONE
                print("success", self.__full_name)
                # Store the dataframe, such that we can access it later
                self.__prices = df

    # Getter function
    def get_name(self):
        return self.__name

    # Getter function
    def get_full_name(self):
        return self.__full_name

    # Getter function
    def get_prices(self):
        return self.__prices

all_assets_none = {x: AssetNone(x) for x in bonds_assets + equity_assets + commodity_assets}
#########################################################################################################################


#########################################################################################################################
class All_assets:

    def __init__(self, category, all_assets, start_point):
        self.__category = category
        self.__start_point = start_point
        df = pd.DataFrame(index=pd.date_range(start=start_point, end="2023-12-31"))
        df["weekday"] = df.index.day_name()
        if category == "all":
            self.__all_assets = all_assets
            for category, assets in all_assets.items():
                for asset in assets:
                    asset_df = asset.get_prices().set_index("date")
                    first_day = asset_df.iloc[0].name - datetime.timedelta(days=1)
                    asset_df = asset_df[[f"{asset.get_name()}_PX-LAST-CHF", f"{asset.get_name()}_start"]]
                    new_df = pd.DataFrame(index=pd.date_range(start=start_point, end="2023-12-31")).join(asset_df, how="left")
                    new_df.loc[:first_day, f"{asset.get_name()}_start"] = "excluded"
                    df = df.join(new_df, how="left")
        elif category == "equity_bonds":
            all_assets = {k:v for k,v in all_assets.items() if k in ("equity", "bonds")}
            self.__all_assets = all_assets
            for category, assets in all_assets.items():
                for asset in assets:
                    asset_df = asset.get_prices().set_index("date")
                    first_day = asset_df.iloc[0].name - datetime.timedelta(days=1)
                    asset_df = asset_df[[f"{asset.get_name()}_PX-LAST-CHF", f"{asset.get_name()}_start"]]
                    new_df = pd.DataFrame(index=pd.date_range(start=start_point, end="2023-12-31")).join(asset_df, how="left")
                    new_df.loc[:first_day, f"{asset.get_name()}_start"] = "excluded"
                    df = df.join(new_df, how="left")
        elif category == "equity_bonds_partial_commodity_2":
            all_assets_new = {k:v for k,v in all_assets.items() if k in ("equity", "bonds")}
            all_assets_new["commodity"] = [x for x in all_assets["commodity"] if x.get_name() in ("CL1_Comdty", "GC1_Comdty")]
            all_assets = all_assets_new
            self.__all_assets = all_assets
            for category, assets in all_assets.items():
                for asset in assets:
                    asset_df = asset.get_prices().set_index("date")
                    first_day = asset_df.iloc[0].name - datetime.timedelta(days=1)
                    asset_df = asset_df[[f"{asset.get_name()}_PX-LAST-CHF", f"{asset.get_name()}_start"]]
                    new_df = pd.DataFrame(index=pd.date_range(start=start_point, end="2023-12-31")).join(asset_df, how="left")
                    new_df.loc[:first_day, f"{asset.get_name()}_start"] = "excluded"
                    df = df.join(new_df, how="left")

        else:
            self.__all_assets = all_assets[category]
            for asset in all_assets[category]:
                asset_df = asset.get_prices().set_index("date")
                first_day = asset_df.iloc[0].name - datetime.timedelta(days=1)
                asset_df = asset_df[[f"{asset.get_name()}_PX-LAST-CHF", f"{asset.get_name()}_start"]]
                new_df = pd.DataFrame(index=pd.date_range(start=start_point, end="2023-12-31")).join(asset_df, how="left")
                new_df.loc[:first_day, f"{asset.get_name()}_start"] = "excluded"
                df = df.join(new_df, how="left")
        self.__merged_df = df

    def get_category(self):
        return self.__category

    def get_start_point(self):
        return self.__start_point

    def get_all_assets(self):
        return self.__all_assets

    def get_merged_df(self):
        return self.__merged_df

bonds_df = All_assets("bonds", all_assets, "1997-08-15")
equity_df = All_assets("equity", all_assets, "1997-08-15")
equity_bonds_df = All_assets("equity_bonds", all_assets, "1997-08-15")
commodity_df = All_assets("commodity", all_assets, "1997-08-15")
all_df = All_assets("all", all_assets, "1997-08-15")
equity_bonds_partial_commodity_2_df = All_assets("equity_bonds_partial_commodity_2", all_assets, "1997-08-15")
#########################################################################################################################


#########################################################################################################################
# This class is used to generate the backtest, handling all work
class Backtest:

    # Generate a backtest object
    def __init__(self, strategy, weighting, trading_freq, roll_data, all_assets):
        # Store object attributes
        self.__strategy = strategy
        assert weighting in ("equal", "vola"), "weighting not defined"
        self.__weighting = weighting
        self.__trading_freq = trading_freq
        assert roll_data in ("ratio", "none"), "roll data not defined"
        self.__roll_data = roll_data
        self.__all_assets = all_assets
        self.__tradeable_assets = {}
        # Run the backtest
        self.find_trading_days()
        self.run_backtest()
        self.save_results()
        # Store mean of weighted return
        with open(os.path.join("results_FINAL_equityBondsPartialCommodity2", "backtest_summary_FINAL_equityBondsPartialCommodity2.txt"), "a") as file:  # 'a' mode appends to the file without overwriting
            file.write(f"{self.__all_assets.get_category()}_{self.__strategy}_{self.__trading_freq}_{self.__weighting}_{self.__roll_data}::::::::::::{self.__all_trades['weighted_return'].mean()}, {self.__all_trades['weighted_return_l'].mean()}, {self.__all_trades['weighted_return_s'].mean()}\n")
        print("DONE")

    # Getter
    def get_strategy(self):
        return self.__strategy

    # Getter
    def get_weighting(self):
        return self.__weighting

    # Getter
    def get_trading_freq(self):
        return self.__trading_freq

    # Getter
    def get_roll_data(self):
        return self.__roll_data

    # Getter
    def get_all_assets(self):
        return self.__all_assets

    # Getter
    def get_trading_days(self):
        return self.__trading_days

    # Getter
    def get_all_returns(self):
        return self.__all_returns

    # Getter
    def get_signals(self):
        return self.__signals

    # Getter
    def get_all_trades(self):
        return self.__all_trades

    def find_trading_days(self):
        first_friday = pd.to_datetime(self.__all_assets.get_start_point()) # "1997-08-15"
        last_friday = pd.to_datetime("2023-12-29") # 5. (last) Friday in December
        trading_days = []
        # If we trade monthly, we always trade at the first day of the month
        if self.__trading_freq == "monthly":
            current_year, current_month= first_friday.year, first_friday.month+1
            while current_year < last_friday.year or (current_year == last_friday.year and current_month <= last_friday.month):
                first_of_month = pd.Timestamp(current_year, current_month, 1)
                current_friday = first_of_month + pd.Timedelta(days=(4 - first_of_month.weekday()) % 7)
                trading_days.append(current_friday)
                if current_month == 12:
                    current_month = 1
                    current_year += 1
                else:
                    current_month += 1
        # If we trade weekly, we trade each Friday
        elif self.__trading_freq == "weekly":
            current_friday = first_friday
            while current_friday <= last_friday:
                trading_days.append(current_friday)
                current_friday += pd.Timedelta(days=7)
        # If we trade twice a year, we always trade at the first day of each 6th month
        elif self.__trading_freq == "biyearly":
            current_year, current_month= first_friday.year, first_friday.month+1
            while current_year < last_friday.year or (current_year == last_friday.year and current_month <= last_friday.month):
                first_of_month = pd.Timestamp(current_year, current_month, 1)
                current_friday = first_of_month + pd.Timedelta(days=(4 - first_of_month.weekday()) % 7)
                trading_days.append(current_friday)
                current_month += 6
                if current_month > 12:
                    current_month -=12
                    current_year += 1
        # empty for now
        else:
            raise "trading frequency not defined"
        self.__trading_days = trading_days

    def run_backtest(self):
        self.__all_returns = self.__all_assets.get_merged_df().loc[:]
        start_columns = [col for col in self.__all_returns if col.endswith("_start")]
        for col in start_columns:
            name = "_".join(col.split("_")[:-1])
            position = self.__all_returns.columns.get_loc(col)
            self.__all_returns.insert(position+1, f"{name}_{self.__trading_freq}Return", np.nan)
        reversed_trading_days = list(reversed(self.__trading_days))
        for i, trading_day in enumerate(reversed_trading_days):
            if i < len(self.__trading_days)-1:
                print("0               ", trading_day)
                for col in start_columns:
                    name = "_".join(col.split("_")[:-1])
                    lookback_date_buy = reversed_trading_days[i+1]
                    lookback_date_sell = trading_day
                    if self.__all_returns.loc[lookback_date_buy, col] == "excluded" or self.__all_returns.loc[lookback_date_sell, col] == "excluded" or self.__all_returns.loc[lookback_date_buy, col] == "sell":
                        continue
                    if self.__all_returns.loc[lookback_date_buy, col] == "start":
                        lookback_buy = self.__all_returns.loc[lookback_date_buy][f"{name}_PX-LAST-CHF"]
                    else: # failsafe
                        print(name, col, trading_day)
                        raise ReturnError1
                    if self.__all_returns.loc[lookback_date_sell, col] in ("start", "sell"):
                        lookback_sell = self.__all_returns.loc[lookback_date_sell][f"{name}_PX-LAST-CHF"]
                    else: # failsafe
                        print(name, col, trading_day)
                        raise ReturnError2
                    self.__all_returns.loc[trading_day, f"{name}_{self.__trading_freq}Return"] = (lookback_sell - lookback_buy) / lookback_buy


        self.__signals = self.__all_assets.get_merged_df().loc[:]
        start_columns = [col for col in self.__signals if col.endswith("_start")]
        for col in start_columns:
            name = "_".join(col.split("_")[:-1])
            position = self.__signals.columns.get_loc(col)
            self.__signals.insert(position+1, f"{name}_signal", np.nan)
            self.__signals.insert(position+2, f"{name}_signal_calculation", np.nan)
            self.__signals.insert(position+3, f"{name}_vola", np.nan)
            self.__signals.insert(position+4, f"{name}_vola_calculation", np.nan)
            if self.__roll_data == "none":
                merged_df = self.__signals.merge(all_assets_none[name].get_prices().set_index("date"), left_index=True, right_index=True, how="left")
                self.__signals.insert(position+5, f"{name}_nonePrice", merged_df[f"{name}_PX-LAST-CHF_y"])
        first_trading_day = self.__trading_days[0] + pd.DateOffset(years=5, months=6)
        filtered_trading_days = [date for date in self.__trading_days if date >= first_trading_day]
        if self.__roll_data == "none":
            set_roll_data = "nonePrice"
        elif self.__roll_data == "ratio":
            set_roll_data = "PX-LAST-CHF"
        for trading_day in filtered_trading_days:
            print("1               ", trading_day)
            for col in start_columns:
                name = "_".join(col.split("_")[:-1])
                lookback_date_vola_b = trading_day - pd.DateOffset(years=1)
                lookback_date_vola_s = trading_day - pd.DateOffset(days=1)
                vola_filtered_df = self.__signals.loc[lookback_date_vola_b:lookback_date_vola_s]
                vola_filtered_df = vola_filtered_df[vola_filtered_df["weekday"].isin(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])]
                vola_filtered_df = vola_filtered_df[f"{name}_{set_roll_data}"]

                if self.__strategy.startswith("basic_momentum") or self.__strategy.startswith("adj_momentum"):
                    start_mom = self.__strategy.split("+")[1].split("-")
                    end_mom = self.__strategy.split("+")[2].split("-")
                    lookback_date_buy = trading_day - pd.DateOffset(years=int(start_mom[0]), months=int(start_mom[1]), days=int(start_mom[2]))
                    lookback_date_sell = trading_day - pd.DateOffset(years=int(end_mom[0]), months=int(end_mom[1]), days=int(end_mom[2]))
                    if self.__signals.loc[lookback_date_buy, col] == "excluded" or self.__signals.loc[lookback_date_sell, col] == "excluded" or vola_filtered_df.notna().sum() < 130:
                        self.__signals.loc[trading_day, f"{name}_signal_calculation"] = str(lookback_date_buy.date()) + "," + str(lookback_date_sell.date())
                        self.__signals.loc[trading_day, f"{name}_vola_calculation"] = str(lookback_date_vola_b.date()) + "," + str(lookback_date_vola_s.date())
                        continue
                    if pd.notnull(self.__signals.loc[lookback_date_buy][f"{name}_{set_roll_data}"]): # failsafe, can be removed later
                        lookback_buy = self.__signals.loc[lookback_date_buy][f"{name}_{set_roll_data}"]
                    else: # failsafe, can be removed later
                        print(name, col, trading_day)
                        raise Error1
                    if pd.notnull(self.__signals.loc[lookback_date_sell][f"{name}_{set_roll_data}"]): # failsafe, can be removed later
                        lookback_sell = self.__signals.loc[lookback_date_sell][f"{name}_{set_roll_data}"]
                    else: # failsafe, can be removed later
                        print(name, col, trading_day)
                        raise Error2
                    if self.__strategy.startswith("basic_momentum"):
                        if self.__strategy.startswith("basic_momentum_contra") and (name in bonds_assets or name in equity_assets):
                            self.__signals.loc[trading_day, f"{name}_signal"] = -(lookback_sell - lookback_buy) / lookback_buy
                        else:
                            self.__signals.loc[trading_day, f"{name}_signal"] = (lookback_sell - lookback_buy) / lookback_buy
                        self.__signals.loc[trading_day, f"{name}_signal_calculation"] = str(lookback_date_buy.date()) + "," + str(lookback_date_sell.date())
                    elif self.__strategy.startswith("adj_momentum"):
                        lookback_date_vola_signal_b = trading_day - pd.DateOffset(years=1)
                        vola_filtered_signal_df = vola_filtered_df.loc[lookback_date_vola_signal_b:]
                        if self.__strategy.startswith("adj_momentum_contra") and (name in bonds_assets or name in equity_assets):
                            self.__signals.loc[trading_day, f"{name}_signal"] = -((lookback_sell - lookback_buy) / lookback_buy) / vola_filtered_signal_df.pct_change().std()
                        else:
                            self.__signals.loc[trading_day, f"{name}_signal"] = ((lookback_sell - lookback_buy) / lookback_buy) / vola_filtered_signal_df.pct_change().std()
                        self.__signals.loc[trading_day, f"{name}_signal_calculation"] = str(lookback_date_buy.date()) + "," + str(lookback_date_sell.date())

                elif self.__strategy.startswith("basic_value") or self.__strategy.startswith("adj_value"):
                    lookback_date_buy_1 = trading_day - pd.DateOffset(years=5, months=6)
                    lookback_date_buy_2 = trading_day - pd.DateOffset(years=4, months=6)
                    value_b_filtered_df = self.__signals.loc[lookback_date_buy_1:lookback_date_buy_2]
                    value_b_filtered_df = value_b_filtered_df[value_b_filtered_df["weekday"].isin(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])]
                    value_b_filtered_df = value_b_filtered_df[f"{name}_{set_roll_data}"]
                    lookback_date_sell = trading_day - pd.DateOffset(days=1)
                    if value_b_filtered_df.notna().sum() < 65 or self.__signals.loc[lookback_date_sell, col] == "excluded" or vola_filtered_df.notna().sum() < 130:
                        self.__signals.loc[trading_day, f"{name}_signal_calculation"] = str(lookback_date_buy_1.date()) + "-" + str(lookback_date_buy_2.date()) + "," + str(lookback_date_sell.date())
                        self.__signals.loc[trading_day, f"{name}_vola_calculation"] = str(lookback_date_vola_b.date()) + "," + str(lookback_date_vola_s.date())
                        continue
                    lookback_buy = value_b_filtered_df.mean()
                    if pd.notnull(self.__signals.loc[lookback_date_sell][f"{name}_{set_roll_data}"]): # failsafe, can be removed later
                        lookback_sell = self.__signals.loc[lookback_date_sell][f"{name}_{set_roll_data}"]
                    else: # failsafe, can be removed later
                        print(name, col, trading_day)
                        raise Error2
                    if self.__strategy.startswith("basic_value"):
                        self.__signals.loc[trading_day, f"{name}_signal"] = np.log(lookback_buy / lookback_sell)
                        self.__signals.loc[trading_day, f"{name}_signal_calculation"] = str(lookback_date_buy_1.date()) + "-" + str(lookback_date_buy_2.date()) + "," + str(lookback_date_sell.date())
                    elif self.__strategy.startswith("adj_value"):
                        lookback_date_vola_signal_b = trading_day - pd.DateOffset(years=1)
                        vola_filtered_signal_df = vola_filtered_df.loc[lookback_date_vola_signal_b:]
                        self.__signals.loc[trading_day, f"{name}_signal"] = (np.log(lookback_buy / lookback_sell)) / vola_filtered_signal_df.pct_change().std()
                        self.__signals.loc[trading_day, f"{name}_signal_calculation"] = str(lookback_date_buy_1.date()) + "-" + str(lookback_date_buy_2.date()) + "," + str(lookback_date_sell.date())


                else:
                    raise "strategy not defined"

                self.__signals.loc[trading_day, f"{name}_vola"] = vola_filtered_df.pct_change().std()
                self.__signals.loc[trading_day, f"{name}_vola_calculation"] = str(lookback_date_vola_b.date()) + "," + str(lookback_date_vola_s.date())


        self.__all_trades = self.__all_returns.loc[:][filtered_trading_days[0]:filtered_trading_days[-1]]
        start_columns = [col for col in self.__all_trades if col.endswith("_start")]
        for i, trading_day in enumerate(filtered_trading_days):
            print("2               ", trading_day)
            for col in start_columns:
                name = "_".join(col.split("_")[:-1])
                if trading_day == filtered_trading_days[0]:
                    position = self.__all_trades.columns.get_loc(col)
                    self.__all_trades.insert(position+2, f"{name}_buy", np.nan)
                    self.__all_trades.insert(position+3, f"{name}_sell", np.nan)
                    self.__all_trades.loc[trading_day, f"{name}_{self.__trading_freq}Return"] = np.nan
                    if self.__all_trades.loc[trading_day, col] == "start":
                        if pd.notnull(self.__signals.loc[trading_day, f"{name}_signal"]):
                            if self.__all_trades.loc[filtered_trading_days[i+1], col] != "excluded":
                                if pd.notnull(self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_{self.__trading_freq}Return"]):
                                    self.__all_trades.loc[trading_day, f"{name}_buy"] = "buy"
                elif trading_day != filtered_trading_days[-1]:
                    if self.__all_trades.loc[trading_day, col] == "start":
                        if pd.notnull(self.__signals.loc[trading_day, f"{name}_signal"]):
                            if self.__all_trades.loc[filtered_trading_days[i+1], col] != "excluded":
                                if pd.notnull(self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_{self.__trading_freq}Return"]):
                                    self.__all_trades.loc[trading_day, f"{name}_buy"] = "buy"
                else:
                    pass


        self.__all_trades["considered_assets"] = None
        self.__all_trades["weighted_return"] = np.nan
        self.__all_trades["weighted_return_l"] = np.nan
        self.__all_trades["weighted_return_s"] = np.nan
        for i, trading_day in enumerate(filtered_trading_days):
            print("3               ", trading_day)
            considered_assets = {}
            for col in start_columns:
                name = "_".join(col.split("_")[:-1])
                if self.__all_trades.loc[trading_day, f"{name}_buy"] == "buy":
                    considered_assets[name] = self.__signals.loc[trading_day, f"{name}_signal"]
            considered_assets = dict(sorted(considered_assets.items(), key=lambda item: item[1], reverse=True))
            self.__all_trades.at[trading_day, "considered_assets"] = considered_assets
            if len(considered_assets) == 0:
                continue
            elif len(considered_assets) < 10:
                print(considered_assets)
                raise consideredAssetsError
            else:
                nr_assets = 5
            top_x_keys = list(considered_assets)[:nr_assets]
            lowest_x_keys = list(considered_assets)[-nr_assets:]
            total_vola_long = 0
            total_vola_short = 0
            for col in start_columns:
                name = "_".join(col.split("_")[:-1])
                if name in top_x_keys:
                    total_vola_long += (1 / self.__signals.loc[trading_day, f"{name}_vola"])
                    self.__all_trades.loc[trading_day, f"{name}_buy"] = 100/nr_assets
                elif name in lowest_x_keys:
                    total_vola_short += (1 / self.__signals.loc[trading_day, f"{name}_vola"])
                    self.__all_trades.loc[trading_day, f"{name}_buy"] = -100/nr_assets
                else:
                    self.__all_trades.loc[trading_day, f"{name}_buy"] = np.nan
            for col in start_columns:
                name = "_".join(col.split("_")[:-1])
                if pd.notnull(self.__all_trades.loc[trading_day, f"{name}_buy"]):
                    if self.__weighting == "vola":
                        inverse_vola = 1 / self.__signals.loc[trading_day, f"{name}_vola"]
                        if self.__all_trades.loc[trading_day, f"{name}_buy"] > 0:
                            self.__all_trades.loc[trading_day, f"{name}_buy"] = (inverse_vola / total_vola_long) * 100
                        elif self.__all_trades.loc[trading_day, f"{name}_buy"] < 0:
                            self.__all_trades.loc[trading_day, f"{name}_buy"] = -(inverse_vola / total_vola_short) * 100
                        else: # failsafe
                            raise VolaError
                    self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_sell"] = self.__all_trades.loc[trading_day, f"{name}_buy"]
                    current_weighted_return = self.__all_trades.loc[filtered_trading_days[i+1], "weighted_return"]
                    if np.isnan(self.__all_trades.loc[filtered_trading_days[i+1], "weighted_return"]):
                        current_weighted_return = 0
                    new_weighted_return =  self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_sell"] / 100 * self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_{self.__trading_freq}Return"]
                    self.__all_trades.loc[filtered_trading_days[i+1], "weighted_return"] = current_weighted_return + new_weighted_return

                    current_weighted_return_l = self.__all_trades.loc[filtered_trading_days[i+1], "weighted_return_l"]
                    if np.isnan(self.__all_trades.loc[filtered_trading_days[i+1], "weighted_return_l"]):
                        current_weighted_return_l = 0
                    if self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_sell"] > 0:
                        new_weighted_return_l =  self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_sell"] / 100 * self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_{self.__trading_freq}Return"]
                        self.__all_trades.loc[filtered_trading_days[i+1], "weighted_return_l"] = current_weighted_return_l + new_weighted_return_l

                    current_weighted_return_s = self.__all_trades.loc[filtered_trading_days[i+1], "weighted_return_s"]
                    if np.isnan(self.__all_trades.loc[filtered_trading_days[i+1], "weighted_return_s"]):
                        current_weighted_return_s = 0
                    if self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_sell"] < 0:
                        new_weighted_return_s =  self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_sell"] / 100 * self.__all_trades.loc[filtered_trading_days[i+1], f"{name}_{self.__trading_freq}Return"]
                        self.__all_trades.loc[filtered_trading_days[i+1], "weighted_return_s"] = current_weighted_return_s + new_weighted_return_s

    def save_results(self):
        self.__all_assets.get_merged_df().to_csv(os.path.join("results_FINAL_equityBondsPartialCommodity2", f"{self.__all_assets.get_category()}_{self.__strategy}_{self.__trading_freq}_{self.__weighting}_{self.__roll_data}_data.csv"))
        self.__all_returns.to_csv(os.path.join("results_FINAL_equityBondsPartialCommodity2", f"{self.__all_assets.get_category()}_{self.__strategy}_{self.__trading_freq}_{self.__weighting}_{self.__roll_data}_returns.csv"))
        self.__signals.to_csv(os.path.join("results_FINAL_equityBondsPartialCommodity2", f"{self.__all_assets.get_category()}_{self.__strategy}_{self.__trading_freq}_{self.__weighting}_{self.__roll_data}_signals.csv"))
        self.__all_trades.to_csv(os.path.join("results_FINAL_equityBondsPartialCommodity2", "trades", f"{self.__all_assets.get_category()}_{self.__strategy}_{self.__trading_freq}_{self.__weighting}_{self.__roll_data}_trades.csv"))



assets_to_use = equity_bonds_partial_commodity_2_df
### MOMENTUM
# Basic momentum 0-12-0:0-0-1
Backtest("basic_momentum+0-12-0+0-0-1", "equal", "weekly", "none", assets_to_use)
Backtest("basic_momentum+0-12-0+0-0-1", "vola", "weekly", "none", assets_to_use)
Backtest("basic_momentum+0-12-0+0-0-1", "equal", "weekly", "ratio", assets_to_use)
Backtest("basic_momentum+0-12-0+0-0-1", "vola", "weekly", "ratio", assets_to_use)
# Adj. momentum 0-12-0:0-0-1
Backtest("adj_momentum+0-12-0+0-0-1", "equal", "weekly", "none", assets_to_use)
Backtest("adj_momentum+0-12-0+0-0-1", "vola", "weekly", "none", assets_to_use)
Backtest("adj_momentum+0-12-0+0-0-1", "equal", "weekly", "ratio", assets_to_use)
Backtest("adj_momentum+0-12-0+0-0-1", "vola", "weekly", "ratio", assets_to_use)
# Basic momentum 0-12-0:0-1-0
Backtest("basic_momentum+0-12-0+0-1-0", "equal", "weekly", "none", assets_to_use)
Backtest("basic_momentum+0-12-0+0-1-0", "vola", "weekly", "none", assets_to_use)
Backtest("basic_momentum+0-12-0+0-1-0", "equal", "weekly", "ratio", assets_to_use)
Backtest("basic_momentum+0-12-0+0-1-0", "vola", "weekly", "ratio", assets_to_use)
# Adj. momentum 0-12-0:0-1-0
Backtest("adj_momentum+0-12-0+0-1-0", "equal", "weekly", "none", assets_to_use)
Backtest("adj_momentum+0-12-0+0-1-0", "vola", "weekly", "none", assets_to_use)
Backtest("adj_momentum+0-12-0+0-1-0", "equal", "weekly", "ratio", assets_to_use)
Backtest("adj_momentum+0-12-0+0-1-0", "vola", "weekly", "ratio", assets_to_use)
# Basic momentum 0-1-0:0-0-1
Backtest("basic_momentum+0-1-0+0-0-1", "equal", "weekly", "none", assets_to_use)
Backtest("basic_momentum+0-1-0+0-0-1", "vola", "weekly", "none", assets_to_use)
Backtest("basic_momentum+0-1-0+0-0-1", "equal", "weekly", "ratio", assets_to_use)
Backtest("basic_momentum+0-1-0+0-0-1", "vola", "weekly", "ratio", assets_to_use)
# Adj. momentum 0-1-0:0-0-1
Backtest("adj_momentum+0-1-0+0-0-1", "equal", "weekly", "none", assets_to_use)
Backtest("adj_momentum+0-1-0+0-0-1", "vola", "weekly", "none", assets_to_use)
Backtest("adj_momentum+0-1-0+0-0-1", "equal", "weekly", "ratio", assets_to_use)
Backtest("adj_momentum+0-1-0+0-0-1", "vola", "weekly", "ratio", assets_to_use)

### VALUE
Backtest("basic_value", "equal", "weekly", "none", assets_to_use)
Backtest("basic_value", "equal", "weekly", "ratio", assets_to_use)
Backtest("basic_value", "vola", "weekly", "none", assets_to_use)
Backtest("basic_value", "vola", "weekly", "ratio", assets_to_use)
Backtest("adj_value", "equal", "weekly", "none", assets_to_use)
Backtest("adj_value", "equal", "weekly", "ratio", assets_to_use)
Backtest("adj_value", "vola", "weekly", "none", assets_to_use)
Backtest("adj_value", "vola", "weekly", "ratio", assets_to_use)

### CONTRARIAN
# Basic momentum 0-12-0:0-0-1 CONTRA
Backtest("basic_momentum_contra+0-12-0+0-0-1", "equal", "weekly", "none", assets_to_use)
Backtest("basic_momentum_contra+0-12-0+0-0-1", "vola", "weekly", "none", assets_to_use)
Backtest("basic_momentum_contra+0-12-0+0-0-1", "equal", "weekly", "ratio", assets_to_use)
Backtest("basic_momentum_contra+0-12-0+0-0-1", "vola", "weekly", "ratio", assets_to_use)
# Adj. momentum 0-12-0:0-0-1 CONTRA
Backtest("adj_momentum_contra+0-12-0+0-0-1", "equal", "weekly", "none", assets_to_use)
Backtest("adj_momentum_contra+0-12-0+0-0-1", "vola", "weekly", "none", assets_to_use)
Backtest("adj_momentum_contra+0-12-0+0-0-1", "equal", "weekly", "ratio", assets_to_use)
Backtest("adj_momentum_contra+0-12-0+0-0-1", "vola", "weekly", "ratio", assets_to_use)
# Basic momentum 0-12-0:0-1-0 CONTRA
Backtest("basic_momentum_contra+0-12-0+0-1-0", "equal", "weekly", "none", assets_to_use)
Backtest("basic_momentum_contra+0-12-0+0-1-0", "vola", "weekly", "none", assets_to_use)
Backtest("basic_momentum_contra+0-12-0+0-1-0", "equal", "weekly", "ratio", assets_to_use)
Backtest("basic_momentum_contra+0-12-0+0-1-0", "vola", "weekly", "ratio", assets_to_use)
# Adj. momentum 0-12-0:0-1-0 CONTRA
Backtest("adj_momentum_contra+0-12-0+0-1-0", "equal", "weekly", "none", assets_to_use)
Backtest("adj_momentum_contra+0-12-0+0-1-0", "vola", "weekly", "none", assets_to_use)
Backtest("adj_momentum_contra+0-12-0+0-1-0", "equal", "weekly", "ratio", assets_to_use)
Backtest("adj_momentum_contra+0-12-0+0-1-0", "vola", "weekly", "ratio", assets_to_use)
# Basic momentum 0-1-0:0-0-1 CONTRA
Backtest("basic_momentum_contra+0-1-0+0-0-1", "equal", "weekly", "none", assets_to_use)
Backtest("basic_momentum_contra+0-1-0+0-0-1", "vola", "weekly", "none", assets_to_use)
Backtest("basic_momentum_contra+0-1-0+0-0-1", "equal", "weekly", "ratio", assets_to_use)
Backtest("basic_momentum_contra+0-1-0+0-0-1", "vola", "weekly", "ratio", assets_to_use)
# Adj. momentum 0-1-0:0-0-1 CONTRA
Backtest("adj_momentum_contra+0-1-0+0-0-1", "equal", "weekly", "none", assets_to_use)
Backtest("adj_momentum_contra+0-1-0+0-0-1", "vola", "weekly", "none", assets_to_use)
Backtest("adj_momentum_contra+0-1-0+0-0-1", "equal", "weekly", "ratio", assets_to_use)
Backtest("adj_momentum_contra+0-1-0+0-0-1", "vola", "weekly", "ratio", assets_to_use)
