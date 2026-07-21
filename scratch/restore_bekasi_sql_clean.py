import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='',
    autocommit=True,
    client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
)

cur = conn.cursor()

print("--- RE-CREATING AND RESTORING JADWAL_BEKASI ---")
cur.execute("DROP DATABASE IF EXISTS `jadwal_bekasi`;")
cur.execute("CREATE DATABASE `jadwal_bekasi`;")
cur.execute("USE `jadwal_bekasi`;")

with open('d:/Jadwal/jadwal_bekasi (1).sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

# Execute full SQL dump
cur.execute(sql_script)

# Drain all results from multi-statement query
while cur.nextset():
    pass

cur.execute("SELECT COUNT(*) as c_cnt FROM classes;")
c_cnt = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) as t_cnt FROM teachers;")
t_cnt = cur.fetchone()[0]

cur.execute("SELECT nama_kelas FROM classes LIMIT 5;")
classes_sample = [r[0] for r in cur.fetchall()]

cur.execute("SELECT nama_guru FROM teachers LIMIT 5;")
teachers_sample = [r[0] for r in cur.fetchall()]

conn.close()

print("\n✅ BEKASI DATABASE RESTORATION COMPLETE!")
print(f"Total Classes in Bekasi: {c_cnt}")
print(f"Sample Classes: {classes_sample}")
print(f"Total Teachers in Bekasi: {t_cnt}")
print(f"Sample Teachers: {teachers_sample}")
