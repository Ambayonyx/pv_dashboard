from typing import List

import plotly.express as px
import streamlit as st

import control
import data_model
from view_model import ViewModel


def main():
    # emojis: https://www.webfx.com/tools/emoji-cheat-sheet
    st.set_page_config(page_title='PV Dashboard',
                       page_icon=':sunny:',
                       layout='wide')

    # ----------------------
    # setup the sidebar
    # ----------------------
    st.sidebar.header('Navigation')
    uploaded_file = st.sidebar.file_uploader('Upload the file here', help="Must an exported Autarco CSV file!")

    ctrl = control.Control()
    if uploaded_file:
        view = ctrl.load_file(data_file=uploaded_file)
    else:
        view = ctrl.get_view()

    if not view.model_is_ok():
        st.markdown('Failed to load the model:')
        st.markdown(f'{view.model_status()}')
        return

    st.sidebar.header("Please filter here:")
    days = st.sidebar.multiselect(
        "Select the date:",
        options=view.days,
        default=view.days
    )

    options = st.sidebar.radio('Pages',
                               options=[
                                   'Daily',
                                   'Overlay',
                                   'Raw data',
                               ])

    st.title(':sunny: PV Dashboard')
    st.markdown('##')

    match options:
        case  'Raw data':
            raw_data(view, days)
        case 'Daily':
            daily(view)
        case 'Overlay':
            overlay_plot(view)

    st.markdown("""*Note: This page is not a product of Autarco, nor is it affiliated to Autarco. 
    Autarco holds no responsibility for its content.* 
    """)


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
    st.dataframe(df_daily)


def raw_data(model: ViewModel, days: List[str]):
    selection = model.select_days(days)
    st.header('All data')
    st.markdown('##')
    st.dataframe(selection)


if __name__ == '__main__':
    main()
