from sqlalchemy import text

from app.database.database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        print("PostgreSQL connection successful!")
        print(result.fetchone()[0])

except Exception as e:
    print("PostgreSQL connection failed!")
    print(e)