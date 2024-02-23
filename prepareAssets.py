import pandas as pd
import numpy as np
import os
import datetime


class prepareAsset:

    def __init__(self, name, first_date, storage_flag=False):

        assert isinstance(name, str), f"name '{name}' is not a string"
        for file in os.listdir(os.path.join("data","assets_raw")):
            if file.startswith(name):
                self.__full_name = os.path.join(os.path.join("data","assets_raw"), file)
                self.__currency  = self.__full_name.split("_")[-1].split(".")[0]
                # Read in all data to a DataFrame
                df_data = pd.read_csv(self.__full_name, usecols=[1,2])
                # Find bigger of the two dates
                second_date = df_data.iloc[0]["date"]
                chosen_date = second_date if pd.Timestamp(second_date) > pd.Timestamp(first_date) else first_date
                ###############################################################################
                # for now to prevent the bug DMark-EUR
                if name == "UB1_Comdty":
                    chosen_date = "1999-01-01"
                ###############################################################################
                # Construct an empty date DataFrame
                df_date = pd.DataFrame(index=pd.date_range(start=chosen_date, end="2023-12-31"))
                # Merge both DataFrames
                df_data["date"] = pd.to_datetime(df_data["date"])
                df = df_date.merge(df_data, how="left", left_index=True, right_on="date").reset_index(drop=True)
                # Add the weekday
                df.insert(1, "weekday", df["date"].dt.day_name())
                # Create unique columns names
                df = df.rename(columns={"PX_LAST": f"{name}_PX-LAST"})
                df["imputed"] = np.nan
                df[f"{name}_start"] = np.nan


                # Find the first tradeable Friday
                start_check = int(df[(df["weekday"] == "Friday") & (df[f"{name}_PX-LAST"].notnull())].first_valid_index())
                df.iloc[start_check, df.columns.get_loc(f"{name}_start")] = "start"

                while start_check != "end of backtest period reached":

                    # 2 weeks before end of dataset
                    if start_check + 14 < len(df.index):
                        start_set = False
                        #####################################################################
                        # If Friday in 2 weeks exists
                        if pd.notnull(df.iloc[start_check+14][f"{name}_PX-LAST"]):
                            # If Friday in 1 week exists
                            if pd.notnull(df.iloc[start_check+7][f"{name}_PX-LAST"]):
                                # We set this Friday to start
                                df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                            # If Friday in 1 week does not exist
                            else:
                                # We look backwards
                                for s in range(start_check+6, start_check-1, -1):
                                    # If there exists a value...
                                    if pd.notnull(df.iloc[s][f"{name}_PX-LAST"]):
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = df.iloc[s][f"{name}_PX-LAST"]
                                        df.iloc[start_check+7, df.columns.get_loc("imputed")] = f"imputed from {s}"
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                                        start_set = True
                                        break
                                if not start_set:
                                    df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                    df.iloc[start_check+7, df.columns.get_loc("imputed")] = np.nan
                                    df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "excluded"


                        # If Friday in 2 weeks does not exist
                        else:
                            start_set = False
                            # imputed down until FR 2 weeks ago
                            for s in range(start_check+13, start_check, -1):
                                if pd.notnull(df.iloc[s][f"{name}_PX-LAST"]):
                                    start_set = True
                                    break
                            if start_set:
                                start_set = False
                                if pd.notnull(df.iloc[start_check+7][f"{name}_PX-LAST"]):
                                    df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                                    start_set = True
                                else:
                                    for s in range(start_check+6, start_check-1, -1):
                                        if pd.notnull(df.iloc[s][f"{name}_PX-LAST"]):
                                            df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = df.iloc[s][f"{name}_PX-LAST"]
                                            df.iloc[start_check+7, df.columns.get_loc("imputed")] = f"imputed from {s}"
                                            df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                                            start_set = True
                                            break
                                    if not start_set:
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                        df.iloc[start_check+7, df.columns.get_loc("imputed")] = np.nan
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "excluded"

                            else:
                                df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                df.iloc[start_check+7, df.columns.get_loc("imputed")] = np.nan
                                df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "excluded"

                        start_check += 7

                    # 1 week before end of dataset
                    elif start_check + 7 < len(df.index):
                        if pd.notnull(df.iloc[start_check+7][f"{name}_PX-LAST"]):
                            df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                        else:
                            for s in range(start_check+6, start_check-1, -1):
                                if pd.notnull(df.iloc[s][f"{name}_PX-LAST"]):
                                    if np.isnan(df.iloc[s]["imputed"]):
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = df.iloc[s][f"{name}_PX-LAST"]
                                        df.iloc[start_check+7, df.columns.get_loc("imputed")] = f"imputed from {s}"
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                                        break
                                    else:
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                        df.iloc[start_check+7, df.columns.get_loc("imputed")] = np.nan
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "excluded"
                                        break

                        start_check = "end of backtest period reached"

                    # end of dataset reached
                    else:
                        start_check = "end of backtest period reached"


                for i in range(len(df)-1, -1, -1):
                    if df.loc[i, "weekday"] == "Friday":
                        break

                if name == "KAA1_Comdty":
                    sell_point = pd.to_datetime("2008-09-12")
                    data_point = pd.to_datetime("2010-10-25")
                while i >= 0:
                    if df.iloc[i][f"{name}_start"] == "excluded":
                        i -= 7
                        if i >= 0:
                            if df.iloc[i][f"{name}_start"] == "start":
                                if isinstance(df.iloc[i]["imputed"], float):
                                    df.iloc[i, df.columns.get_loc(f"{name}_start")] = "sell"
                                else:
                                    df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                    df.iloc[i, df.columns.get_loc("imputed")] = np.nan
                                    df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"
                    else:
                        if i-7 >= 0:
                            if df.iloc[i][f"{name}_start"] == "start" and df.iloc[i-7][f"{name}_start"] == "excluded":
                                # if no data is found, the start is equal to the first data point
                                for _ in range(i-6, i):
                                    if pd.notnull(df.iloc[_][f"{name}_PX-LAST"]):
                                        df.iloc[_, df.columns.get_loc(f"{name}_start")] = "data"
                                        break
                        i -= 7
                    if name == "KAA1_Comdty":
                        if df.iloc[i]["date"] == sell_point:
                            df.iloc[i, df.columns.get_loc(f"{name}_start")] = "sell"
                        elif sell_point < df.iloc[i]["date"] < data_point:
                            df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                            df.iloc[i, df.columns.get_loc("imputed")] = np.nan
                            df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"

                first_start = False
                sell_found = False
                for i in range(0, len(df.index)):
                    if not first_start:
                        if isinstance(df.iloc[i, df.columns.get_loc(f"{name}_start")], float):
                            df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                            df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"
                        else:
                            first_start = True
                    else:
                        if df.iloc[i, df.columns.get_loc(f"{name}_start")] == "sell":
                            sell_found = True
                            continue
                        if sell_found:
                            if df.iloc[i, df.columns.get_loc(f"{name}_start")] in ("data", "start"):
                                sell_found = False
                                continue
                            if isinstance(df.iloc[i]["imputed"], float):
                                df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"
                            else:
                                df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                df.iloc[i, df.columns.get_loc("imputed")] = np.nan
                                df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"


                # Convert currencies
                if self.__currency == "CHF":
                    df = df.rename(columns={f"{name}_PX-LAST": f"{name}_PX-LAST-CHF"})
                else:
                    for file in os.listdir(os.path.join("data","support")):
                        if file.startswith(self.__currency):
                            df_currency = pd.read_csv(os.path.join("data","support", file), usecols=[1,2])
                            df_currency["date"] = pd.to_datetime(df_currency["date"])
                            df[f"{name}_CURRENCY-{self.__currency}"] = df["date"].map(df_currency.set_index("date")["PX_LAST"])
                            assert all((df.loc[df[f"{name}_PX-LAST"].notna(), f"{name}_CURRENCY-{self.__currency}"].notna())), \
                                f"Not all non-NaN {name}_PX-LAST entries have a corresponding non-NaN {name}_CURRENCY-{self.__currency} entry."
                            if self.__currency in ("JPY", "KRW"):
                                df[f"{name}_PX-LAST-CHF"] = df[f"{name}_PX-LAST"] * df[f"{name}_CURRENCY-{self.__currency}"] / 100
                            else:
                                df[f"{name}_PX-LAST-CHF"] = df[f"{name}_PX-LAST"] * df[f"{name}_CURRENCY-{self.__currency}"]
                            column_order = df.columns.tolist()
                            column_order.insert(3, column_order.pop(column_order.index(f"{name}_CURRENCY-{self.__currency}")))
                            column_order.insert(4, column_order.pop(column_order.index(f"{name}_PX-LAST-CHF")))
                            df = df[column_order]


                for i in range(0, len(df.index)):
                    if df.iloc[i, df.columns.get_loc(f"{name}_start")] != "excluded":
                        if pd.notnull(df.iloc[i][f"{name}_PX-LAST-CHF"]):
                            last_value = df.iloc[i][f"{name}_PX-LAST-CHF"]
                        else:
                            df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST-CHF")] = last_value
                            df.iloc[i, df.columns.get_loc("imputed")] = f"imputed from {i-1}"


                # Done
                if storage_flag:
                    df.to_csv(os.path.join("data", "assets", name + ".csv"), index=False)

                self.__prices = df
                print("success", self.__full_name)

    def get_attributes(self):
        return self.__full_name, self.__currency, self.__prices

