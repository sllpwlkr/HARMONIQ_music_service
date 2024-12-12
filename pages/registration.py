import streamlit as st
from repositories.passwords import register_user

def show_registration_page():
    st.title("Регистрация")
    no_sidebar_style = """
                <style>
                    div[data-testid="stSidebarNav"] {display: none;}
                </style>
            """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)
    with st.sidebar:
        if st.button("Выйти"):
            st.session_state.page = "Вход"
            st.query_params = {"page": "login"}

    username = st.text_input("Введите логин")
    password = st.text_input("Введите пароль", type="password")
    confirm_password = st.text_input("Подтвердите пароль", type="password")

    role = st.selectbox("Выберите роль", options=[2, 1], format_func=lambda x: "Пользователь" if x == 2 else "Администратор")
    if role == 1:
        admin_password = st.text_input("Введите код доступа к этой роли", type="password")

    st.markdown("---")
    if st.button("Зарегистрироваться"):

        if not password.strip() or not username.strip():
            st.error("Логин и пароль не могут быть пустыми. Попробуйте снова.")
            return
        elif password != confirm_password:
            st.error("Пароли не совпадают. Проверьте введенный пароль.")
        else:
            if role == 1 and admin_password != "admin_password":
                st.error("Вам отказано в доступе")
            else:
                result = register_user(username, password, role)
                if result == "registration_success":
                    st.success("Пользователь успешно зарегистрирован!")
                    st.info("Нажмите на кнопку 'Выйти'")
                elif result == "user_exists":
                    st.warning("Пользователь с таким логином уже существует.")
                else:
                    st.error("Произошла ошибка во время регистрации. Попробуйте позже.")
