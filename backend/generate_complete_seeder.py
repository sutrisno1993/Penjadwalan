import json
import os

# 1. Define all 27 classes (including XI TKR 2)
CLASSES = [
    # X
    "X AK 1", "X OTKP 1", "X OTKP 2", "X TKJ 1", "X TKJ 2", "X TKR 1", "X TKR 2", "X TSM 1", "X TSM 2",
    # XI
    "XI AK 1", "XI OTKP 1", "XI OTKP 2", "XI TKJ 1", "XI TKJ 2", "XI TKR 1", "XI TKR 2", "XI TSM 1", "XI TSM 2",
    # XII
    "XII AK 1", "XII OTKP 1", "XII OTKP 2", "XII TKJ 1", "XII TKJ 2", "XII TKR 1", "XII TKR 2", "XII TSM 1", "XII TSM 2"
]

# 2. Corrected Screenshot Allocations (Teachers 14 - 37)
# Note: Fixed Teacher 24's transcription (removed XI TKJ 1 & 2)
SCREENSHOT_DATA = {
    14: {
        "OTK Kepegawaian": {"XI OTKP 1": 2, "XI OTKP 2": 2, "XII OTKP 1": 3, "XII OTKP 2": 3},
        "Adm Pajak": {"XI AK 1": 2, "XII AK 1": 2}
    },
    15: {
        "Matematika": {
            "X OTKP 2": 5, "X TKR 1": 5, "X TKR 2": 5, "X TSM 1": 5, "X TSM 2": 5,
            "XI AK 1": 5, "XI TSM 1": 5, "XI TSM 2": 5,
            "XII AK 1": 5, "XII TKJ 1": 5, "XII TKJ 2": 5, "XII TKR 1": 5, "XII TKR 2": 5
        }
    },
    16: {
        "Kelistrikan Kendaraan": {"XI TSM 1": 5, "XI TSM 2": 5},
        "Main. Mesin Sepeda Motor": {"XII TSM 1": 5, "XII TSM 2": 5},
        "TDO": {"X TKR 1": 4},
        "Main. Sasis Sepeda Motor": {"XI TSM 1": 4, "XI TSM 2": 4, "XII TSM 1": 5, "XII TSM 2": 5},
        "Kelistrikan Sepeda Motor": {"XI TSM 1": 4, "XI TSM 2": 4, "XII TSM 1": 5, "XII TSM 2": 5}
    },
    17: {
        "Bahasa Inggris": {
            "X AK 1": 4,
            "XI TKR 1": 4, "XI TKR 2": 4, "XI TSM 1": 4, "XI TSM 2": 4,
            "XII AK 1": 4, "XII OTKP 1": 4, "XII OTKP 2": 4, "XII TKJ 1": 4, "XII TKJ 2": 4
        }
    },
    18: {
        "Pendidikan Agama Islam": {
            "X OTKP 1": 2, "X TKJ 2": 2, "X TKR 1": 2,
            "XI TKJ 1": 2, "XI TKJ 2": 2, "XI TKR 1": 2, "XI TKR 2": 2, "XI TSM 1": 2, "XI TSM 2": 2,
            "XII TKJ 1": 2, "XII TKJ 2": 2, "XII TKR 1": 2, "XII TKR 2": 2, "XII TSM 1": 2, "XII TSM 2": 2
        }
    },
    19: {
        "Teknologi Infrastruktur Jaringan": {"XII TKJ 1": 4, "XII TKJ 2": 4},
        "KKA / Coding": {
            "XI AK 1": 2, "XI OTKP 1": 2, "XI OTKP 2": 2, "XI TKJ 1": 2, "XI TKJ 2": 2, "XI TKR 1": 2, "XI TKR 2": 2, "XI TSM 1": 2, "XI TSM 2": 2
        },
        "Teknologi Layanan Jaringan": {"XII TKJ 1": 4, "XII TKJ 2": 4}
    },
    20: {
        "Sejarah Indonesia": {
            "X TKJ 2": 2, "X TKR 1": 2, "X TKR 2": 2,
            "XI TKR 1": 2, "XI TKR 2": 2, "XI TSM 1": 2, "XI TSM 2": 2,
            "XII TKR 1": 2, "XII TKR 2": 2, "XII TSM 1": 2, "XII TSM 2": 2
        }
    },
    21: {
        "Main. Mesin Kendaraan": {"XII TKR 1": 5, "XII TKR 2": 5},
        "Main. Sasis Kendaraan": {"XII TKR 1": 5, "XII TKR 2": 5},
        "PDTO": {"X TKR 1": 4, "XI TKR 1": 4, "XI TKR 2": 4},
        "TDO": {"X TSM 1": 4},
        "Kelistrikan Kendaraan Ringan": {"XI TKR 1": 4, "XI TKR 2": 4, "XII TKR 1": 5, "XII TKR 2": 5}
    },
    22: {
        "Gambar Teknik": {"X TKR 1": 3, "X TKR 2": 3, "X TSM 1": 3, "X TSM 2": 3},
        "TDO": {"X TKR 2": 4},
        "K3LH": {"X AK 1": 2, "X OTKP 1": 2, "X OTKP 2": 2, "X TKJ 2": 3, "X TKR 1": 2, "X TKR 2": 2, "X TSM 1": 2, "X TSM 2": 2},
        "PDTO": {"X TSM 1": 4}
    },
    23: {
        "Bahasa Indonesia": {
            "X OTKP 1": 3, "X TKJ 1": 3, "X TKR 1": 3, "X TSM 1": 3,
            "XI OTKP 1": 3, "XI OTKP 2": 3, "XI TKJ 1": 3, "XI TKJ 2": 3,
            "XII TKJ 1": 3, "XII TKJ 2": 3, "XII TKR 1": 3, "XII TKR 2": 3, "XII TSM 1": 3, "XII TSM 2": 3
        },
        "Spreadsheet": {"X AK 1": 2},
        "AK Keuangan": {"XI AK 1": 2}
    },
    24: {
        "Pendidikan Agama Islam": {
            "X AK 1": 2, "X TKJ 1": 2, "X TKR 2": 2, "X TSM 2": 2,
            "XI AK 1": 2, "XI OTKP 1": 2, "XI OTKP 2": 2,
            "XII AK 1": 3, "XII OTKP 1": 2, "XII OTKP 2": 2
        }
    },
    25: {
        "Dasar Jaringan Komputer": {"X TKJ 1": 4, "X TKJ 2": 4},
        "Wide Area Network (WAN)": {"XII TKJ 1": 3, "XII TKJ 2": 3},
        "Teknik Infrastruktur Jaringan": {"XI TKJ 1": 3, "XI TKJ 2": 3},
        "Administrasi Sistem Jaringan": {"XI TKJ 1": 4, "XI TKJ 2": 4, "XII TKJ 1": 4, "XII TKJ 2": 4},
        "Informatika": {"X TKR 1": 3, "X TKR 2": 3, "X TSM 1": 3, "X TSM 2": 3}
    },
    26: {
        "Tek Jaringan Komputer": {"X TKJ 1": 3, "X TKJ 2": 3},
        "Bisnis Teknologi Informasi": {"X TKJ 1": 3, "X TKJ 2": 3},
        "Tek Layanan Jaringan": {"XI TKJ 1": 3, "XI TKJ 2": 3},
        "Wide Area Network (WAN)": {"XI TKJ 1": 3, "XI TKJ 2": 3},
        "Informatika": {"X AK 1": 3, "X OTKP 1": 3, "X OTKP 2": 3, "X TKJ 1": 3, "X TKJ 2": 3}
    },
    27: {
        "Teknologi Perkantoran": {"X OTKP 1": 3, "X OTKP 2": 3},
        "OTK Humas": {"X OTKP 1": 3, "X OTKP 2": 3},
        "OTK Sarpras": {"XI OTKP 1": 2, "XI OTKP 2": 2, "XII OTKP 1": 4, "XII OTKP 2": 4},
        "Kearsipan": {"XI OTKP 1": 2, "XI OTKP 2": 2}
    },
    28: {
        "Bahasa Inggris": {"X TKR 1": 4, "X TKR 2": 4, "X TSM 1": 4, "X TSM 2": 4, "XI TKJ 1": 4, "XI TKJ 2": 4}
    },
    29: {
        "PPKn": {"X TKJ 2": 2, "X TKR 1": 2, "X TKR 2": 2, "X TSM 1": 2, "XII TKR 2": 2, "XII TSM 1": 2, "XII TSM 2": 2},
        "Sejarah Indonesia": {"X AK 1": 2, "X OTKP 1": 2, "X OTKP 2": 2, "X TKJ 1": 2}
    },
    30: {
        "Adm Umum": {"X OTKP 1": 2, "X OTKP 2": 2, "XI AK 1": 2},
        "IPAS": {
            "X AK 1": 2, "X OTKP 1": 2, "X OTKP 2": 2, "X TKJ 1": 2, "X TKJ 2": 2, "X TKR 1": 2, "X TKR 2": 2, "X TSM 1": 2, "X TSM 2": 2
        }
    },
    32: {
        "Komputer Akuntansi": {"X AK 1": 2, "XI AK 1": 2, "XII AK 1": 3}
    },
    33: {
        "Seni Budaya": {c: 2 for c in CLASSES}  # Riska Amelia teaches 2 JP Seni Budaya in all classes
    },
    34: {
        "Bahasa Inggris": {
            "X OTKP 1": 4, "X OTKP 2": 4, "X TKJ 1": 4, "X TKJ 2": 4,
            "XI OTKP 1": 4, "XI OTKP 2": 4,
            "XII TKR 1": 4, "XII TKR 2": 4, "XII TSM 1": 4, "XII TSM 2": 4
        }
    },
    35: {
        "Matematika": {"X AK 1": 5, "X OTKP 1": 5, "X TKJ 1": 5, "X TKJ 2": 5, "XI TKR 1": 5, "XI TKR 2": 5}
    },
    36: {
        "Bahasa Indonesia": {
            "X AK 1": 3, "XI AK 1": 2, "XI TKR 1": 3, "XI TKR 2": 3, "XI TSM 1": 3, "XI TSM 2": 3,
            "XII AK 1": 3, "XII OTKP 1": 3, "XII OTKP 2": 3, "XII TKJ 1": 3, "XII TKJ 2": 3
        }
    },
    37: {
        "TDO": {"X TSM 2": 4},
        "PDTO": {"X TKR 2": 4},
        "K3LH": {"X TKJ 1": 3},
        "Main. Mesin Kendaraan": {"XI TSM 1": 5, "XI TSM 2": 5}
    }
}

