import psycopg2
import psycopg2.extras
from settings import DB_CONFIG
from repositories.users_id import get_user_id_by_login


def create_playlist(name: str, login: str):
    user_id = get_user_id_by_login(login)
    if user_id is None:
        return None

    query = "INSERT INTO playlists (name, date_creation) VALUES (%s, CURRENT_DATE) RETURNING playlist_id"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

                user_id = get_user_id_by_login(login)
                cur.execute(f"SET session.user_id = {user_id};")

                cur.execute(query, (name,))
                playlist_id = cur.fetchone()
                if playlist_id:
                    playlist_id = playlist_id['playlist_id']

                    insert_user_playlist_query = "INSERT INTO users_playlists (user_id, playlist_id) VALUES (%s, %s)"
                    cur.execute(insert_user_playlist_query, (user_id, playlist_id))
                    conn.commit()

                    return playlist_id
                else:
                    return None
    except Exception as e:
        print(f"Ошибка при создании плейлиста: {e}")
        return None


def add_to_playlist(playlist_name: str, song_name: str, login: str):
    get_song_id_query = "SELECT song_id FROM songs WHERE name = %s"
    get_playlist_id_query = "SELECT playlist_id FROM playlists WHERE name = %s"
    check_existing_query = "SELECT 1 FROM playlists_songs WHERE playlist_id = %s AND song_id = %s"

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

                user_id = get_user_id_by_login(login)
                cur.execute(f"SET session.user_id = {user_id};")

                cur.execute(get_song_id_query, (song_name,))
                song = cur.fetchone()
                if not song:
                    raise Exception(f"Песня с названием {song_name} не найдена.")
                song_id = song["song_id"]

                cur.execute(get_playlist_id_query, (playlist_name,))
                playlist = cur.fetchone()
                if not playlist:
                    raise Exception(f"Плейлист с названием {playlist_name} не найден.")
                playlist_id = playlist["playlist_id"]

                cur.execute(check_existing_query, (playlist_id, song_id))
                existing_song = cur.fetchone()
                if existing_song:
                    return "Песня уже добавлена в плейлист."

                query = "INSERT INTO playlists_songs (playlist_id, song_id) VALUES (%s, %s)"
                cur.execute(query, (playlist_id, song_id))
                conn.commit()
                return "Песня успешно добавлена в плейлист."

    except Exception as e:
        print(f"Ошибка при добавлении песни в плейлист: {e}")
        return "Произошла ошибка при добавлении песни в плейлист."



def get_user_playlists(login: str):

    query = """
    SELECT p.playlist_id, p.name 
    FROM playlists p
    JOIN users_playlists up ON p.playlist_id = up.playlist_id
    WHERE up.user_id = %s
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                user_id = get_user_id_by_login(login)
                cur.execute(query, (user_id,))
                playlists = cur.fetchall()
        return playlists
    except Exception as e:
        print(f"Ошибка при получении плейлистов: {e}")
        return None


def get_songs_from_playlist(playlist_id):
    query = """
    SELECT s.song_id, s.name AS song_name, a.name AS artist_name
    FROM songs s
    JOIN playlists_songs ps ON s.song_id = ps.song_id
    JOIN artists a ON s.artist_id = a.artist_id
    WHERE ps.playlist_id = %s
    ORDER BY s.name;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (playlist_id,))
                songs = cur.fetchall()
                if not songs:
                    return 0
            return songs
    except Exception as e:
        return []

def delete_playlist(playlist_name: str, login: str):
    user_id = get_user_id_by_login(login)
    if user_id is None:
        return None

    query = """SELECT playlist_id FROM playlists WHERE name = %s"""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                user_id = get_user_id_by_login(login)
                cur.execute(f"SET session.user_id = {user_id};")
                cur.execute(query, (playlist_name,))
                playlist = cur.fetchone()
                if playlist:
                    playlist_id = playlist['playlist_id']

                    delete_playlist_query = "DELETE FROM playlists WHERE playlist_id = %s"
                    cur.execute(delete_playlist_query, (playlist_id,))
                    conn.commit()

                    return playlist_id
                else:
                    return None
    except Exception as e:
        print(f"Ошибка при удалении плейлиста: {e}")
        return None


def delete_song_from_playlist(playlist_name: str, song_name: str, login: str):
    user_id = get_user_id_by_login(login)
    if user_id is None:
        return None

    query_playlist = """SELECT playlist_id FROM playlists WHERE name = %s"""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                user_id = get_user_id_by_login(login)
                cur.execute(f"SET session.user_id = {user_id};")
                cur.execute(query_playlist, (playlist_name,))
                playlist = cur.fetchone()
                if playlist:
                    playlist_id = playlist['playlist_id']

                    query_song = """SELECT song_id FROM songs WHERE name = %s"""
                    cur.execute(query_song, (song_name,))
                    song = cur.fetchone()
                    if song:
                        song_id = song['song_id']
                        delete_song_query = """DELETE FROM playlists_songs WHERE playlist_id = %s AND song_id = %s"""
                        cur.execute(delete_song_query, (playlist_id, song_id))
                        conn.commit()
                        return song_id
                    else:
                        return None
                else:
                    return None
    except Exception as e:
        print(f"Ошибка при удалении песни из плейлиста: {e}")
        return None



