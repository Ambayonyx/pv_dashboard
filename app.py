import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

day_column_name = 'day'
time_column_name = 'hour'
power_column_name = 'ac_power'
energy_column_name = 'ac_energy_today'


def main(default_filename: str):
    # emojis: https://www.webfx.com/tools/emoji-cheat-sheet
    st.set_page_config(page_title='PV Dashboard',
                       page_icon=':sunny:',
                       layout='wide')

    # ----------------------
    # setup the sidebar
    # ----------------------
    st.sidebar.header('Navigation')
    uploaded_file = st.sidebar.file_uploader('Upload the file here', help="Must an exported Autarco CSV file!")

    if uploaded_file:
        file_to_show = uploaded_file
    else:
        file_to_show = default_filename

    df = pd.read_csv(
        file_to_show,
        sep=',',
        header=0,
        usecols=['date', 'ac_power', 'ac_energy_today'],
        nrows=10000
    )
    df[day_column_name] = pd.to_datetime(df['date']).dt.date
    df[time_column_name] = pd.to_datetime(df['date']).dt.strftime("%H:%M:%S")

    st.sidebar.header("Please filter here:")
    days = st.sidebar.multiselect(
        "Select the date:",
        options=df[day_column_name].unique(),
        default=df[day_column_name].unique()
    )

    options = st.sidebar.radio('Pages',
                               options=[
                                   'All data',
                                   'Daily',
                                   'overlay',
                               ])

    st.title(':sunny: PV Dashboard')
    st.markdown('##')

    if options == 'All data':
        all_data(df, days)
    elif options == 'Daily':
        daily(df)
    elif options == 'overlay':
        overlay_plot(df)

    st.markdown("""*Note: This page is not a product of Autarco, nor is it affiliated to Autarco. 
    Autarco holds no responsibility for its content.* 
    """)


def overlay_plot(df):
    st.header('Overlay')
    st.markdown('##')

    # create the day with intervals of 5 minutes
    rng = pd.date_range(pd.Timestamp(year=2022, month=1, day=1), periods=24 * 12, freq='5min')
    overlay = pd.DataFrame()
    overlay[time_column_name] = rng.astype(str)
    overlay[time_column_name] = pd.to_datetime(overlay[time_column_name]).dt.strftime('%H:%M:%S')
    overlay.set_index(time_column_name, inplace=True)
    day_entries = {}
    for _, entry in df.iterrows():
        day = entry[day_column_name].isoformat()
        if day not in day_entries:
            day_entries[day] = {}
        moment = datetime.time.fromisoformat(entry[time_column_name])
        moment_interval = datetime.time(hour=moment.hour, minute=int(moment.minute / 5) * 5, second=0)
        power = entry[power_column_name]
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
    overlay = overlay.rename(columns={'index': time_column_name})
    overlay.fillna(0, inplace=True)

    dates = overlay.columns.tolist()
    dates.remove(time_column_name)
    dates.insert(0, 'All')
    y_axis_val = st.selectbox('Select Y-axis Value', options=dates)

    if y_axis_val == 'All':
        plot = px.line(overlay, x=overlay[time_column_name], y=dates[1:])
    else:
        plot = px.line(overlay, x=overlay[time_column_name], y=y_axis_val)
    plot.update_layout(width=800)
    st.plotly_chart(plot)

    st.dataframe(overlay)


def daily(df):
    days = sorted(df[day_column_name].unique())

    start_list = []
    end_list = []
    power_max_list = []
    energy_list = []
    energy_calculated_list = []
    energy_error_perc_list = []
    for day in days:
        day_entries = df[(df[day_column_name] == day)]

        hours_sorted = sorted(day_entries[time_column_name])
        start = hours_sorted[0]
        start_list.append(start)
        end = hours_sorted[-1]
        end_list.append(end)

        power_sorted = sorted(day_entries[power_column_name])
        power_max = power_sorted[-1]
        power_max_list.append(power_max)

        energy_sorted = sorted(day_entries[energy_column_name])
        energy = energy_sorted[-1]
        energy_list.append(energy)

        energy_calculated = sum(power_sorted) / 12 / 1000
        energy_calculated_list.append(energy_calculated)

        energy_error_perc = (energy_calculated - energy)/energy * 100
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

    df_daily = pd.DataFrame(data=daily_data)
    st.header('Daily')
    st.markdown('##')
    st.dataframe(df_daily)


def all_data(df, days):
    df_selection = df.query(
        f"{day_column_name} == @days"
    )
    st.header('All data')
    st.markdown('##')
    st.dataframe(df_selection)


if __name__ == '__main__':
    filename = 'data/input/full-messages.cpl25biy.20221231-20230103.csv'
    main(filename)
