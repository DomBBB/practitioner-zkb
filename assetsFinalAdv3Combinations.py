import pandas as pd
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
import math

for file in os.listdir(os.path.join("results_FINAL_all", "trades")):
    if "momentum" in file:
        continue
    elif "value_weekly_vola_none" not in file: ######
        continue
    # get VALUE
    else:
        for file2 in os.listdir(os.path.join("results_FINAL_all", "trades")):
            if "value" in file2:
                continue
            elif "momentum_contra+0-1-0+0-0-1_weekly_vola_none" not in file2: ##########
                continue
            # get CONTRA
            else:
                for file3 in os.listdir(os.path.join("results_FINAL_all", "trades")):
                    if "value" in file3:
                        continue
                    elif "momentum+0-12-0+0-1-0_weekly_vola_none" not in file3: ##########
                        continue
                    # get MOMENTUM
                    else:
                        if "equal" in file:
                            data_weighting = "equal"
                        elif "vola" in file:
                            data_weighting = "vola"
                        else:
                            raise "decoding not possible"
                        ##################
                        file_trades_3 = os.path.join("results_FINAL_all", "trades", file3) # here I need the signal per day
                        trades_df_3 = pd.read_csv(file_trades_3, index_col=0)
                        ##################
                        file_trades_2 = os.path.join("results_FINAL_all", "trades", file2) # here I need the signal per day
                        trades_df_2 = pd.read_csv(file_trades_2, index_col=0)
                        ##################
                        file_trades = os.path.join("results_FINAL_all", "trades", file) # here I have prices, returns and signals per day
                        trades_df = pd.read_csv(file_trades, index_col=0)
                        for column in trades_df.columns:
                            if "_buy" in column or "_sell" in column or "weighted_return" in column:
                                trades_df[column] = np.nan
                        position = trades_df.columns.get_loc("considered_assets")
                        trades_df.insert(position+1, "sub_considered_assets_1", trades_df["considered_assets"])
                        trades_df.insert(position+2, "sub_considered_assets_2", trades_df_2["considered_assets"])
                        trades_df.insert(position+3, "sub_considered_assets_3", trades_df_3["considered_assets"])
                        trades_df["considered_assets"] = None
                        file_signals = os.path.join("results_FINAL_all", file[:-10] + "signals.csv") # here I have f"{name}_vola"
                        signals_df = pd.read_csv(file_signals, index_col=0)
                        ##################
                        for index, row in trades_df.iterrows():
                            if row["weekday"] != "Friday":
                                continue
                            if index == "2023-12-23":
                                break
                            sub_1_str = eval(row["sub_considered_assets_1"])
                            sub_2_str = eval(row["sub_considered_assets_2"])
                            sub_3_str = eval(row["sub_considered_assets_3"])
                            common_keys = set(sub_1_str.keys()) & set(sub_2_str.keys()) & set(sub_3_str.keys())
                            sub_1_dict = {key: sub_1_str[key] for key in common_keys}
                            sub_2_dict = {key: sub_2_str[key] for key in common_keys}
                            sub_3_dict = {key: sub_3_str[key] for key in common_keys}
                            sub_1 = dict(sorted(sub_1_dict.items(), key=lambda item: item[1], reverse=True))
                            sub_2 = dict(sorted(sub_2_dict.items(), key=lambda item: item[1], reverse=True))
                            sub_3 = dict(sorted(sub_3_dict.items(), key=lambda item: item[1], reverse=True))
                            trades_df.at[index, "sub_considered_assets_1"] = sub_1
                            trades_df.at[index, "sub_considered_assets_2"] = sub_2
                            trades_df.at[index, "sub_considered_assets_3"] = sub_3
                            summed_ranks = {}
                            for rank, key in enumerate(sub_1.keys()):
                                for rank2, key2 in enumerate(sub_2.keys()):
                                    for rank3, key3 in enumerate(sub_3.keys()):
                                        if key == key2 and key == key3:
                                            summed_ranks[key] = (rank+1)/3 + (rank2+1)/3 +  (rank3+1)/3
                            if len(summed_ranks) < 20:
                                if index == "2023-12-29":
                                    continue
                                else:
                                    print(index)
                                    raise SumError
                            summed_ranks = dict(sorted(summed_ranks.items(), key=lambda item: item[1], reverse=False))
                            trades_df.at[index, "considered_assets"] = summed_ranks

                            if len(summed_ranks) < 30:
                                nr_assets = math.floor(len(summed_ranks)/2)
                            else:
                                nr_assets = 15
                            top_x_keys = list(summed_ranks.keys())[:nr_assets]
                            lowest_x_keys = list(summed_ranks.keys())[-nr_assets:]
                            total_vola_long = 0
                            total_vola_short = 0
                            start_columns = [col for col in trades_df if col.endswith("_start")]
                            for col in start_columns:
                                name = "_".join(col.split("_")[:-1])
                                if name in top_x_keys:
                                    total_vola_long += (1 / signals_df.loc[index, f"{name}_vola"])
                                    trades_df.loc[index, f"{name}_buy"] = 100/nr_assets
                                elif name in lowest_x_keys:
                                    total_vola_short += (1 / signals_df.loc[index, f"{name}_vola"])
                                    trades_df.loc[index, f"{name}_buy"] = -100/nr_assets
                                else:
                                    trades_df.loc[index, f"{name}_buy"] = np.nan
                            for col in start_columns:
                                name = "_".join(col.split("_")[:-1])
                                if pd.notnull(trades_df.loc[index, f"{name}_buy"]):
                                    if data_weighting == "vola":
                                        inverse_vola = 1 / signals_df.loc[index, f"{name}_vola"]
                                        if trades_df.loc[index, f"{name}_buy"] > 0:
                                            trades_df.loc[index, f"{name}_buy"] = (inverse_vola / total_vola_long) * 100
                                        elif trades_df.loc[index, f"{name}_buy"] < 0:
                                            trades_df.loc[index, f"{name}_buy"] = -(inverse_vola / total_vola_short) * 100
                                        else: # failsafe
                                            raise VolaError

                                    next_index = (pd.to_datetime(index) + pd.Timedelta(days=7)).strftime("%Y-%m-%d")
                                    trades_df.loc[next_index, f"{name}_sell"] = trades_df.loc[index, f"{name}_buy"]
                                    current_weighted_return = trades_df.loc[next_index, "weighted_return"]
                                    if np.isnan(trades_df.loc[next_index, "weighted_return"]):
                                        current_weighted_return = 0
                                    new_weighted_return =  trades_df.loc[next_index, f"{name}_sell"] / 100 * trades_df.loc[next_index, f"{name}_weeklyReturn"]
                                    trades_df.loc[next_index, "weighted_return"] = current_weighted_return + new_weighted_return

                                    current_weighted_return_l = trades_df.loc[next_index, "weighted_return_l"]
                                    if np.isnan(trades_df.loc[next_index, "weighted_return_l"]):
                                        current_weighted_return_l = 0
                                    if trades_df.loc[next_index, f"{name}_sell"] > 0:
                                        new_weighted_return_l =  trades_df.loc[next_index, f"{name}_sell"] / 100 * trades_df.loc[next_index, f"{name}_weeklyReturn"]
                                        trades_df.loc[next_index, "weighted_return_l"] = current_weighted_return_l + new_weighted_return_l

                                    current_weighted_return_s = trades_df.loc[next_index, "weighted_return_s"]
                                    if np.isnan(trades_df.loc[next_index, "weighted_return_s"]):
                                        current_weighted_return_s = 0
                                    if trades_df.loc[next_index, f"{name}_sell"] < 0:
                                        new_weighted_return_s =  trades_df.loc[next_index, f"{name}_sell"] / 100 * trades_df.loc[next_index, f"{name}_weeklyReturn"]
                                        trades_df.loc[next_index, "weighted_return_s"] = current_weighted_return_s + new_weighted_return_s

                        # SAVE
                        trades_df.to_csv(os.path.join("results_FINAL_all", "adv_baseline3", file[4:-11] + "__" + file2[4:-11] + "__" + file3[4:-11] + ".csv"))
                        with open(os.path.join("results_FINAL_all", "adv_baseline3", "summary.txt"), "a") as f:  # 'a' mode appends to the file without overwriting
                            f.write(f"{file}_____{file2}_____{file3}::::::::::::{trades_df['weighted_return'].mean()}, {trades_df['weighted_return_l'].mean()}, {trades_df['weighted_return_s'].mean()}\n")
                        print("DONE")
