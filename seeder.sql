-- ============================================================
-- SEEDER.SQL
-- Jalankan di Supabase → SQL Editor
-- Bersifat IDEMPOTENT (ON CONFLICT DO NOTHING)
-- ============================================================

-- ── STEP 1: Pastikan constraint unik pada subjects ────────────
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'subjects_nama_mapel_key'
    ) THEN
        ALTER TABLE subjects ADD CONSTRAINT subjects_nama_mapel_key UNIQUE (nama_mapel);
    END IF;
END
$$;

-- ── STEP 2: Insert mata pelajaran ────────────────────────────
INSERT INTO subjects (nama_mapel, kategori_mapel) VALUES
  ('Matematika',                                                              'UMUM'),
  ('Bahasa Indonesia',                                                        'UMUM'),
  ('Bahasa Inggris',                                                          'UMUM'),
  ('PPKn',                                                                    'UMUM'),
  ('PKK',                                                                     'UMUM'),
  ('Sejarah Indonesia',                                                       'UMUM'),
  ('Etika Profesi',                                                           'UMUM'),
  ('Seni Budaya',                                                             'UMUM'),
  ('Pendidikan Agama Islam',                                                  'UMUM'),
  ('Informatika',                                                             'UMUM'),
  ('IPAS',                                                                    'UMUM'),
  ('Penjasorkes',                                                             'OLAHRAGA'),
  ('Akuntansi Dasar',                                                         'PRODUKTIF'),
  ('Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur',             'PRODUKTIF'),
  ('OTK Keuangan',                                                            'PRODUKTIF'),
  ('AK Lembaga',                                                              'PRODUKTIF'),
  ('Ekonomi Bisnis',                                                          'PRODUKTIF'),
  ('AK Keuangan',                                                             'PRODUKTIF'),
  ('Komputer Akuntansi',                                                      'PRODUKTIF'),
  ('Spreadsheet',                                                             'PRODUKTIF'),
  ('Perbankan Dasar',                                                         'PRODUKTIF'),
  ('Korespondensi',                                                           'PRODUKTIF'),
  ('OTK Humas',                                                               'PRODUKTIF'),
  ('OTK Kepegawaian',                                                         'PRODUKTIF'),
  ('OTK Sarpras',                                                             'PRODUKTIF'),
  ('Teknologi Perkantoran',                                                   'PRODUKTIF'),
  ('Kearsipan',                                                               'PRODUKTIF'),
  ('Adm Pajak',                                                               'PRODUKTIF'),
  ('Adm Umum',                                                                'PRODUKTIF'),
  ('Kelistrikan Kendaraan',                                                   'PRODUKTIF'),
  ('Kelistrikan Kendaraan Ringan',                                            'PRODUKTIF'),
  ('Kelistrikan Sepeda Motor',                                                'PRODUKTIF'),
  ('Main. Mesin Sepeda Motor',                                                'PRODUKTIF'),
  ('Main. Sasis Sepeda Motor',                                                'PRODUKTIF'),
  ('Main. Mesin Kendaraan',                                                   'PRODUKTIF'),
  ('Main. Sasis Kendaraan',                                                   'PRODUKTIF'),
  ('TDO',                                                                     'PRODUKTIF'),
  ('PDTO',                                                                    'PRODUKTIF'),
  ('Gambar Teknik',                                                           'PRODUKTIF'),
  ('K3LH',                                                                    'PRODUKTIF'),
  ('Dasar Jaringan Komputer',                                                 'PRODUKTIF'),
  ('Wide Area Network (WAN)',                                                  'PRODUKTIF'),
  ('Teknik Infrastruktur Jaringan',                                           'PRODUKTIF'),
  ('Adm Sistem Jaringan',                                                     'PRODUKTIF'),
  ('Tek Jaringan Komputer',                                                   'PRODUKTIF'),
  ('Bisnis Teknologi Informasi',                                              'PRODUKTIF'),
  ('Tek Layanan Jaringan',                                                    'PRODUKTIF'),
  ('KKA / Coding',                                                            'PRODUKTIF')
ON CONFLICT (nama_mapel) DO NOTHING;

-- ── STEP 3: Insert/Update guru ────────────────────────────────
-- Clean up old teachers first
DELETE FROM teacher_subjects WHERE id_guru IN (SELECT id_guru FROM teachers WHERE kode_guru NOT IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39));
DELETE FROM teachers WHERE kode_guru NOT IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39);

