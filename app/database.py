import psycopg2
from app import config

class PostgreSQLConnection():
    def __init__(self):
        self.conn = psycopg2.connect(
            host=config['PGHOST'],
            port=config['PGPORT'],
            dbname=config['PGDATABASE'],
            user=config['PGUSER'],
            password=config['PGPASSWORD'],
            options=config['PGOPTIONS'],
            sslmode=config['PGSSLMODE'],
            sslrootcert=config['PGSSLROOTCERT']
        )
        self.conn.autocommit = True

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id uuid NOT NULL UNIQUE,
                    user_identifier_type varchar NOT NULL,
                    user_identifier varchar NOT NULL,
                    clicked_source_id uuid[] DEFAULT '{}',
                    starred_source_id uuid[] DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS sources (
                    source_id uuid NOT NULL UNIQUE,
                    title varchar NOT NULL,
                    description text NOT NULL,
                    link text NOT NULL,
                    domain varchar NOT NULL
                );
                """
            )

    def drop_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(
                # """
                # DROP TABLE IF EXISTS users;
                # """
                """
                DROP TABLE IF EXISTS users;
                DROP TABLE IF EXISTS sources;
                """
            )

    def create_user(self, id, identifier_type, identifier):
        self.create_tables()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (user_id, user_identifier_type, user_identifier)
                VALUES ('{0}', '{1}', '{2}')
                ON CONFLICT DO NOTHING;
                """.format(id, identifier_type, identifier)
            )
        print("New User: user_id={0} user_identifier_type={1} user_identifier={2}".format(id, identifier_type, identifier))

    def get_user(self, user_id):
        self.create_tables()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM users
                WHERE user_id = '{0}';
                """.format(user_id)
            )
            user = cur.fetchone()
            if user == None:
                return None
            return {
                'user_id': user[0],
                'user_identifier_type': user[1],
                'user_identifier': user[2],
                'clicked_source_id': list(user[3].replace('{', '').replace('}', '').replace(' ', '').split(',')),
                'starred_source_id': list(user[4].replace('{', '').replace('}', '').replace(' ', '').split(','))
            }

    def create_source(self, source_vals):
        self.create_tables()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sources (source_id, title, description, link, domain)
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')
                ON CONFLICT DO NOTHING;
                """.format(source_vals['id'], source_vals['title'], source_vals['description'], source_vals['link'], source_vals['domain'])
            )

    def get_source(self, source_id):
        self.create_tables()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM sources
                WHERE source_id = '{0}';
                """.format(source_id)
            )
            source = cur.fetchone()
            if source == None:
                return None
            return {
                'source_id': source[0],
                'title': source[1],
                'description': source[2],
                'link': source[3],
                'domain': source[4]
            }

    def add_user_click(self, user_id, source_id):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET clicked_source_id = array_append(clicked_source_id, '{0}')
                WHERE user_id = '{1}';
                """.format(source_id, user_id)
            )

    def add_user_star(self, user_id, source_id):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET starred_source_id = array_append(starred_source_id, '{0}')
                WHERE user_id = '{1}';
                """.format(source_id, user_id)
            )

    def remove_user_star(self, user_id, source_id):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET starred_source_id = array_remove(starred_source_id, '{0}')
                WHERE user_id = '{1}';
                """.format(source_id, user_id)
            )

    def get_user_stars(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT starred_source_id
                FROM users
                WHERE user_id = '{0}';
                """.format(user_id)
            )
            user_stars = cur.fetchone()
            if user_stars == None:
                return None
            return list(user_stars[0].replace('{', '').replace('}', '').replace(' ', '').split(','))

    def get_user_clicks(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT clicked_source_id
                FROM users
                WHERE user_id = '{0}';
                """.format(user_id)
            )
            user_clicks = cur.fetchone()
            if user_clicks == None:
                return None
            return list(user_clicks[0].replace('{', '').replace('}', '').replace(' ', '').split(','))