import bcrypt
import psycopg2
import psycopg2.extras
from settings import DB_CONFIG
from repositories.users_id import get_user_id_by_login

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(stored_hash: str, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))


def authenticate_user(login: str, password: str):
    query = f"SELECT hash_password, role_id FROM users WHERE login = %s"

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (login,))
            result = cur.fetchone()

    if result:
        stored_hash = result['hash_password']
        role_id = result['role_id']

        if check_password(stored_hash, password):
            if role_id == 1:
                return "admin_dashboard"
            elif role_id == 2:
                return "user_dashboard"
            else:
                return "unknown_role"
        else:
            return "invalid_password"
    else:
        return "user_not_found"


def register_user(login: str, password: str, role_id: int ) -> str:
    user_id = get_user_id_by_login(login)
    insert_query = """
    INSERT INTO users (login, hash_password, role_id)
    VALUES (%s, %s, %s)
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                if user_id:
                    return "user_exists"

                hashed_password = hash_password(password)
                cur.execute(insert_query, (login, hashed_password, role_id))
                conn.commit()

                return "registration_success"
    except Exception as e:
        print(f"Error during registration: {e}")
        return "registration_error"