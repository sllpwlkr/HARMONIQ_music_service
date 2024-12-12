import psycopg2
import psycopg2.extras
import pandas as pd
from settings import DB_CONFIG
from repositories.users_id import get_user_id_by_login

def get_user_actions(login, selected_date):
    query = """
    SELECT actions.name AS action_name, log_actions.action_time
    FROM log_actions
    JOIN users ON log_actions.user_id = users.user_id
    JOIN actions ON log_actions.action_id = actions.action_id
    WHERE users.login = %s AND DATE(log_actions.action_time) = %s
    ORDER BY log_actions.action_time DESC;
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                user_id = get_user_id_by_login(login)

                if not user_id:
                    return "Пользователь не найден"

                cur.execute(query, (login, selected_date))
                result = cur.fetchall()

        return result if result else []
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return "error"

def get_top_artists():
    query = """
    SELECT 
        ar.name AS artist_name,
        SUM(sl.count_listen) AS total_listens
    FROM artists ar
    JOIN songs s ON ar.artist_id = s.artist_id
    RIGHT JOIN songs_listens sl ON s.song_id = sl.song_id
    GROUP BY ar.artist_id, ar.name
    ORDER BY total_listens DESC
    LIMIT 10;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()

        df = pd.DataFrame(result, columns=["Артист", "Количество прослушиваний"])
        df.index += 1
        return df
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")
        return None

def get_top_songs():
    query = """
    SELECT s.name AS song_name, COALESCE(sl.count_listen, 0) AS listens
    FROM songs s
    LEFT JOIN songs_listens sl ON s.song_id = sl.song_id
    ORDER BY listens DESC
    LIMIT 10;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()

        df = pd.DataFrame(result, columns=["Трек", "Количество прослушиваний"])
        df.index += 1
        return df
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")
        return None