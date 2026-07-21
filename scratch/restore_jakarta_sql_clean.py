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

print("--- RE-CREATING AND RESTORING JADWAL_JAKARTA FROM ORIGINAL SQL DUMP ---")
cur.execute("DROP DATABASE IF EXISTS `jadwal_jakarta`;")
cur.execute("CREATE DATABASE `jadwal_jakarta`;")
cur.execute("USE `jadwal_jakarta`;")

with open('d:/Jadwal/jadwal_jakarta.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

cur.execute(sql_script)

while cur.nextset():
    pass

cur.execute("SELECT COUNT(*) FROM classes;")
c_cnt = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM teachers;")
t_cnt = cur.fetchone()[0]

cur.execute("SELECT id_guru, kode_guru, nama_guru, hari_tersedia_pagi, hari_tersedia_siang FROM teachers LIMIT 5;")
sample_teachers = cur.fetchall()

conn.close()

print("\n✅ JADWAL_JAKARTA RESTORATION COMPLETE!")
print(f"Total Classes in Jakarta : {c_cnt}")
print(f"Total Teachers in Jakarta: {t_cnt}")
print("\nSample Custom Availability in Jakarta:")
for t in sample_teachers:
    print(f" - {t[2]}: Pagi={t[3]}, Siang={t[4]}")
