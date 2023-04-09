from sqlalchemy import create_engine
import psycopg2
def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='school',
                            user='postgres',
                            password='Otsi1234',
                            )
    return conn

def pg_engine():
    pg_Lhengine = create_engine('postgresql://postgres:Otsi1234@localhost/school')
    return pg_Lhengine
    