def load_curriculum():
    curriculum = {}
    for c in CLASSES:
        if c.startswith("X "):
            cur = {
                "Pendidikan Agama Islam": 2,
                "PPKn": 2,
                "Bahasa Indonesia": 3,
                "Penjasorkes": 2,
                "Sejarah Indonesia": 2,
                "Seni Budaya": 2,
                "Matematika": 5,
                "Bahasa Inggris": 4,
                "Informatika": 3,
                "IPAS": 2
            }
            if "AK" in c:
                cur.update({
                    "Etika Profesi": 2,
                    "K3LH": 2,
                    "Spreadsheet": 2,
                    "Akuntansi Dasar": 3,
                    "Perbankan Dasar": 2,
                    "Komputer Akuntansi": 2
                })
            elif "OTKP" in c:
                cur.update({
                    "K3LH": 2,
                    "Adm Umum": 2,
                    "Teknologi Perkantoran": 3,
                    "Korespondensi": 3,
                    "OTK Humas": 3
                })
            elif "TKJ" in c:
                cur.update({
                    "Tek Jaringan Komputer": 3,
                    "Dasar Jaringan Komputer": 4,
                    "Bisnis Teknologi Informasi": 3,
                    "K3LH": 3
                })
            elif "TKR" in c or "TSM" in c:
                cur.update({
                    "K3LH": 2,
                    "TDO": 4,
                    "PDTO": 4,
                    "Gambar Teknik": 3
                })
            curriculum[c] = cur

        elif c.startswith("XI "):
            cur = {
                "Pendidikan Agama Islam": 2,
                "PPKn": 2,
                "Bahasa Indonesia": 3 if ("TKR" in c or "TSM" in c) else 2,
                "Penjasorkes": 2,
                "Sejarah Indonesia": 2,
                "Seni Budaya": 2,
                "Matematika": 5,
                "Bahasa Inggris": 4
            }
            if "AK" in c:
                cur.update({
                    "Ekonomi Bisnis": 2,
                    "Adm Umum": 2,
                    "Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur": 2,
                    "AK Lembaga": 2,
                    "AK Keuangan": 2,
                    "Komputer Akuntansi": 2,
                    "Adm Pajak": 2,
                    "PKK": 3,
                    "KKA / Coding": 2
                })
            elif "OTKP" in c:
                cur.update({
                    # OTKP has 40 JP total in screenshot, so we need to add 3 JP to make it 40 JP
                    # Let's adjust OTK Humas to 3 JP or add OTK Keuangan = 2, OTK Humas = 3 (we balance it)
                    "Kearsipan": 2,
                    "OTK Kepegawaian": 2,
                    "OTK Keuangan": 2,
                    "OTK Sarpras": 2,
                    "OTK Humas": 3, # Adjusted to 3 to make exactly 40 JP
                    "PKK": 3,
                    "KKA / Coding": 2
                })
            elif "TKJ" in c:
                cur.update({
                    "Wide Area Network (WAN)": 3,
                    "Tek Layanan Jaringan": 3,
                    "Teknik Infrastruktur Jaringan": 3,
                    "Administrasi Sistem Jaringan": 4, # Changed to long name to match DB and qualified
                    "PKK": 3,
                    "KKA / Coding": 2
                })
            elif "TKR" in c:
                cur.update({
                    "PDTO": 4,
                    "Kelistrikan Kendaraan Ringan": 4,
                    "Main. Mesin Kendaraan": 5, # Auto-added to hit 40 JP
                    "PKK": 3,
                    "KKA / Coding": 2
                })
            elif "TSM" in c:
                cur.update({
                    "Main. Mesin Kendaraan": 5,
                    "Kelistrikan Kendaraan": 5,
                    "Main. Sasis Sepeda Motor": 4,
                    "Kelistrikan Sepeda Motor": 4,
                    "PKK": 3,
                    "KKA / Coding": 2
                })
            curriculum[c] = cur

        elif c.startswith("XII "):
            cur = {
                "Pendidikan Agama Islam": 3 if "AK" in c else 2,
                "PPKn": 2,
                "Bahasa Indonesia": 3,
                "Penjasorkes": 2,
                "Sejarah Indonesia": 2,
                "Seni Budaya": 2,
                "Matematika": 5,
                "Bahasa Inggris": 4
            }
            if "AK" in c:
                cur.update({
                    "Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur": 4,
                    "AK Lembaga": 3,
                    "AK Keuangan": 3,
                    "Komputer Akuntansi": 3,
                    "Adm Pajak": 2,
                    "PKK": 3
                })
            elif "OTKP" in c:
                cur.update({
                    "OTK Kepegawaian": 3,
                    "OTK Keuangan": 4,
                    "OTK Sarpras": 4,
                    "OTK Humas": 4,
                    "PKK": 3
                })
            elif "TKJ" in c:
                cur.update({
                    "Wide Area Network (WAN)": 3,
                    "Administrasi Sistem Jaringan": 4,
                    "Teknologi Infrastruktur Jaringan": 4,
                    "Teknologi Layanan Jaringan": 4,
                    "PKK": 3
                })
            elif "TKR" in c:
                cur.update({
                    "Main. Mesin Kendaraan": 5,
                    "Main. Sasis Kendaraan": 5,
                    "Kelistrikan Kendaraan Ringan": 5,
                    "PKK": 3
                })
            elif "TSM" in c:
                cur.update({
                    "Main. Mesin Sepeda Motor": 5,
                    "Main. Sasis Sepeda Motor": 5,
                    "Kelistrikan Sepeda Motor": 5,
                    "PKK": 3
                })
            curriculum[c] = cur

    return curriculum

