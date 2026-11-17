import psycopg


def connect(password):
    # Параметры передаём отдельно: символы @ и & в пароле допустимы.
    return psycopg.connect(
        host="aws-0-ap-southeast-2.pooler.supabase.com",
        port=5432,
        dbname="postgres",
        user="postgres.rswrwrjccqifgxjiemwh",
        password=password,
        sslmode="require",
        connect_timeout=15,
    )


def main():
    # Пароль вводится при запуске и не сохраняется в файле.
    password = input("Database password (visible): ")
    with connect(password) as connection:
        # Только проверяем подключение и наличие расширения pgvector.
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user")
            database, user = cursor.fetchone()
            print("Connected:", database, "as", user)

            cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            row = cursor.fetchone()
            print("pgvector:", row[0] if row else "not enabled")


if __name__ == "__main__":
    main()
