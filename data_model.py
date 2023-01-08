from typing import List

import pandas as pd

day_column_name = 'day'
time_column_name = 'hour'
power_column_name = 'ac_power'
energy_column_name = 'ac_energy_today'


# Forward declaration
class Model:
    pass


class Model:
    def __init__(self):
        self.df: pd.DataFrame = pd.DataFrame()
        self.model_status: List[str] = []
        self.days: List[str] = []

    def create_model(self, data_file: str) -> Model:
        self.model_status.clear()
        try:
            self.df = pd.read_csv(
                data_file,
                sep=',',
                header=0,
                usecols=['date', 'ac_power', 'ac_energy_today'],
                nrows=10000
            )
            self.df[day_column_name] = pd.to_datetime(self.df['date']).dt.date
            self.df[time_column_name] = pd.to_datetime(self.df['date']).dt.strftime("%H:%M:%S")
        except FileNotFoundError as exception:
            self.model_status.append(f'{str(exception)}')

        return self
