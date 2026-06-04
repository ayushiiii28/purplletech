# =====================================================
# SQLITE DATABASE SETUP
# =====================================================

import sqlite3

# =====================================================
# CONNECT DATABASE
# =====================================================

conn = sqlite3.connect(

    "store_analytics.db",

    check_same_thread=False
)

cursor = conn.cursor()

# =====================================================
# CREATE EVENTS TABLE
# =====================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS events (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    event_id TEXT,

    store_id TEXT,

    camera_id TEXT,

    visitor_id TEXT,

    event_type TEXT,

    timestamp TEXT,

    zone_id TEXT,

    dwell_ms INTEGER,

    is_staff BOOLEAN,

    confidence REAL,

    metadata TEXT
)

""")

# =====================================================
# CREATE INDEXES
# =====================================================

cursor.execute("""

CREATE INDEX IF NOT EXISTS idx_event_type

ON events(event_type)

""")

cursor.execute("""

CREATE INDEX IF NOT EXISTS idx_store_id

ON events(store_id)

""")

cursor.execute("""

CREATE INDEX IF NOT EXISTS idx_timestamp

ON events(timestamp)

""")

# =====================================================
# COMMIT CHANGES
# =====================================================

conn.commit()

print("\nDatabase initialized successfully")