all_assets = [prepareAsset(x, "1997-08-15", False) for x in ['FB1_Comdty', 'TU1_Comdty', 'FV1_Comdty', 'TY1_Comdty',
                                                                                                'WN1_Comdty', 'CV1_Comdty', 'XQ1_Comdty', 'CN1_Comdty',
                                                                                                'LGB1_Comdty', 'WB1_Comdty', 'WX1_Comdty', 'G 1_Comdty',
                                                                                                'UGL1_Comdty', 'DU1_Comdty', 'OE1_Comdty', 'RX1_Comdty',
                                                                                                'UB1_Comdty', 'IK1_Comdty', 'OAT1_Comdty', 'XM1_Comdty',
                                                                                                'JB1_Comdty', 'KAA1_Comdty', 'TFT1_Comdty', 'SM1_Index',
                                                                                                'ES1_Index', 'PT1_Index', 'VG1_Index', 'Z 1_Index', 'GX1_Index',
                                                                                                'ST1_Index', 'CF1_Index', 'OI1_Index', 'QC1_Index', 'ATT1_Index',
                                                                                                'BE1_Index', 'EO1_Index', 'OT1_Index', 'XP1_Index', 'TP1_Index',
                                                                                                'NI1_Index', 'HI1_Index', 'IH1_Index', 'MES1_Index', 'BZ1_Index',
                                                                                                'CL1_Comdty', 'QS1_Comdty', 'XB1_Comdty', 'HO1_Comdty',
                                                                                                'NG1_Comdty', 'LMAHDS03 LME_Comdty', 'LMCADS03_Comdty',
                                                                                                'LMNIDS03_Comdty', 'GC1_Comdty', 'SI1_Comdty', 'LC1_Comdty',
                                                                                                'KC1_Comdty', 'C 1_Comdty', 'CT1_Comdty', 'S 1_Comdty', 'SB1_Comdty',
                                                                                                'W 1_Comdty']]


