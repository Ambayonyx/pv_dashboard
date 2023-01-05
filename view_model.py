import datetime
from typing import List, Tuple

import numpy as np
import pandas as pd

import data_model
from data_model import Model, day_column_name


class ViewModel:
    def __init__(self, model: Model):
        self._model_ = model
        self.days = self._model_.df[day_column_name].unique()

    def dataframe(self) -> pd.DataFrame:
        return self._model_.df

    def overlay(self) -> Tuple[pd.DataFrame, List[str]]:

        # create the day with intervals of 5 minutes
        rng = pd.date_range(pd.Timestamp(year=2022, month=1, day=1), periods=24 * 12, freq='5min')
        overlay = pd.DataFrame()
        overlay[data_model.time_column_name] = rng.astype(str)
        overlay[data_model.time_column_name] = pd.to_datetime(overlay[data_model.time_column_name]).dt.strftime(
            '%H:%M:%S')
        overlay.set_index(data_model.time_column_name, inplace=True)
        day_entries = {}
        for _, entry in self.dataframe().iterrows():
            day = entry[data_model.day_column_name].isoformat()
            if day not in day_entries:
                day_entries[day] = {}
            moment = datetime.time.fromisoformat(entry[data_model.time_column_name])
            moment_interval = datetime.time(hour=moment.hour, minute=int(moment.minute / 5) * 5, second=0)
            power = entry[data_model.power_column_name]
            day_entries[day][moment_interval.strftime('%H:%M:%S')] = power
        df_day_entries = pd.DataFrame(data=day_entries)
        overlay = overlay.join(df_day_entries)

        # calculate average
        nr_dates = len(overlay.columns)
        generating = overlay.apply(np.sign).replace(True, 1).replace(False, 0).sum(axis=1)
        overlay_sum = overlay.sum(axis=1)
        overlay['Average_simple'] = overlay_sum / nr_dates
        overlay['Average_generating'] = overlay_sum / generating
        overlay['Generating*4'] = generating * 50

        overlay.reset_index(inplace=True)
        overlay = overlay.rename(columns={'index': data_model.time_column_name})
        overlay.fillna(0, inplace=True)

        dates = overlay.columns.tolist()
        dates.remove(data_model.time_column_name)
        dates.insert(0, 'All')

        return overlay, dates

    def daily(self) -> pd.DataFrame:
        df = self._model_.df
        days = sorted(df[data_model.day_column_name].unique())

        start_list = []
        end_list = []
        power_max_list = []
        energy_list = []
        energy_calculated_list = []
        energy_error_perc_list = []
        for day in days:
            day_entries = df[(df[data_model.day_column_name] == day)]

            hours_sorted = sorted(day_entries[data_model.time_column_name])
            start = hours_sorted[0]
            start_list.append(start)
            end = hours_sorted[-1]
            end_list.append(end)

            power_sorted = sorted(day_entries[data_model.power_column_name])
            power_max = power_sorted[-1]
            power_max_list.append(power_max)

            energy_sorted = sorted(day_entries[data_model.energy_column_name])
            energy = energy_sorted[-1]
            energy_list.append(energy)

            energy_calculated = sum(power_sorted) / 12 / 1000
            energy_calculated_list.append(energy_calculated)

            energy_error_perc = (energy_calculated - energy) / energy * 100
            energy_error_perc_list.append(energy_error_perc)

        daily_data = {
            'date': days,
            'start': start_list,
            'end': end_list,
            'power max [W]': power_max_list,
            'energy [kWh]': energy_list,
            'energy (calculated) [kWh]': energy_calculated_list,
            'energy_error [%]': energy_error_perc_list
        }

        return pd.DataFrame(data=daily_data)

    def select_days(self, days: List[str]) -> pd.DataFrame:
        df_selection = self._model_.df.query(
            f"{data_model.day_column_name} == @days"
        )
        return df_selection
