import streamlit as st
import gettext
import os

def load_translation(language):
    localedir = os.path.join(os.path.dirname(__file__), 'locales')
    try:
        lang = gettext.translation('messages', localedir=localedir, languages=[language])
        lang.install()
        return lang.gettext
    except FileNotFoundError:
        gettext.install('messages')
        return gettext.gettext

language = st.sidebar.selectbox("Choose Language", ["en", "hi", "mr", "pa", "ta"])
_ = load_translation(language)

st.title(_("👑 Admin Setup"))
st.subheader(_("This is a one-time setup to create the system administrator"))
st.button(_("Vote"))
# def load_translation(language):
    # locale_path = os.path.join(os.path.dirname(__file__), "locales")
    # try:
    #     lang = gettext.translation('messages', localedir=locale_path, languages=[language])
    #     lang.install()
    #     _ = lang.gettext
    # except FileNotFoundError:
    #     _ = gettext.gettext
    # return _

