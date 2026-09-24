from sqlalchemy import text
from app.database.database import engine

with engine.begin() as conn:
    conn.execute(text("ALTER TABLE packages ADD COLUMN IF NOT EXISTS relevance_score INTEGER NOT NULL DEFAULT 0;"))
    conn.execute(text("ALTER TABLE packages ADD COLUMN IF NOT EXISTS priority VARCHAR NOT NULL DEFAULT 'LOW';"))
    rows = conn.execute(text("SELECT id, name, downloads, is_monitored, relevance_score, priority FROM packages ORDER BY id")).fetchall()
    for row in rows:
        print(row)
