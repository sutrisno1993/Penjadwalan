import os
import sys

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import get_db_connection, init_db, save_setting, get_setting

def test():
    print("Inisialisasi DB...")
    init_db()
    save_setting("split_multi_subject_teacher_days", "true")
    save_setting("multi_subject_jp_threshold", "4")
    
    print("Fetching settings...")
    print("split_multi:", get_setting("split_multi_subject_teacher_days"))
    print("threshold:", get_setting("multi_subject_jp_threshold"))
    print("TEST SUCCESS!")

if __name__ == "__main__":
    test()