class prepareAssetNone:

    def __init__(self, name, first_date, storage_flag=False):

        assert isinstance(name, str), f"name '{name}' is not a string"
        for file in os.listdir(os.path.join("data","assets_raw_none")):
            if file.startswith(name):
                self.__full_name = os.path.join(os.path.join("data","assets_raw_none"), file)
                self.__currency  = self.__full_name.split("_")[-1].split(".")[0][:-4]
                # Read in all data to a DataFrame
                df_data = pd.read_csv(self.__full_name, usecols=[1,2])
                # Find bigger of the two dates
                second_date = df_data.iloc[0]["date"]
                chosen_date = second_date if pd.Timestamp(second_date) > pd.Timestamp(first_date) else first_date
                ###############################################################################
                # for now to prevent the bug DMark-EUR
                if name == "UB1_Comdty":
                    chosen_date = "1999-01-01"
                ###############################################################################
                # Construct an empty date DataFrame
                df_date = pd.DataFrame(index=pd.date_range(start=chosen_date, end="2023-12-31"))
                # Merge both DataFrames
                df_data["date"] = pd.to_datetime(df_data["date"])
                df = df_date.merge(df_data, how="left", left_index=True, right_on="date").reset_index(drop=True)
                # Add the weekday
                df.insert(1, "weekday", df["date"].dt.day_name())
                # Create unique columns names
                df = df.rename(columns={"PX_LAST": f"{name}_PX-LAST"})
                df["imputed"] = np.nan
                df[f"{name}_start"] = np.nan


                # Find the first tradeable Friday
                start_check = int(df[(df["weekday"] == "Friday") & (df[f"{name}_PX-LAST"].notnull())].first_valid_index())
                df.iloc[start_check, df.columns.get_loc(f"{name}_start")] = "start"

                while start_check != "end of backtest period reached":

                    # 2 weeks before end of dataset
                    if start_check + 14 < len(df.index):
                        start_set = False
                        #####################################################################
                        # If Friday in 2 weeks exists
                        if pd.notnull(df.iloc[start_check+14][f"{name}_PX-LAST"]):
                            # If Friday in 1 week exists
                            if pd.notnull(df.iloc[start_check+7][f"{name}_PX-LAST"]):
                                # We set this Friday to start
                                df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                            # If Friday in 1 week does not exist
                            else:
                                # We look backwards
                                for s in range(start_check+6, start_check-1, -1):
                                    # If there exists a value...
                                    if pd.notnull(df.iloc[s][f"{name}_PX-LAST"]):
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = df.iloc[s][f"{name}_PX-LAST"]
                                        df.iloc[start_check+7, df.columns.get_loc("imputed")] = f"imputed from {s}"
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                                        start_set = True
                                        break
                                if not start_set:
                                    df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                    df.iloc[start_check+7, df.columns.get_loc("imputed")] = np.nan
                                    df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "excluded"


                        # If Friday in 2 weeks does not exist
                        else:
                            start_set = False
                            # imputed down until FR 2 weeks ago
                            for s in range(start_check+13, start_check, -1):
                                if pd.notnull(df.iloc[s][f"{name}_PX-LAST"]):
                                    start_set = True
                                    break
                            if start_set:
                                start_set = False
                                if pd.notnull(df.iloc[start_check+7][f"{name}_PX-LAST"]):
                                    df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                                    start_set = True
                                else:
                                    for s in range(start_check+6, start_check-1, -1):
                                        if pd.notnull(df.iloc[s][f"{name}_PX-LAST"]):
                                            df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = df.iloc[s][f"{name}_PX-LAST"]
                                            df.iloc[start_check+7, df.columns.get_loc("imputed")] = f"imputed from {s}"
                                            df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                                            start_set = True
                                            break
                                    if not start_set:
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                        df.iloc[start_check+7, df.columns.get_loc("imputed")] = np.nan
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "excluded"

                            else:
                                df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                df.iloc[start_check+7, df.columns.get_loc("imputed")] = np.nan
                                df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "excluded"

                        start_check += 7

                    # 1 week before end of dataset
                    elif start_check + 7 < len(df.index):
                        if pd.notnull(df.iloc[start_check+7][f"{name}_PX-LAST"]):
                            df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                        else:
                            for s in range(start_check+6, start_check-1, -1):
                                if pd.notnull(df.iloc[s][f"{name}_PX-LAST"]):
                                    if np.isnan(df.iloc[s]["imputed"]):
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = df.iloc[s][f"{name}_PX-LAST"]
                                        df.iloc[start_check+7, df.columns.get_loc("imputed")] = f"imputed from {s}"
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "start"
                                        break
                                    else:
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                        df.iloc[start_check+7, df.columns.get_loc("imputed")] = np.nan
                                        df.iloc[start_check+7, df.columns.get_loc(f"{name}_start")] = "excluded"
                                        break

                        start_check = "end of backtest period reached"

                    # end of dataset reached
                    else:
                        start_check = "end of backtest period reached"


                for i in range(len(df)-1, -1, -1):
                    if df.loc[i, "weekday"] == "Friday":
                        break

                if name == "KAA1_Comdty":
                    sell_point = pd.to_datetime("2008-09-12")
                    data_point = pd.to_datetime("2010-10-25")
                while i >= 0:
                    if df.iloc[i][f"{name}_start"] == "excluded":
                        i -= 7
                        if i >= 0:
                            if df.iloc[i][f"{name}_start"] == "start":
                                if isinstance(df.iloc[i]["imputed"], float):
                                    df.iloc[i, df.columns.get_loc(f"{name}_start")] = "sell"
                                else:
                                    df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                    df.iloc[i, df.columns.get_loc("imputed")] = np.nan
                                    df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"
                    else:
                        if i-7 >= 0:
                            if df.iloc[i][f"{name}_start"] == "start" and df.iloc[i-7][f"{name}_start"] == "excluded":
                                # if no data is found, the start is equal to the first data point
                                for _ in range(i-6, i):
                                    if pd.notnull(df.iloc[_][f"{name}_PX-LAST"]):
                                        df.iloc[_, df.columns.get_loc(f"{name}_start")] = "data"
                                        break
                        i -= 7
                    if name == "KAA1_Comdty":
                        if df.iloc[i]["date"] == sell_point:
                            df.iloc[i, df.columns.get_loc(f"{name}_start")] = "sell"
                        elif sell_point < df.iloc[i]["date"] < data_point:
                            df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                            df.iloc[i, df.columns.get_loc("imputed")] = np.nan
                            df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"

                first_start = False
                sell_found = False
                for i in range(0, len(df.index)):
                    if not first_start:
                        if isinstance(df.iloc[i, df.columns.get_loc(f"{name}_start")], float):
                            df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                            df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"
                        else:
                            first_start = True
                    else:
                        if df.iloc[i, df.columns.get_loc(f"{name}_start")] == "sell":
                            sell_found = True
                            continue
                        if sell_found:
                            if df.iloc[i, df.columns.get_loc(f"{name}_start")] in ("data", "start"):
                                sell_found = False
                                continue
                            if isinstance(df.iloc[i]["imputed"], float):
                                df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"
                            else:
                                df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST")] = np.nan
                                df.iloc[i, df.columns.get_loc("imputed")] = np.nan
                                df.iloc[i, df.columns.get_loc(f"{name}_start")] = "excluded"


                # Convert currencies
                if self.__currency == "CHF":
                    df = df.rename(columns={f"{name}_PX-LAST": f"{name}_PX-LAST-CHF"})
                else:
                    for file in os.listdir(os.path.join("data","support")):
                        if file.startswith(self.__currency):
                            df_currency = pd.read_csv(os.path.join("data","support", file), usecols=[1,2])
                            df_currency["date"] = pd.to_datetime(df_currency["date"])
                            df[f"{name}_CURRENCY-{self.__currency}"] = df["date"].map(df_currency.set_index("date")["PX_LAST"])
                            assert all((df.loc[df[f"{name}_PX-LAST"].notna(), f"{name}_CURRENCY-{self.__currency}"].notna())), \
                                f"Not all non-NaN {name}_PX-LAST entries have a corresponding non-NaN {name}_CURRENCY-{self.__currency} entry."
                            if self.__currency in ("JPY", "KRW"):
                                df[f"{name}_PX-LAST-CHF"] = df[f"{name}_PX-LAST"] * df[f"{name}_CURRENCY-{self.__currency}"] / 100
                            else:
                                df[f"{name}_PX-LAST-CHF"] = df[f"{name}_PX-LAST"] * df[f"{name}_CURRENCY-{self.__currency}"]
                            column_order = df.columns.tolist()
                            column_order.insert(3, column_order.pop(column_order.index(f"{name}_CURRENCY-{self.__currency}")))
                            column_order.insert(4, column_order.pop(column_order.index(f"{name}_PX-LAST-CHF")))
                            df = df[column_order]


                for i in range(0, len(df.index)):
                    if df.iloc[i, df.columns.get_loc(f"{name}_start")] != "excluded":
                        if pd.notnull(df.iloc[i][f"{name}_PX-LAST-CHF"]):
                            last_value = df.iloc[i][f"{name}_PX-LAST-CHF"]
                        else:
                            df.iloc[i, df.columns.get_loc(f"{name}_PX-LAST-CHF")] = last_value
                            df.iloc[i, df.columns.get_loc("imputed")] = f"imputed from {i-1}"


                # Done
                if storage_flag:
                    df.to_csv(os.path.join("data", "assets_none", name + ".csv"), index=False)

                self.__prices = df
                print("success", self.__full_name)

    def get_attributes(self):
        return self.__full_name, self.__currency, self.__prices

