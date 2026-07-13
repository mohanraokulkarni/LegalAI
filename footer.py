import streamlit as st
from htbuilder import HtmlElement, div, p, styles, img
from htbuilder.units import percent, px
import PyPDF2




def layout(*args):
    style = """
    <style>
        # MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp {bottom: 40px;}
    </style>
    """
    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1,
    )
    body = p()
    foot = div(style=style_div)(body)

    st.markdown(style, unsafe_allow_html=True)
    for arg in args:
        if isinstance(arg, str):
            body(arg)
        elif isinstance(arg, HtmlElement):
            body(arg)
    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = ["Made by Zealot"]
    layout(*myargs)



