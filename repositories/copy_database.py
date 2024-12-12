from settings import DB_CONFIG
import subprocess
import os
import streamlit as st
import time

def backup_database():
    time.sleep(10)
    try:
        backup_file = "backup.sql"
        os.environ["PGPASSWORD"] = DB_CONFIG["password"]
        command = [
            r'C:\Program Files\PostgreSQL\17\bin\pg_dump',
            '-U', DB_CONFIG["user"],  # Имя пользователя базы данных
            '-h', DB_CONFIG["host"],  # Хост базы данных (например, localhost)
            '-p', DB_CONFIG["port"],  # Порт (обычно 5432)
            '-b',  # Включить большие объекты
            '--encoding', 'UTF8',  # Кодировка резервной копии (например, UTF-8)
            '-f', backup_file,  # Имя файла для дампа
            DB_CONFIG["dbname"],  # Имя базы данных
        ]

        with st.spinner('Создание резервной копии базы данных...'):
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                st.success(f"Резервная копия базы данных создана успешно. Файл: {backup_file}")

                with open(backup_file, "rb") as file:
                    st.download_button(
                        label="Скачать резервную копию",
                        data=file,
                        file_name=backup_file,
                        mime="application/octet-stream"
                    )
            else:
                st.error(f"Ошибка при создании резервной копии: {result.stderr}")
    except Exception as e:
        st.error(f"Ошибка: {str(e)}")
