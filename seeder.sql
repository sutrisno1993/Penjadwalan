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

-- ── STEP 3: Insert guru ──────────────────────────────────────
INSERT INTO teachers (kode_guru, nama_guru, hari_tersedia, shift_pagi, shift_siang, hari_tersedia_pagi, hari_tersedia_siang) VALUES
  (1,  'REZA PATRIOTA PUTRA, S.Kom',       '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (2,  'TAMAN SASTRA DIKARNA, S.Pd',       '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (3,  'SUHARNO, S.Pdi',                   '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (4,  'SAMSUL HUDA, S.Pd',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (5,  'AHMAD HUSEN NASUTION, SS',         '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (6,  'WISNU NARA UTAMA, S.Pd',           '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (7,  'FITRI MULYANI, S.Pd',              '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (8,  'DERA ISMAWATI, S.PdI',             '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (9,  'WIDONI SANTOSO, S.Pd',             '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (10, 'SRI TITA MULYATI',                 '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (11, 'EUIS SUPRIHATIN, S.Pd',            '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (12, 'WIDA HARTANI, S.Pd',               '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (13, 'LUTHFI AHMAD NAZHIF, S.Pd',        '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (14, 'WIDJAYANTI, S.Sos',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (15, 'DEDE HIDAYATULLAH',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (16, 'KOKO',                             '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (17, 'CHRISTIN SIREGAR, S.Pd',           '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (18, 'Muhammad Syafe''i',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (19, 'Muhammad Andika Prawira',          '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (20, 'Dra. Sri Chandri Yani',            '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (21, 'Yulistio',                         '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (22, 'Kuat Suparto',                     '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (23, 'Astri Wulandari',                  '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (24, 'Arief Akbar Fadillah',             '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (25, 'Agung Ainul Hakim',                '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (26, 'Sutrisno',                         '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (27, 'Muhammad Albar Sapin',             '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (28, 'Tiara Shanti Hartono, S.Sos',      '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (29, 'Oktari Qomimis Syatun, S.Pd',      '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (30, 'Catur Wulandari',                  '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (31, 'Dwiana Rikasari, S.Ap',            '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (32, 'IDAYATUL MUSTAFIDAH',              '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (33, 'RISKA AMELIA, S.M',               '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (34, 'SISTER NINDA PUTRI, S.Pd',        '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (35, 'DELA AMELIA PUTRI, S.Pd',         '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (36, 'WIWIK UMAYAH, S.Pd',              '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'),
  (37, 'ENDANG KURNIAWAN, ST',            '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', TRUE, TRUE, '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]', '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]')
ON CONFLICT (kode_guru) DO NOTHING;

-- ── STEP 4: Insert relasi guru ↔ mata pelajaran ──────────────
-- Menggunakan subquery untuk lookup id_guru dan id_mapel by name/kode

INSERT INTO teacher_subjects (id_guru, id_mapel)
SELECT t.id_guru, s.id_mapel
FROM (VALUES
  -- kode_guru=2: TAMAN SASTRA DIKARNA
  (2, 'Matematika'),
  -- kode_guru=3: SUHARNO
  (3, 'Penjasorkes'),
  -- kode_guru=4: SAMSUL HUDA
  (4, 'Matematika'),
  -- kode_guru=5: AHMAD HUSEN NASUTION
  (5, 'PPKn'),
  -- kode_guru=6: WISNU NARA UTAMA
  (6, 'PKK'),
  -- kode_guru=7: FITRI MULYANI
  (7, 'Akuntansi Dasar'),
  (7, 'Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur'),
  (7, 'OTK Keuangan'),
  (7, 'AK Lembaga'),
  (7, 'Ekonomi Bisnis'),
  -- kode_guru=8: DERA ISMAWATI
  (8, 'Korespondensi'),
  (8, 'OTK Humas'),
  -- kode_guru=9: WIDONI SANTOSO
  (9, 'Penjasorkes'),
  -- kode_guru=10: SRI TITA MULYATI
  (10, 'Penjasorkes'),
  -- kode_guru=11: EUIS SUPRIHATIN
  (11, 'Sejarah Indonesia'),
  (11, 'Etika Profesi'),
  (11, 'Perbankan Dasar'),
  (11, 'PKK'),
  -- kode_guru=12: WIDA HARTANI
  (12, 'PPKn'),
  -- kode_guru=13: LUTHFI AHMAD NAZHIF
  (13, 'Bahasa Indonesia'),
  -- kode_guru=14: WIDJAYANTI
  (14, 'OTK Kepegawaian'),
  (14, 'Adm Pajak'),
  -- kode_guru=15: DEDE HIDAYATULLAH
  (15, 'Matematika'),
  -- kode_guru=16: KOKO
  (16, 'Kelistrikan Kendaraan'),
  (16, 'Main. Mesin Sepeda Motor'),
  (16, 'TDO'),
  (16, 'PDTO'),
  (16, 'Main. Sasis Sepeda Motor'),
  (16, 'Kelistrikan Sepeda Motor'),
  -- kode_guru=17: CHRISTIN SIREGAR
  (17, 'Bahasa Inggris'),
  -- kode_guru=18: Muhammad Syafe'i
  (18, 'Pendidikan Agama Islam'),
  -- kode_guru=19: Muhammad Andika Prawira
  (19, 'Teknik Infrastruktur Jaringan'),
  (19, 'KKA / Coding'),
  (19, 'Tek Layanan Jaringan'),
  -- kode_guru=20: Dra. Sri Chandri Yani
  (20, 'Sejarah Indonesia'),
  -- kode_guru=21: Yulistio
  (21, 'Main. Mesin Kendaraan'),
  (21, 'Main. Sasis Kendaraan'),
  (21, 'PDTO'),
  (21, 'TDO'),
  (21, 'Main. Sasis Sepeda Motor'),
  (21, 'Kelistrikan Kendaraan Ringan'),
  -- kode_guru=22: Kuat Suparto
  (22, 'Gambar Teknik'),
  (22, 'TDO'),
  (22, 'K3LH'),
  (22, 'PDTO'),
  -- kode_guru=23: Astri Wulandari
  (23, 'Bahasa Indonesia'),
  (23, 'Spreadsheet'),
  (23, 'AK Keuangan'),
  -- kode_guru=24: Arief Akbar Fadillah
  (24, 'Pendidikan Agama Islam'),
  -- kode_guru=25: Agung Ainul Hakim
  (25, 'Dasar Jaringan Komputer'),
  (25, 'Wide Area Network (WAN)'),
  (25, 'Teknik Infrastruktur Jaringan'),
  (25, 'Adm Sistem Jaringan'),
  (25, 'Informatika'),
  -- kode_guru=26: Sutrisno
  (26, 'Tek Jaringan Komputer'),
  (26, 'Bisnis Teknologi Informasi'),
  (26, 'Tek Layanan Jaringan'),
  (26, 'Wide Area Network (WAN)'),
  (26, 'Informatika'),
  -- kode_guru=27: Muhammad Albar Sapin
  (27, 'Teknologi Perkantoran'),
  (27, 'OTK Humas'),
  (27, 'OTK Sarpras'),
  (27, 'Kearsipan'),
  -- kode_guru=28: Tiara Shanti Hartono
  (28, 'Bahasa Inggris'),
  -- kode_guru=29: Oktari Qomimis Syatun
  (29, 'PPKn'),
  (29, 'Sejarah Indonesia'),
  -- kode_guru=30: Catur Wulandari
  (30, 'Adm Umum'),
  (30, 'IPAS'),
  -- kode_guru=32: IDAYATUL MUSTAFIDAH
  (32, 'Komputer Akuntansi'),
  -- kode_guru=33: RISKA AMELIA
  (33, 'Seni Budaya'),
  -- kode_guru=34: SISTER NINDA PUTRI
  (34, 'Bahasa Inggris'),
  -- kode_guru=35: DELA AMELIA PUTRI
  (35, 'Matematika'),
  -- kode_guru=36: WIWIK UMAYAH
  (36, 'Bahasa Indonesia'),
  -- kode_guru=37: ENDANG KURNIAWAN
  (37, 'TDO'),
  (37, 'PDTO'),
  (37, 'K3LH'),
  (37, 'Main. Mesin Kendaraan')
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
