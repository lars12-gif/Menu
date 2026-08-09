"""
db.py
طبقة قاعدة البيانات (SQLite) لموقع المنيو.
كل التعامل مع الأصناف والأطعمة يمر من هنا فقط.
"""

import sqlite3
from contextlib import contextmanager

DB_PATH = "menu.db"


@contextmanager
def get_connection():
    """يفتح اتصال بقاعدة البيانات ويغلقه (ويحفظ التغييرات) تلقائياً بعد الانتهاء."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """ينشئ الجداول إذا ما كانت موجودة. يُستدعى مرة وحدة عند بدء التطبيق."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                price       REAL NOT NULL,
                description TEXT DEFAULT '',
                image_path  TEXT DEFAULT '',
                available   INTEGER NOT NULL DEFAULT 1,
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
            """
        )


# ---------------------------------------------------------------------------
# الأصناف (Categories)
# ---------------------------------------------------------------------------

def get_categories():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
        return [dict(r) for r in rows]


def add_category(name: str):
    name = (name or "").strip()
    if not name:
        return False, "اسم الصنف ما يصير يكون فارغ"
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        return True, f"تمت إضافة صنف «{name}» بنجاح"
    except sqlite3.IntegrityError:
        return False, "هذا الصنف موجود مسبقاً"


def delete_category(category_id: int):
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM items WHERE category_id = ?", (category_id,)
        ).fetchone()[0]
        if count > 0:
            return False, "ما تكدر تحذف هذا الصنف لأنه يحتوي أطعمة، احذف الأطعمة أولاً"
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    return True, "تم حذف الصنف"


# ---------------------------------------------------------------------------
# الأطعمة (Items)
# ---------------------------------------------------------------------------

def get_items(category_id: int | None = None):
    with get_connection() as conn:
        if category_id:
            rows = conn.execute(
                "SELECT * FROM items WHERE category_id = ? ORDER BY name",
                (category_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM items ORDER BY category_id, name"
            ).fetchall()
        return [dict(r) for r in rows]


def get_item(item_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return dict(row) if row else None


def add_item(name, price, description, image_path, available, category_id):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO items (name, price, description, image_path, available, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                (name or "").strip(),
                float(price),
                (description or "").strip(),
                image_path or "",
                int(bool(available)),
                category_id,
            ),
        )


def update_item(item_id, name, price, description, image_path, available, category_id):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE items
            SET name = ?, price = ?, description = ?, image_path = ?, available = ?, category_id = ?
            WHERE id = ?
            """,
            (
                (name or "").strip(),
                float(price),
                (description or "").strip(),
                image_path or "",
                int(bool(available)),
                category_id,
                item_id,
            ),
        )


def delete_item(item_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