TEACHER_SUBJECTS_MAP = {
    "Matematika": [2, 4],
    "Penjasorkes": [3, 9, 10],
    "PPKn": [5, 12],
    "PKK": [6, 11],
    "Bahasa Indonesia": [13],
    "Sejarah Indonesia": [11],
    "Ekonomi Bisnis": [7],
    "Akuntansi Dasar": [7],
    "AK Lembaga": [7],
    "Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur": [7],
    "OTK Keuangan": [7],
    "Korespondensi": [8],
    "OTK Humas": [8],
    "Etika Profesi": [11],
    "Perbankan Dasar": [11],
    "AK Keuangan": [23], # Assigned Astri Wulandari (23) for XII AK 1
}

def resolve_teacher(subject, cname, used_load):
    candidates = TEACHER_SUBJECTS_MAP.get(subject, [])
    if not candidates:
        return None
    candidates.sort(key=lambda t: used_load.get(t, 0))
    selected = candidates[0]
    return selected

def main():
    curriculum = load_curriculum()
    allocations = []
    used_load = {t: 0 for t in range(1, 38)}
    
    # Explicit screenshot allocations
    for t_code, mapels in SCREENSHOT_DATA.items():
        for mname, classes in mapels.items():
            for cname, jp in classes.items():
                allocations.append({
                    "class": cname,
                    "subject": mname,
                    "teacher": t_code,
                    "jp": jp
                })
                used_load[t_code] += jp
                
    # Auto-resolve remainders
    for cname in CLASSES:
        cur = curriculum.get(cname, {})
        class_allocs = [a for a in allocations if a["class"] == cname]
        
        for mname, jp in cur.items():
            existing = [a for a in class_allocs if a["subject"] == mname]
            if existing:
                continue
            
            t_code = resolve_teacher(mname, cname, used_load)
            if t_code:
                allocations.append({
                    "class": cname,
                    "subject": mname,
                    "teacher": t_code,
                    "jp": jp
                })
                used_load[t_code] += jp
            else:
                # Fallback: if not mapped, pick first teacher who has qualification in teacher_subjects
                # E.g. for general/religion/etc.
                print(f"Warning: No teacher for {mname} in {cname}")
                
        # Check totals
        class_allocs = [a for a in allocations if a["class"] == cname]
        new_sum = sum(a["jp"] for a in class_allocs)
        if new_sum != 40:
            print(f"Class {cname} sum is {new_sum} JP! Let's check detail:")
            for a in class_allocs:
                print(f"  - {a['subject']}: {a['jp']} JP (Teacher: {a['teacher']})")
                
    # ── STEP C: Generate SQL Script ──
    sql = []
    sql.append("-- ============================================================")
    sql.append("-- SEED DATA: CLASS SUBJECT ALLOCATIONS")
    sql.append("-- ============================================================")
    sql.append("")
    # We will insert XI TKR 2 class dynamically to prevent foreign key errors
    sql.append("INSERT INTO classes (nama_kelas, shift_operasional, tingkat, jurusan)")
    sql.append("VALUES ('XI TKR 2', 'SIANG', 'XI', 'TKR')")
    sql.append("ON CONFLICT (nama_kelas) DO NOTHING;")
    sql.append("")
    sql.append("TRUNCATE TABLE class_subjects CASCADE;")
    sql.append("")
    sql.append("INSERT INTO class_subjects (id_kelas, id_mapel, id_guru, durasi_jp)")
    sql.append("SELECT c.id_kelas, s.id_mapel, t.id_guru, data.durasi_jp")
    sql.append("FROM (VALUES")
    
    values_str = []
    for a in allocations:
        # Match subject name to actual db subject names
        subj_name = a["subject"]
        if subj_name == "Pendidikan Agama Islam":
            # Map PAI to the DB name
            subj_name = "Pendidikan Agama dan Budi Pekerti"
        elif subj_name == "Penjasorkes":
            subj_name = "Pendidikan Jasmani, Olah Raga & Kesehatan"
        elif subj_name == "PPKn":
            subj_name = "Pendidikan Pancasila dan Kewarganegaraan"
            
        subj = subj_name.replace("'", "''")
        val = f"  ('{a['class']}', '{subj}', {a['teacher']}, {a['jp']})"
        values_str.append(val)
        
    sql.append(",\n".join(values_str))
    sql.append(") AS data(nama_kelas, nama_mapel, kode_guru, durasi_jp)")
    sql.append("JOIN classes c ON c.nama_kelas = data.nama_kelas")
    sql.append("JOIN subjects s ON s.nama_mapel = data.nama_mapel")
    sql.append("LEFT JOIN teachers t ON t.kode_guru = data.kode_guru;")
    
    with open("backend/seed_class_subjects.sql", "w", encoding="utf-8") as f:
        f.write("\n".join(sql))
        
    print("\nSQL Seed generated successfully in backend/seed_class_subjects.sql")

if __name__ == "__main__":
    main()
