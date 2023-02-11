import streamlit as st

from view.view_common import footer


def home():
    # emojis: https://www.webfx.com/tools/emoji-cheat-sheet
    st.set_page_config(page_title='PV Dashboard',
                       page_icon=':sunny:',
                       layout='wide')

    st.title(':sunny: PV Dashboard')
    st.markdown('##')

    st.header("Goal")
    st.markdown('#')
    st.markdown("""
    [MIT License]: https://github.com/Ambayonyx/pv_dashboard/blob/main/LICENSE "LICENSE"
    The goal of PV Dashboard is to provide insights in the performance of you PV installation.

    The current version supports data exported from Autarco systems in CSV format.

    The code is opensource ([MIT License]) and can be found at GitHub, see the about section below.
    """)

    st.subheader("About")
    st.markdown("""
    [code archive]: https://github.com/Ambayonyx/pv_dashboard 'GITHUB Repository'
    [project page]: https://github.com/users/Ambayonyx/projects/3 'Project page'
                
    Sources:
     * [Code archive]
     * [Project page]  (private)
    
    Version: 0.0
    """)

    footer()


if __name__ == '__main__':
    home()