INSERT INTO teachers (kode_guru, nama_guru, hari_tersedia, shift_pagi, shift_siang, hari_tersedia_pagi, hari_tersedia_siang, no_wa) VALUES
  (1,  'REZA PATRIOTA PUTRA, S.Kom',       '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560001'),
  (2,  'TAMAN SASTRA DIKARNA, S.Pd',       '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560002'),
  (3,  'SUHARNO, S.Pdi',                   '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560003'),
  (4,  'SAMSUL HUDA, S.Pd',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560004'),
  (5,  'AHMAD HUSEN NASUTION, SS',         '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560005'),
  (6,  'WISNU NARA UTAMA, S.Pd',           '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560006'),
  (7,  'FITRI MULYANI, S.Pd',              '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560007'),
  (8,  'DERA ISMAWATI, S.PdI',             '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560008'),
  (9,  'WIDONI SANTOSO, S.Pd',             '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560009'),
  (10, 'SRI TITA MULYATI',                 '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560010'),
  (11, 'EUIS SUPRIHATIN, S.Pd',            '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560011'),
  (12, 'WIDA HARTANI, S.Pd',               '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560012'),
  (13, 'LUTHFI AHMAD NAZHIF, S.Pd',        '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560013'),
  (14, 'WIDJAYANTI, S.Sos',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560014'),
  (15, 'DEDE HIDAYATULLAH',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560015'),
  (16, 'KOKO, ST',                         '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560016'),
  (17, 'CHRISTIN SIREGAR, S.Pd',           '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560017'),
  (18, 'MUHAMMAD SYAFE''I',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560018'),
  (19, 'MUHAMMAD ANDIKA PRAWIRA, S.Kom',   '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560019'),
  (20, 'YULISTIO HARDIYANTO, ST',          '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560020'),
  (21, 'KUAT SUPARTO, ST',                 '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560021'),
  (22, 'ASTRI WULANDARI, S.Ak',            '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560022'),
  (23, 'AGUNG AINUL HAKIM',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560023'),
  (24, 'SUTRISNO',                         '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560024'),
  (25, 'MUHAMMAD ALBAR SAPIN',             '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560025'),
  (26, 'TIARA SHANTI HARTONO, S.Sos',      '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560026'),
  (27, 'OKTARI QOMIMIS SYATUN, S.Pd',      '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560027'),
  (28, 'CATUR WULANDARI, A.Md',            '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560028'),
  (29, 'DWIANA RIKASARI, S.Ap',            '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560029'),
  (30, 'IDAYATUL MUSTAFIDAH',              '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560030'),
  (31, 'RISKA AMELIA, S.M',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560031'),
  (32, 'SISTER NINDA PUTRI, S.Pd',         '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560032'),
  (33, 'DELA AMELIA PUTRI, S.Pd',          '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560033'),
  (34, 'WIWIK UMAYAH, S.Pd',               '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560034'),
  (35, 'ENDANG KURNIAWAN, ST',             '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560035'),
  (36, 'SEPTIANI RAKA SIWI, M.Pd',         '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560036'),
  (37, 'FAUZI, S.Kom',                     '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560037'),
  (38, 'AZMIRAL AZIS, S.Pd',               '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560038'),
  (39, 'RAIHAN NABILA SYIFA, S.Pd',        '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '081234560039')
ON CONFLICT (kode_guru) DO UPDATE SET
  nama_guru = EXCLUDED.nama_guru,
  no_wa = EXCLUDED.no_wa;

-- ── STEP 4: Insert relasi guru ↔ mata pelajaran ──────────────
-- Menggunakan subquery untuk lookup id_guru dan id_mapel by name/kode

INSERT INTO teacher_subjects (id_guru, id_mapel)
SELECT t.id_guru, s.id_mapel
FROM (VALUES
  -- kode_guru=2: Taman Sastra Dikarna
  (2, 'Matematika'),
  -- kode_guru=3: Suharno
  (3, 'Penjasorkes'),
  -- kode_guru=4: Samsul Huda
  (4, 'Matematika'),
  -- kode_guru=5: Ahmad Husen Nasution
  (5, 'PPKn'),
  -- kode_guru=6: Wisnu Nara Utama
  (6, 'PKK'),
  -- kode_guru=7: Fitri Mulyani
  (7, 'Akuntansi Dasar'),
  (7, 'Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur'),
  (7, 'OTK Keuangan'),
  (7, 'AK Lembaga'),
  (7, 'Ekonomi Bisnis'),
  -- kode_guru=8: Dera Ismawati
  (8, 'Korespondensi'),
  (8, 'OTK Humas'),
  -- kode_guru=9: Widoni Santoso
  (9, 'Penjasorkes'),
  -- kode_guru=10: Sri Tita Mulyati
  (10, 'Penjasorkes'),
  -- kode_guru=11: Euis Suprihatin
  (11, 'Sejarah Indonesia'),
  (11, 'Etika Profesi'),
  (11, 'Perbankan Dasar'),
  (11, 'PKK'),
  -- kode_guru=12: Wida Hartani
  (12, 'PPKn'),
  -- kode_guru=13: Luthfi Ahmad Nazhif
  (13, 'Bahasa Indonesia'),
  -- kode_guru=14: Widjayanti
  (14, 'OTK Kepegawaian'),
  (14, 'Adm Pajak'),
  -- kode_guru=15: Dede Hidayatullah
  (15, 'Matematika'),
  -- kode_guru=16: Koko, ST
  (16, 'Kelistrikan Kendaraan'),
  (16, 'Main. Mesin Sepeda Motor'),
  (16, 'TDO'),
  (16, 'PDTO'),
  (16, 'Main. Sasis Sepeda Motor'),
  (16, 'Kelistrikan Sepeda Motor'),
  -- kode_guru=17: Christin Siregar
  (17, 'Bahasa Inggris'),
  -- kode_guru=18: Muhammad Syafe''I
  (18, 'Pendidikan Agama Islam'),
  -- kode_guru=19: M. Andika Prawira, S.Kom
  (19, 'Teknik Infrastruktur Jaringan'),
  (19, 'KKA / Coding'),
  (19, 'Tek Layanan Jaringan'),
  -- kode_guru=20: Yulistio Hardiyanto, ST
  (20, 'Main. Mesin Kendaraan'),
  (20, 'Main. Sasis Kendaraan'),
  (20, 'PDTO'),
  (20, 'TDO'),
  (20, 'Main. Sasis Sepeda Motor'),
  (20, 'Kelistrikan Kendaraan Ringan'),
  -- kode_guru=21: Kuat Suparto, ST
  (21, 'Gambar Teknik'),
  (21, 'TDO'),
  (21, 'K3LH'),
  (21, 'PDTO'),
  -- kode_guru=22: Astri Wulandari, S.Ak
  (22, 'Bahasa Indonesia'),
  (22, 'Spreadsheet'),
  (22, 'AK Keuangan'),
  -- kode_guru=23: Agung Ainul Hakim
  (23, 'Dasar Jaringan Komputer'),
  (23, 'Wide Area Network (WAN)'),
  (23, 'Teknik Infrastruktur Jaringan'),
  (23, 'Adm Sistem Jaringan'),
  (23, 'Informatika'),
  -- kode_guru=24: Sutrisno
  (24, 'Tek Jaringan Komputer'),
  (24, 'Bisnis Teknologi Informasi'),
  (24, 'Tek Layanan Jaringan'),
  (24, 'Wide Area Network (WAN)'),
  (24, 'Informatika'),
  -- kode_guru=25: Muhammad Albar Sapin, SM
  (25, 'Teknologi Perkantoran'),
  (25, 'OTK Humas'),
  (25, 'OTK Sarpras'),
  (25, 'Kearsipan'),
  -- kode_guru=26: Tiara Shanti Hartono, S.Sos
  (26, 'Bahasa Inggris'),
  -- kode_guru=27: Oktari Qomimis Syatun, S.Pd
  (27, 'PPKn'),
  (27, 'Sejarah Indonesia'),
  -- kode_guru=28: Catur Wulandari, A.Md
  (28, 'Adm Umum'),
  (28, 'IPAS'),
  -- kode_guru=30: Idayatul Mustafidah, SE
  (30, 'Komputer Akuntansi'),
  -- kode_guru=31: Riska Amelia, S.M
  (31, 'Seni Budaya'),
  -- kode_guru=32: Sister Ninda Putri, S.Pd
  (32, 'Bahasa Inggris'),
  -- kode_guru=33: Dela Amelia Putri, S.Pd
  (33, 'Matematika'),
  -- kode_guru=34: Wiwik Umayah, S.Pd
  (34, 'Bahasa Indonesia'),
  -- kode_guru=35: Endang Kurniawan, ST
  (35, 'TDO'),
  (35, 'PDTO'),
  (35, 'K3LH'),
  (35, 'Main. Mesin Kendaraan')
) AS data(kode_guru, nama_mapel)
JOIN teachers t ON t.kode_guru = data.kode_guru
JOIN subjects s ON s.nama_mapel = data.nama_mapel
ON CONFLICT (id_guru, id_mapel) DO NOTHING;

-- ── SELESAI ──────────────────────────────────────────────────
SELECT
  'subjects' AS tabel, COUNT(*) AS total FROM subjects
UNION ALL
SELECT 'teachers', COUNT(*) FROM teachers
UNION ALL
SELECT 'teacher_subjects', COUNT(*) FROM teacher_subjects;
