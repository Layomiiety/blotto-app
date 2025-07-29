import streamlit as st
from practice_page import practice_mode
from tournament_page import tournament_mode

st.set_page_config(
    page_title="Blotto Strategy Game",
    page_icon="🏰",
    layout="wide"
)

st.sidebar.title("🎮 Blotto Game Menu")
mode = st.sidebar.radio("Select Mode", ["Practice Mode", "Tournament Mode"])

if mode == "Practice Mode":
    practice_mode()
elif mode == "Tournament Mode":
    tournament_mode()
