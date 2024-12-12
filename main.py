import streamlit as st
from pages.login import show_login_page
from pages.registration import show_registration_page
from pages.admin_page import show_admin_page
from pages.user_page import show_user_page

def main():
    st.set_page_config(page_title="HARMONIQ", layout="centered")

    if "page" not in st.session_state:
        st.session_state.page = "Вход"

    if st.session_state.page == "Вход":
        show_login_page()
    elif st.session_state.page == "Регистрация":
        show_registration_page()
    elif st.session_state.page == "admin_dashboard":
        show_admin_page()
    elif st.session_state.page == "user_dashboard":
        show_user_page()

if __name__ == "__main__":
    main()