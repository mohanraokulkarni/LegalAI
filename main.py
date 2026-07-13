import streamlit as st
from streamlit_option_menu import option_menu
import os
# from dotenv import load_dotenv
# load_dotenv()

import appchat , app2 , account1
st.set_page_config(
        page_title="Nyaya Mitra",
        page_icon="⚖️",  # You can replace this with a local image file or URL
        layout="centered"
)

st.markdown(
    """
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src=f"https://www.googletagmanager.com/gtag/js?id={os.getenv('analytics_tag')}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', os.getenv('analytics_tag'));
        </script>
    """, unsafe_allow_html=True)
print(os.getenv('analytics_tag'))


class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):  # Add 'self' parameter to the method
        with st.sidebar:
            app = option_menu(
                menu_title='⚖️ Nyaya Mitra ',
                options =['Legal Chatbot', 'Contract Analysis', 'Account'],
                icons = ['chat-left-dots-fill', 'file-earmark-text-fill', 'person-circle'],
            # 'trophy-fill', 'chat-fill', 'info-circle-fill'
                menu_icon='scales',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": '#939597'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "15px", "text-align": "left", "margin": "0px",
                                 "--hover-color": "#000080"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )
        if app == "Contract Analysis":
            app2.app2()
        if app == "Legal Chatbot":
            appchat.app()
        if app == "Account":
            account1.app()



# Create an instance of the MultiApp class and call 'run' on it
multi_app = MultiApp()
multi_app.run()
