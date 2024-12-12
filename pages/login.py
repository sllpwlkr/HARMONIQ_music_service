import streamlit as st

from repositories.passwords import authenticate_user

def show_login_page():
    st.title("Вход")
    no_sidebar_style = """
                <style>
                    div[data-testid="stSidebarNav"] {display: none;}
                </style>
            """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)
    login = st.text_input("Введите логин")
    password = st.text_input("Введите пароль", type="password")

    if st.button("Войти"):
        if not login.strip() or not password.strip():
            st.error("Логин и пароль не могут быть пустыми. Попробуйте снова.")
            return

        result = authenticate_user(login, password)

        if result == "admin_dashboard":
            st.success("Вы успешно зашли. Нажмите на кнопку еще раз.")
            st.session_state["current_user"] = login
            st.session_state.page = "admin_dashboard"
        elif result == "user_dashboard":
            st.session_state["current_user"] = login
            st.success("Вы успешно зашли. Нажмите на кнопку еще раз.")
            st.session_state.page = "user_dashboard"
        elif result == "invalid_password":
            st.error("Неверный пароль. Попробуйте снова.")
        elif result == "user_not_found":
            st.error("Пользователь не найден.")
        else:
            st.error("Неизвестная роль.")

    elif st.button("Перейти на страницу регистрации"):
        st.session_state.page = "Регистрация"

