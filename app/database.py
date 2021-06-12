import psycopg2
import uuid

class PostgreSQLConnection():
    def __init__(self):
        self.conn = psycopg2.connect('')

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id uuid NOT NULL UNIQUE,
                    identifier_type varchar NOT NULL,
                    identifier varchar NOT NULL,
                    interests varchar[],
                    fav_sources varchar[]
                );
                CREATE TABLE IF NOT EXISTS sources (
                    id uuid NOT NULL UNIQUE,
                    link text NOT NULL UNIQUE
                );
                CREATE TABLE IF NOT EXISTS clicks (
                    user_id uuid NOT NULL,
                    source_id uuid NOT NULL,
                    count integer DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS views (
                    user_id uuid NOT NULL,
                    source_id uuid NOT NULL,
                    time integer
                );
                CREATE TABLE IF NOT EXISTS stars (
                    user_id uuid NOT NULL,
                    source_id uuid NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reports (
                    id uuid NOT NULL UNIQUE,
                    user_id uuid NOT NULL,
                    source_id uuid NOT NULL,
                    title varchar NOT NULL,
                    description text NOT NULL
                );
                """
            )

    def drop_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                DROP TABLE IF EXISTS users;
                DROP TABLE IF EXISTS sources;
                DROP TABLE IF EXISTS clicks;
                DROP TABLE IF EXISTS views;
                DROP TABLE IF EXISTS stars;
                DROP TABLE IF EXISTS reports;
                """
            )

    def create_user(self, id, identifier_type, identifier):
        self.create_tables()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (id, identifier_type, identifier)
                VALUES ('{0}', '{1}', '{2}')
                ON CONFLICT DO NOTHING;
                """.format(id, identifier_type, identifier)
            )
        print("New User: id={0} identifier_type={1} identifier={2}".format(id, identifier_type, identifier))