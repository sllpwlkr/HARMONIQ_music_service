import streamlit as st
import psycopg2
import psycopg2.extras
import csv
import random
from io import StringIO
from datetime import datetime
from repositories.users_id import get_user_id_by_login
from settings import DB_CONFIG

def add_tracks_from_csv(file, login: str):
    try:
        file.seek(0)
        reader = csv.DictReader(StringIO(file.read().decode('utf-8')))

        required_columns = {'song_name', 'artist_name', 'genre_name', 'duration'}
        if not required_columns.issubset(reader.fieldnames):
            st.error("CSV файл должен содержать колонки: 'song_name', 'artist_name', 'genre_name', 'duration'")
            return

        for row in reader:
            song_name = row['song_name'].strip()
            artist_name = row['artist_name'].strip()
            genre_name = row['genre_name'].strip()
            duration = row['duration'].strip()

            result = add_track(song_name, artist_name, genre_name, login, duration)
            st.write(result)
    except Exception as e:
        st.error(f"Ошибка при обработке файла: {e}")


def add_track(song_name: str, artist_name: str, genre_name: str, login:str, duration: str):
    try:
        duration_time = datetime.strptime(duration, "%M:%S").time()

        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                user_id = get_user_id_by_login(login)
                cur.execute(f"SET session.user_id = {user_id};")
                cur.execute("""SELECT song_id FROM songs WHERE name = %s;""", (song_name,))
                song = cur.fetchone()

                if song:
                    return (f"Трек '{song_name}' уже существует в базе данных.")


                cur.execute("""SELECT artist_id FROM artists WHERE name = %s;""", (artist_name,))
                artist = cur.fetchone()

                if not artist:
                    cur.execute("""INSERT INTO artists (name) VALUES (%s) RETURNING artist_id;""", (artist_name,))
                    artist_id = cur.fetchone()['artist_id']

                else:
                    artist_id = artist['artist_id']

                cur.execute("""SELECT genre_id FROM genres WHERE name = %s;""", (genre_name,))
                genre = cur.fetchone()

                if not genre:
                    cur.execute("""INSERT INTO genres (name) VALUES (%s) RETURNING genre_id;""", (genre_name,))
                    genre_id = cur.fetchone()['genre_id']

                else:
                    genre_id = genre['genre_id']

                cur.execute("""INSERT INTO songs (name, artist_id, genre_id, duration) VALUES (%s, %s, %s, %s);""",
                            (song_name, artist_id, genre_id, duration_time))

                conn.commit()

                return f"Трек '{song_name}' успешно добавлен."

    except Exception as e:
        print(f"Ошибка при добавлении трека: {e}")
        return "Произошла ошибка при добавлении трека."

def counts_listens(song_name: str):
    try:

        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT song_id FROM songs WHERE name = %s", (song_name,))
                song = cur.fetchone()

                if song:
                    song_id = song[0]
                    cur.execute("SELECT count_listen FROM songs_listens WHERE song_id = %s", (song_id,))
                    listen = cur.fetchone()
                    random_count = random.randint(1, 100)
                    if listen:
                        new_count = listen[0] + random_count
                        cur.execute("UPDATE songs_listens SET count_listen = %s WHERE song_id = %s",
                                    (new_count, song_id))
                    else:
                        cur.execute("INSERT INTO songs_listens (song_id, count_listen) VALUES (%s, 1)", (song_id,))

                    conn.commit()

                else:
                    print(f"Песня '{song_name}' не найдена в базе данных.")
    except Exception as e:
        print(f"Ошибка при воспроизведении песни: {e}")


def get_all_songs():
    query = """SELECT s.name AS song_name, a.name AS artist_name
                FROM songs s
                JOIN artists a ON s.artist_id = a.artist_id
                ORDER BY s.name;"""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                songs = cur.fetchall()
                return songs
    except Exception as e:
        print(f"Ошибка при получении песен: {e}")
        return []

def delete_track(song_name: str, login: str):
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

                user_id = get_user_id_by_login(login)
                cur.execute(f"SET session.user_id = {user_id};")

                cur.execute("SELECT song_id FROM songs WHERE name = %s;", (song_name,))
                song = cur.fetchone()
                if not song:
                    return f"Трек '{song_name}' не найден."
                song_id = song['song_id']

                cur.execute("DELETE FROM songs WHERE song_id = %s;", (song_id,))
                conn.commit()

                return f"Трек '{song_name}' успешно удалён."
    except Exception as e:
        return f"Ошибка при удалении трека: {e}"


def get_all_artists():
    query = """SELECT a.name AS artist_name
                FROM artists a
                ORDER BY a.name;"""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                artists = cur.fetchall()  # Получаем все песни
                return artists
    except Exception as e:
        print(f"Ошибка при получении исполнителей: {e}")
        return []

def delete_artist(artist_name: str, login: str):
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

                user_id = get_user_id_by_login(login)
                cur.execute(f"SET session.user_id = {user_id};")

                cur.execute("SELECT artist_id FROM artists WHERE name = %s;", (artist_name,))
                artist = cur.fetchone()
                if not artist:
                    return f"Исполнитель '{artist_name}' не найден."

                artist_id = artist['artist_id']

                cur.execute("DELETE FROM artists WHERE artist_id = %s;", (artist_id,))
                conn.commit()

                return f"Исполнитель '{artist_name}' успешно удалён."
    except Exception as e:
        return f"Ошибка при удалении исполнителя: {e}"