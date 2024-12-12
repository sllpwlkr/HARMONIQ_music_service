import psycopg2
import psycopg2.extras
from settings import DB_CONFIG

def get_user_id_by_login(login: str):
    query = "SELECT user_id FROM users WHERE login = %s"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (login,))
                result = cur.fetchone()
                if result:
                    return result['user_id']
                else:

                    return None
    except Exception as e:
        print(f"Ошибка при получении user_id для {login}: {e}")
        return None