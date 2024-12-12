import streamlit as st

from repositories.music import get_all_songs, counts_listens  # Импортируем функцию для получения всех песен
from repositories.playlists import add_to_playlist, create_playlist, get_user_playlists, get_songs_from_playlist , delete_playlist, delete_song_from_playlist



def show_user_page():
    with st.sidebar:
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
    current_user = st.session_state.get('current_user')

    st.subheader("Ваши плейлисты")
    name = st.text_input("Введите название плейлиста")

    if st.button("Создать новый плейлист"):
        if not name.strip():
            st.error("Название плейлиста не может быть пустым. Попробуйте снова.")
        else:
            create_playlist(name, current_user)
            st.success(f"Плейлист '{name}' создан.")

    playlists = get_user_playlists(st.session_state["current_user"])
    if playlists:
        playlist_names = [playlist["name"] for playlist in playlists]
        selected_playlist_name = st.selectbox("Выберите плейлист", playlist_names, key="playlist_select")

        selected_playlist = next(playlist for playlist in playlists if playlist["name"] == selected_playlist_name)
        playlist_id = selected_playlist["playlist_id"]
        st.write(f"Плейлист: {selected_playlist_name}")
        if st.button("Удалить выбранный плейлист"):
            delete_playlist(selected_playlist_name, current_user)
            st.success(f"Плейлист: ' {selected_playlist_name}' удалён")
        songs_in_playlist = get_songs_from_playlist(playlist_id)
        if songs_in_playlist:
            song_choices = [f"{song['song_name']} - {song['artist_name']}" for song in songs_in_playlist]

            selected_song = st.selectbox(f"Выберите песню из плейлиста {selected_playlist_name}", song_choices,
                                         key=f"song_select_{playlist_id}")
            task = st.selectbox('Выбрать действие для песни',['Прослушать','Удалить'])
            if task == 'Прослушать':
                if st.button(f"Послушать {selected_song}", key=f"play_button_{playlist_id}"):
                    counts_listens(selected_song.split(" - ")[0])
                    st.success(f"Играет: {selected_song}")
                    st.info("Чтобы не нарушать авторские права, песня воспроизводиться не будет")
            else:
                if st.button("Удалить песню из плейлиста"):
                    delete_song_from_playlist(selected_playlist_name, selected_song.split(" - ")[0], current_user)
                    st.success(f"Песня: '{selected_song}' удалена")
        else:
            st.write("В этом плейлисте нет песен.")

        all_songs = get_all_songs()
        if all_songs:
            song_choices = [f"{song['song_name']} - {song['artist_name']}" for song in all_songs]
            selected_song_to_add = st.selectbox(
                f"Выберите песню для добавления в плейлист {selected_playlist_name}",
                song_choices, key=f"song_add_{playlist_id}")

            if st.button(f"Добавить песню в {selected_playlist_name}", key=f"add_button_{playlist_id}"):
                if not selected_song_to_add:
                    st.error("Песня не выбрана.")
                else:
                    result = add_to_playlist(selected_playlist_name, selected_song_to_add.split(" - ")[0],
                                             st.session_state["current_user"])
                    if result == "Песня успешно добавлена в плейлист.":
                        st.success(f"Песня '{selected_song_to_add}' добавлена в плейлист '{selected_playlist_name}'")
                    else:
                        st.warning(result)
    else:
        st.warning("У вас нет плейлистов. Создайте новый!")