all_assets_none = [prepareAssetNone(x, "1997-08-15", False) for x in ['FB1_Comdty', 'TU1_Comdty', 'FV1_Comdty', 'TY1_Comdty',
                                                                                                'WN1_Comdty', 'CV1_Comdty', 'XQ1_Comdty', 'CN1_Comdty',
                                                                                                'LGB1_Comdty', 'WB1_Comdty', 'WX1_Comdty', 'G 1_Comdty',
                                                                                                'UGL1_Comdty', 'DU1_Comdty', 'OE1_Comdty', 'RX1_Comdty',
                                                                                                'UB1_Comdty', 'IK1_Comdty', 'OAT1_Comdty', 'XM1_Comdty',
                                                                                                'JB1_Comdty', 'KAA1_Comdty', 'TFT1_Comdty', 'SM1_Index',
                                                                                                'ES1_Index', 'PT1_Index', 'VG1_Index', 'Z 1_Index', 'GX1_Index',
                                                                                                'ST1_Index', 'CF1_Index', 'OI1_Index', 'QC1_Index', 'ATT1_Index',
                                                                                                'BE1_Index', 'EO1_Index', 'OT1_Index', 'XP1_Index', 'TP1_Index',
                                                                                                'NI1_Index', 'HI1_Index', 'IH1_Index', 'MES1_Index', 'BZ1_Index',
                                                                                                'CL1_Comdty', 'QS1_Comdty', 'XB1_Comdty', 'HO1_Comdty',
                                                                                                'NG1_Comdty', 'LMAHDS03 LME_Comdty', 'LMCADS03_Comdty',
                                                                                                'LMNIDS03_Comdty', 'GC1_Comdty', 'SI1_Comdty', 'LC1_Comdty',
                                                                                                'KC1_Comdty', 'C 1_Comdty', 'CT1_Comdty', 'S 1_Comdty', 'SB1_Comdty',
                                                                                                'W 1_Comdty']]
