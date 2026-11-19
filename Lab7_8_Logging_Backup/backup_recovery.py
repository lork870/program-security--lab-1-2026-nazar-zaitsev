import hashlib
import os
import shutil
import sqlite3
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "liberink_prod.db")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def init_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE BookElements (
            Id INTEGER PRIMARY KEY,
            UserId TEXT NOT NULL,
            Title TEXT NOT NULL,
            EncryptedContent TEXT NOT NULL
        )
    """)
    cur.executemany(
        "INSERT INTO BookElements (UserId, Title, EncryptedContent) VALUES (?, ?, ?)",
        [
            ("uid_101", "Chapter 1: Prologue", "aes256gcm:9a8f7c..."),
            ("uid_101", "Character Lore: Elena", "aes256gcm:3b1d2e..."),
            ("uid_205", "Draft Notes", "aes256gcm:7f4c9a..."),
        ],
    )
    conn.commit()
    conn.close()
    print(f"[1] Database initialized: {DB_PATH} (3 records)")


def create_backup():
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    backup_path = os.path.join(BACKUP_DIR, f"liberink_backup_{ts}.db")
    hash_path = backup_path + ".sha256"

    # Безпечне онлайн-копіювання SQLite
    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(backup_path)
    src.backup(dst)
    dst.close()
    src.close()

    checksum = sha256_file(backup_path)
    with open(hash_path, "w", encoding="utf-8") as f:
        f.write(checksum)

    print(f"[2] Backup created: {os.path.basename(backup_path)}")
    print(f"    SHA-256: {checksum}")
    return backup_path, hash_path


def simulate_disaster():
    os.remove(DB_PATH)
    print(f"[3] DISASTER SIMULATED: Production DB deleted! Exists: {os.path.exists(DB_PATH)}")


def restore_from_backup(backup_path: str, hash_path: str):
    with open(hash_path, "r", encoding="utf-8") as f:
        expected_hash = f.read().strip()

    actual_hash = sha256_file(backup_path)
    if actual_hash != expected_hash:
        raise RuntimeError("Backup integrity check FAILED! Hash mismatch.")

    print(f"[4] Integrity check PASSED (SHA-256 matches).")
    shutil.copy2(backup_path, DB_PATH)
    print(f"[5] Database restored to: {DB_PATH}")


def verify_restored_data():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT Id, UserId, Title FROM BookElements").fetchall()
    conn.close()
    print(f"[6] Post-recovery verification ({len(rows)} records restored):")
    for row in rows:
        print(f"    - {row}")


if __name__ == "__main__":
    init_database()
    b_path, h_path = create_backup()
    simulate_disaster()
    restore_from_backup(b_path, h_path)
    verify_restored_data()