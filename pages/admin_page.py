import streamlit as st
import pandas as pd
import datetime
from datetime import datetime
from io import StringIO

from repositories.music import add_tracks_from_csv
from repositories.copy_database import backup_database
from repositories.statistics import get_user_actions, get_top_artists, get_top_songs
from repositories.music import add_track, get_all_songs, delete_track , get_all_artists, delete_artist

def show_admin_page():
    with st.sidebar:
        st.header("Действия")
        selected_function = st.radio("Выберите действие",["Добавить треки", "Удалить треки или исполнителя","Статистика","Копия базы данных"])
        if st.button("Выйти"):
            st.session_state.page = "Вход"
            st.query_params = {"page": "login"}
        if st.button("Обновить страницу"):
            st.success("Cтраница обновлена")

    st.title(f"Добро пожаловать, {st.session_state['current_user']}!")
    no_sidebar_style = """
                <style>
                    div[data-testid="stSidebarNav"] {display: none;}
                </style>
            """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)

    if selected_function == "Добавить треки":
        add()
    elif selected_function == "Удалить треки или исполнителя":
        delete()
    elif selected_function == "Статистика":
        statics()
    elif selected_function == "Копия базы данных":
        copy()

def add():
        st.subheader("Добавить трек, исполнителя и жанр")
        current_user = st.session_state.get('current_user')

        choice = st.selectbox("Выбрать действие",["Добавить трек вручную","Загрузить файл"])

        if choice == "Добавить трек вручную":
            song = st.text_input("Трек:")
            artist = st.text_input("Исполнитель:")
            genre = st.text_input("Жанр:")
            duration = st.text_input("Длительность (мм:сс):")

            if st.button("Добавить трек"):
                if song and artist and genre and duration:
                    result = add_track(song, artist, genre, current_user, duration)
                    st.write(result)
                else:
                    st.warning("Пожалуйста, заполните все поля.")
        else:
            st.title("Загрузка треков из CSV")
            st.write("Загрузите CSV файл с колонками: 'song_name', 'artist_name', 'genre_name', 'duration'")

            uploaded_file = st.file_uploader("Выберите CSV файл", type=["csv"])

            if uploaded_file :
                file_data = uploaded_file.read().decode('utf-8')
                dataframe = pd.read_csv(StringIO(file_data))

                st.write("Предварительный просмотр загруженного файла:")
                st.dataframe(dataframe)
                if st.button("Загрузить треки"):
                    add_tracks_from_csv(uploaded_file, current_user)

def delete():
    st.subheader("Удалить трек или исполнителя")
    current_user = st.session_state.get('current_user')
    choice = st.selectbox("Выбрать действие", ["Удалить трек", "Удалить исполнителя"])

    if choice == "Удалить трек":
        tracks = get_all_songs()

        if tracks:
            song_choices = [f"{song['song_name']} - {song['artist_name']}" for song in tracks]
        else:
            st.warning("Список треков пуст.")
            return
        selected_track = st.selectbox("Выберите трек для удаления:", song_choices)

        if st.button("Удалить трек"):
            if selected_track:
                song_name = selected_track.split(" - ")[0]
                result = delete_track(song_name, current_user)
                st.success(result)
            else:
                st.warning("Пожалуйста, выберите трек для удаления.")
    else:
        artists = get_all_artists()
        if artists:
            artist_choices = [f"{artist['artist_name']}" for artist in artists]
        else:
            st.warning("Список исполнителей пуст.")
            return
        selected_artist = st.selectbox("Выберите исполнителя для удаления:", artist_choices)
        if st.button("Удалить исполнителя"):
            if selected_artist:
                result = delete_artist(selected_artist, current_user)
                st.success(result)
            else:
                st.warning("Пожалуйста, выберите исполнителя для удаления.")



def statics():
    choice = st.selectbox("Статистика", ["Действия пользователей", "Популярные треки", "Популярные исполнители"])

    if choice == "Действия пользователей":
        st.subheader("Посмотреть статистику по пользователям")

        login = st.text_input('Введите логин пользователя')
        selected_date = st.date_input("Выберите дату для просмотра статистики", datetime.today().date())

        if st.button("Получить данные о действиях пользователя"):
            if login:
                data = get_user_actions(login, selected_date)
                if isinstance(data, list) and data:
                    df = pd.DataFrame(data)
                    df.index += 1
                    st.table(df)
                elif isinstance(data, str) and data == "Пользователь не найден":
                    st.warning("Пользователь не найден.")
                else:
                    st.warning("Данных о действиях для этого пользователя за выбранную дату не найдено.")
            else:
                st.warning("Пожалуйста, введите логин пользователя.")

    elif choice == "Популярные исполнители":
        st.subheader("Топ-10 популярных артистов")
        top_artists = get_top_artists()
        if top_artists is not None:
            st.table(top_artists)
        else:
            st.error("Не удалось загрузить статистику. Проверьте соединение с базой данных.")

    elif choice == "Популярные треки":
        st.subheader("Топ-10 популярных треков")
        top_songs = get_top_songs()
        if top_songs is not None:
            st.table(top_songs)
        else:
            st.error("Не удалось загрузить статистику. Проверьте соединение с базой данных.")

def copy():
        st.subheader("Сделать копию базы данных")
        if st.button("Получить файл"):
            backup_database()
