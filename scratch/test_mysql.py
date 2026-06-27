import os
import sys

# Setup environment
from dotenv import load_dotenv
load_dotenv()

from backend.database import get_db_connection, db_execute, db_fetchall, active_branch

def test():
    print("Testing Bekasi Branch...")
    active_branch.set("bekasi")
    conn = get_db_connection()
    try:
        db_execute(conn, "INSERT IGNORE INTO system_settings (`key`, `value`) VALUES ('test_key', 'test_value_bekasi')")
        res = db_fetchall(conn, "SELECT * FROM system_settings WHERE `key`='test_key'")
        print(f"Bekasi setting: {res}")
    finally:
        conn.close()

    print("\nTesting Jakarta Branch...")
    active_branch.set("jakarta")
    conn2 = get_db_connection()
    try:
        db_execute(conn2, "INSERT IGNORE INTO system_settings (`key`, `value`) VALUES ('test_key', 'test_value_jakarta')")
        res2 = db_fetchall(conn2, "SELECT * FROM system_settings WHERE `key`='test_key'")
        print(f"Jakarta setting: {res2}")
    finally:
        conn2.close()

if __name__ == "__main__":
    test()
