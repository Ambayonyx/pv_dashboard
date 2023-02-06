import plotly.express as px
import streamlit as st

import control
import data_model
from view.view_common import footer
from view_model import ViewModel


def analysis():
    # emojis: https://www.webfx.com/tools/emoji-cheat-sheet
    st.set_page_config(page_title='PV Analysis',
                       page_icon=':chart_with_upwards_trend:',
                       layout='wide')

    # ----------------------
    # setup the sidebar
    # ----------------------
    st.sidebar.header('Navigation')
    uploaded_file = st.sidebar.file_uploader('Upload the file here', help="Must be an exported Autarco CSV file!")

    if uploaded_file:
        ctrl = control.Control()
        view = ctrl.load_file(data_file=uploaded_file)
    else:
        st.title(':chart_with_upwards_trend: PV Analysis')
        st.header(':arrow_left: Load CSV file first')
        footer()
        return

    if not view.model_is_ok():
        st.markdown('Failed to load the model:')
        st.markdown(f'{view.model_status()}')
        footer()
        return

    if not view.model_is_ok():
        st.markdown('Failed to load the model:')
        st.markdown(f'{view.model_status()}')
        footer()
        return

    options = st.sidebar.radio('Pages',
                               options=[
                                   'Daily',
                                   'Monthly',
                                   'Overlay',
                                   'Raw data',
                               ])

    st.title(':chart_with_upwards_trend: PV Analysis')
    st.markdown('##')

    match options:
        case 'Raw data':
            raw_data(view)
        case 'Daily':
            daily(view)
        case 'Monthly':
            monthly(view)
        case 'Overlay':
            overlay_plot(view)

    footer()


def overlay_plot(model: ViewModel):
    st.header('Overlay')
    st.markdown('##')

    overlay, dates = model.overlay()
    y_axis_val = st.selectbox('Select Y-axis Value', options=dates)

    if y_axis_val == 'All':
        plot = px.line(overlay, x=overlay[data_model.time_column_name], y=dates[1:])
    else:
        plot = px.line(overlay, x=overlay[data_model.time_column_name], y=y_axis_val)
    plot.update_layout(width=800)
    st.plotly_chart(plot)

    st.dataframe(overlay)


def daily(model: ViewModel):
    df_daily = model.daily()
    st.header('Daily')
    st.markdown('##')

    plot_duration = px.bar(df_daily,
                           x=df_daily['date'],
                           y=['generation period [min]'],
                           title="Production time")
    plot_duration.update_layout(width=800)
    st.plotly_chart(plot_duration)

    plot_power = px.bar(df_daily,
                        x=df_daily['date'],
                        y=['power max [W]', 'power avg [W]'],
                        title="Power production",
                        barmode='overlay')
    plot_power.update_layout(width=800)
    st.plotly_chart(plot_power)

    plot_energy = px.bar(df_daily,
                         x=df_daily['date'],
                         y=['energy [kWh]'],
                         title="Energy yield")
    plot_energy.update_layout(width=800)
    st.plotly_chart(plot_energy)

    df_daily = df_daily[[
        'date',
        'start',
        'end',
        'generation period [min]',
        'power max [W]',
        'power avg [W]',
        'energy [kWh]',
        'energy (calculated) [kWh]',
        'energy_error [%]'
    ]]
    st.dataframe(df_daily)


def monthly(model: ViewModel):
    df_monthly = model.daily()
    df_monthly['month'] = df_monthly['date'].apply(lambda d: d.isoformat()[:7])
    st.header('Monthly')
    st.markdown('##')

    plot_duration = px.box(df_monthly,
                           x=df_monthly['month'],
                           y=['generation period [min]'],
                           title="Production time")
    plot_duration.update_layout(width=800)
    st.plotly_chart(plot_duration)

    plot_power_max = px.box(df_monthly,
                            x=df_monthly['month'],
                            y=['power max [W]'],
                            title="Power production max")
    plot_power_max.update_layout(width=800)
    st.plotly_chart(plot_power_max)

    plot_power_average = px.box(df_monthly,
                                x=df_monthly['month'],
                                y=['power avg [W]'],
                                title="Power production average")
    plot_power_average.update_layout(width=800)
    st.plotly_chart(plot_power_average)

    plot_energy = px.box(df_monthly,
                         x=df_monthly['month'],
                         y=['energy [kWh]'],
                         title="Energy yield")
    plot_energy.update_layout(width=800)
    st.plotly_chart(plot_energy)

    df_monthly = df_monthly[[
        'date',
        'month',
        'start',
        'end',
        'generation period [min]',
        'power max [W]',
        'power avg [W]',
        'energy [kWh]',
        'energy (calculated) [kWh]',
        'energy_error [%]'
    ]]
    st.dataframe(df_monthly)


def raw_data(model: ViewModel):
    st.header('All data')
    st.markdown('##')
    st.dataframe(model.dataframe())


analysis()
