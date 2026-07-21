-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 20 Jul 2026 pada 05.34
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `jadwal_bekasi`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `cache`
--

CREATE TABLE `cache` (
  `key` varchar(255) NOT NULL,
  `value` mediumtext NOT NULL,
  `expiration` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `cache_locks`
--

CREATE TABLE `cache_locks` (
  `key` varchar(255) NOT NULL,
  `owner` varchar(255) NOT NULL,
  `expiration` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `classes`
--

CREATE TABLE `classes` (
  `id_kelas` bigint(20) UNSIGNED NOT NULL,
  `nama_kelas` varchar(255) NOT NULL,
  `shift_operasional` enum('PAGI','SIANG') NOT NULL,
  `tingkat` varchar(255) DEFAULT NULL,
  `jurusan` varchar(255) DEFAULT NULL,
  `id_guru_wali` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `classes`
--

INSERT INTO `classes` (`id_kelas`, `nama_kelas`, `shift_operasional`, `tingkat`, `jurusan`, `id_guru_wali`, `created_at`, `updated_at`) VALUES
(1, 'X AKL 1', 'PAGI', 'X', 'AKL', NULL, NULL, NULL),
(2, 'X OTKP 1', 'PAGI', 'X', 'OTKP', NULL, NULL, NULL),
(3, 'X OTKP 2', 'SIANG', 'X', 'OTKP', NULL, NULL, NULL),
(4, 'X TBSM 1', 'PAGI', 'X', 'TBSM', NULL, NULL, NULL),
(5, 'X TBSM 2', 'SIANG', 'X', 'TBSM', NULL, NULL, NULL),
(6, 'X TKJ 1', 'PAGI', 'X', 'TKJ', NULL, NULL, NULL),
(7, 'X TKJ 2', 'SIANG', 'X', 'TKJ', NULL, NULL, NULL),
(8, 'X TKRO 1', 'PAGI', 'X', 'TKRO', NULL, NULL, NULL),
(9, 'X TKRO 2', 'SIANG', 'X', 'TKRO', NULL, NULL, NULL),
(10, 'XI AKL 1', 'SIANG', 'XI', 'AKL', NULL, NULL, NULL),
(11, 'XI OTKP 1', 'SIANG', 'XI', 'OTKP', NULL, NULL, NULL),
(12, 'XI OTKP 2', 'SIANG', 'XI', 'OTKP', NULL, NULL, NULL),
(13, 'XI TBSM 1', 'SIANG', 'XI', 'TBSM', NULL, NULL, NULL),
(14, 'XI TBSM 2', 'SIANG', 'XI', 'TBSM', NULL, NULL, NULL),
(15, 'XI TKJ 1', 'SIANG', 'XI', 'TKJ', NULL, NULL, NULL),
(16, 'XI TKJ 2', 'SIANG', 'XI', 'TKJ', NULL, NULL, NULL),
(17, 'XI TKRO 1', 'SIANG', 'XI', 'TKRO', NULL, NULL, NULL),
(18, 'XII AKL 1', 'PAGI', 'XII', 'AKL', NULL, NULL, NULL),
(19, 'XII OTKP 1', 'PAGI', 'XII', 'OTKP', NULL, NULL, NULL),
(20, 'XII OTKP 2', 'PAGI', 'XII', 'OTKP', NULL, NULL, NULL),
(21, 'XII TBSM 1', 'PAGI', 'XII', 'TBSM', NULL, NULL, NULL),
(22, 'XII TBSM 2', 'PAGI', 'XII', 'TBSM', NULL, NULL, NULL),
(23, 'XII TKJ 1', 'PAGI', 'XII', 'TKJ', NULL, NULL, NULL),
(24, 'XII TKJ 2', 'PAGI', 'XII', 'TKJ', NULL, NULL, NULL),
(25, 'XII TKRO 1', 'PAGI', 'XII', 'TKRO', NULL, NULL, NULL),
(26, 'XII TKRO 2', 'PAGI', 'XII', 'TKRO', NULL, NULL, NULL),
(68, 'XI TKRO 2', 'SIANG', 'XI', 'TKRO', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `class_subjects`
--

CREATE TABLE `class_subjects` (
  `id_class_subject` bigint(20) UNSIGNED NOT NULL,
  `id_kelas` bigint(20) UNSIGNED NOT NULL,
  `id_mapel` bigint(20) UNSIGNED NOT NULL,
  `durasi_jp` int(11) NOT NULL,
  `id_guru_mutlak` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `class_subjects`
--

INSERT INTO `class_subjects` (`id_class_subject`, `id_kelas`, `id_mapel`, `durasi_jp`, `id_guru_mutlak`, `created_at`, `updated_at`) VALUES
(1, 11, 25, 2, 14, NULL, NULL),
(3, 19, 25, 2, 14, NULL, NULL),
(5, 10, 29, 2, 14, NULL, NULL),
(6, 18, 29, 2, 14, NULL, NULL),
(8, 8, 1, 5, 33, NULL, NULL),
(9, 9, 1, 5, 15, NULL, NULL),
(10, 4, 1, 5, 15, NULL, NULL),
(12, 10, 1, 5, 2, NULL, NULL),
(13, 13, 1, 5, 15, NULL, NULL),
(15, 18, 1, 5, 2, NULL, NULL),
(16, 23, 1, 5, 2, NULL, NULL),
(17, 24, 1, 5, 2, NULL, NULL),
(18, 25, 1, 5, 4, NULL, NULL),
(19, 26, 1, 5, 4, NULL, NULL),
(20, 13, 34, 5, 35, NULL, NULL),
(22, 21, 34, 5, 20, NULL, NULL),
(23, 22, 34, 5, 20, NULL, NULL),
(24, 8, 38, 4, 16, NULL, NULL),
(25, 13, 35, 4, 20, NULL, NULL),
(27, 21, 35, 5, 16, NULL, NULL),
(28, 22, 35, 5, 16, NULL, NULL),
(29, 13, 33, 4, 16, NULL, NULL),
(31, 21, 33, 5, 35, NULL, NULL),
(32, 22, 33, 5, 35, NULL, NULL),
(33, 1, 3, 4, 32, NULL, NULL),
(34, 17, 3, 4, 17, NULL, NULL),
(35, 13, 3, 4, 17, NULL, NULL),
(37, 18, 3, 4, 17, NULL, NULL),
(38, 19, 3, 4, 17, NULL, NULL),
(40, 23, 3, 4, 17, NULL, NULL),
(41, 24, 3, 4, 17, NULL, NULL),
(42, 2, 9, 2, 18, NULL, NULL),
(43, 7, 9, 2, 38, NULL, NULL),
(44, 8, 9, 2, 18, NULL, NULL),
(45, 15, 9, 2, 18, NULL, NULL),
(46, 16, 9, 2, 18, NULL, NULL),
(47, 17, 9, 2, 38, NULL, NULL),
(48, 13, 9, 2, 38, NULL, NULL),
(50, 23, 9, 2, 38, NULL, NULL),
(51, 24, 9, 2, 38, NULL, NULL),
(52, 25, 9, 2, 18, NULL, NULL),
(53, 26, 9, 2, 18, NULL, NULL),
(54, 21, 9, 2, 18, NULL, NULL),
(55, 22, 9, 2, 18, NULL, NULL),
(56, 23, 44, 4, 19, NULL, NULL),
(57, 24, 44, 4, 19, NULL, NULL),
(58, 10, 12, 2, 19, NULL, NULL),
(59, 11, 12, 2, 19, NULL, NULL),
(61, 15, 12, 2, 19, NULL, NULL),
(62, 16, 12, 2, 19, NULL, NULL),
(63, 17, 12, 2, 19, NULL, NULL),
(64, 13, 12, 2, 19, NULL, NULL),
(66, 23, 48, 4, 19, NULL, NULL),
(67, 24, 48, 4, 24, NULL, NULL),
(68, 7, 6, 2, 30, NULL, NULL),
(69, 8, 6, 2, 30, NULL, NULL),
(70, 9, 6, 2, 30, NULL, NULL),
(71, 17, 6, 2, 31, NULL, NULL),
(72, 13, 6, 2, 30, NULL, NULL),
(74, 25, 6, 2, 30, NULL, NULL),
(75, 26, 6, 2, 30, NULL, NULL),
(76, 21, 6, 2, 31, NULL, NULL),
(77, 22, 6, 2, 31, NULL, NULL),
(78, 25, 36, 5, 20, NULL, NULL),
(79, 26, 36, 5, 20, NULL, NULL),
(80, 25, 37, 5, 16, NULL, NULL),
(81, 26, 37, 5, 16, NULL, NULL),
(82, 8, 39, 4, 20, NULL, NULL),
(84, 4, 38, 4, 35, NULL, NULL),
(85, 17, 32, 4, 20, NULL, NULL),
(86, 25, 32, 5, 16, NULL, NULL),
(87, 26, 32, 5, 16, NULL, NULL),
(88, 8, 40, 3, 21, NULL, NULL),
(89, 9, 40, 3, 21, NULL, NULL),
(90, 4, 40, 3, 21, NULL, NULL),
(92, 9, 38, 4, 16, NULL, NULL),
(93, 1, 41, 2, 21, NULL, NULL),
(94, 2, 41, 2, 21, NULL, NULL),
(96, 7, 41, 3, 21, NULL, NULL),
(97, 8, 41, 2, 21, NULL, NULL),
(98, 9, 41, 2, 21, NULL, NULL),
(99, 4, 41, 2, 21, NULL, NULL),
(101, 4, 39, 4, 16, NULL, NULL),
(102, 2, 2, 3, 22, NULL, NULL),
(103, 6, 2, 3, 22, NULL, NULL),
(104, 8, 2, 3, 22, NULL, NULL),
(105, 4, 2, 3, 34, NULL, NULL),
(106, 11, 2, 3, 22, NULL, NULL),
(108, 15, 2, 3, 22, NULL, NULL),
(109, 16, 2, 3, 22, NULL, NULL),
(110, 23, 2, 3, 34, NULL, NULL),
(111, 24, 2, 3, 34, NULL, NULL),
(112, 25, 2, 3, 22, NULL, NULL),
(113, 26, 2, 3, 22, NULL, NULL),
(114, 21, 2, 3, 22, NULL, NULL),
(115, 22, 2, 3, 22, NULL, NULL),
(116, 1, 21, 2, 37, NULL, NULL),
(117, 10, 19, 2, 22, NULL, NULL),
(118, 1, 9, 2, 18, NULL, NULL),
(119, 6, 9, 2, 18, NULL, NULL),
(120, 9, 9, 2, 38, NULL, NULL),
(122, 10, 9, 2, 18, NULL, NULL),
(123, 11, 9, 2, 18, NULL, NULL),
(125, 18, 9, 2, 18, NULL, NULL),
(126, 19, 9, 2, 38, NULL, NULL),
(128, 6, 42, 4, 23, NULL, NULL),
(129, 7, 42, 4, 23, NULL, NULL),
(130, 23, 43, 3, 23, NULL, NULL),
(131, 24, 43, 3, 23, NULL, NULL),
(132, 15, 44, 3, 23, NULL, NULL),
(133, 16, 44, 3, 23, NULL, NULL),
(134, 15, 45, 4, 23, NULL, NULL),
(135, 16, 45, 4, 23, NULL, NULL),
(136, 23, 45, 4, 23, NULL, NULL),
(137, 24, 45, 4, 23, NULL, NULL),
(138, 8, 10, 3, 37, NULL, NULL),
(139, 9, 10, 3, 37, NULL, NULL),
(140, 4, 10, 3, 23, NULL, NULL),
(142, 6, 46, 3, 24, NULL, NULL),
(143, 7, 46, 3, 24, NULL, NULL),
(144, 6, 47, 3, 24, NULL, NULL),
(145, 7, 47, 3, 24, NULL, NULL),
(146, 15, 48, 3, 24, NULL, NULL),
(147, 16, 48, 3, 24, NULL, NULL),
(148, 15, 43, 3, 24, NULL, NULL),
(149, 16, 43, 3, 24, NULL, NULL),
(150, 1, 10, 3, 37, NULL, NULL),
(151, 2, 10, 3, 24, NULL, NULL),
(153, 6, 10, 3, 37, NULL, NULL),
(154, 7, 10, 3, 37, NULL, NULL),
(155, 2, 27, 3, 25, NULL, NULL),
(157, 2, 24, 3, 25, NULL, NULL),
(159, 11, 26, 2, 25, NULL, NULL),
(161, 19, 26, 2, 25, NULL, NULL),
(163, 11, 28, 2, 25, NULL, NULL),
(165, 8, 3, 4, 26, NULL, NULL),
(166, 9, 3, 4, 26, NULL, NULL),
(167, 4, 3, 4, 26, NULL, NULL),
(169, 15, 3, 4, 26, NULL, NULL),
(170, 16, 3, 4, 26, NULL, NULL),
(171, 7, 4, 2, 5, NULL, NULL),
(172, 8, 4, 2, 12, NULL, NULL),
(173, 9, 4, 2, 12, NULL, NULL),
(174, 4, 4, 2, 27, NULL, NULL),
(175, 26, 4, 2, 27, NULL, NULL),
(176, 21, 4, 2, 27, NULL, NULL),
(177, 22, 4, 2, 27, NULL, NULL),
(178, 1, 6, 2, 30, NULL, NULL),
(179, 2, 6, 2, 11, NULL, NULL),
(181, 6, 6, 2, 30, NULL, NULL),
(182, 2, 30, 2, 28, NULL, NULL),
(184, 10, 30, 2, 28, NULL, NULL),
(185, 1, 11, 2, 28, NULL, NULL),
(186, 2, 11, 2, 28, NULL, NULL),
(188, 6, 11, 2, 28, NULL, NULL),
(189, 7, 11, 2, 28, NULL, NULL),
(190, 8, 11, 2, 28, NULL, NULL),
(191, 9, 11, 2, 28, NULL, NULL),
(192, 4, 11, 2, 28, NULL, NULL),
(194, 1, 20, 2, 30, NULL, NULL),
(195, 10, 20, 2, 30, NULL, NULL),
(196, 18, 20, 3, 30, NULL, NULL),
(197, 1, 8, 2, 39, NULL, NULL),
(198, 2, 8, 2, 39, NULL, NULL),
(200, 6, 8, 2, 39, NULL, NULL),
(201, 7, 8, 2, 39, NULL, NULL),
(202, 8, 8, 2, 31, NULL, NULL),
(203, 9, 8, 2, 31, NULL, NULL),
(204, 4, 8, 2, 31, NULL, NULL),
(206, 10, 8, 2, 31, NULL, NULL),
(207, 11, 8, 2, 31, NULL, NULL),
(209, 15, 8, 2, 31, NULL, NULL),
(210, 16, 8, 2, 31, NULL, NULL),
(211, 17, 8, 2, 31, NULL, NULL),
(212, 13, 8, 2, 31, NULL, NULL),
(214, 18, 8, 2, 39, NULL, NULL),
(215, 19, 8, 2, 31, NULL, NULL),
(217, 23, 8, 2, 31, NULL, NULL),
(218, 24, 8, 2, 31, NULL, NULL),
(219, 25, 8, 2, 31, NULL, NULL),
(220, 26, 8, 2, 31, NULL, NULL),
(221, 21, 8, 2, 31, NULL, NULL),
(222, 22, 8, 2, 31, NULL, NULL),
(223, 2, 3, 4, 32, NULL, NULL),
(225, 6, 3, 4, 32, NULL, NULL),
(226, 7, 3, 4, 32, NULL, NULL),
(227, 11, 3, 4, 32, NULL, NULL),
(229, 25, 3, 4, 32, NULL, NULL),
(230, 26, 3, 4, 32, NULL, NULL),
(231, 21, 3, 4, 32, NULL, NULL),
(232, 22, 3, 4, 32, NULL, NULL),
(233, 1, 1, 5, 33, NULL, NULL),
(234, 2, 1, 5, 33, NULL, NULL),
(235, 6, 1, 5, 15, NULL, NULL),
(236, 7, 1, 5, 15, NULL, NULL),
(237, 17, 1, 5, 33, NULL, NULL),
(238, 1, 2, 3, 22, NULL, NULL),
(239, 10, 2, 2, 13, NULL, NULL),
(240, 17, 2, 3, 13, NULL, NULL),
(241, 13, 2, 3, 34, NULL, NULL),
(243, 18, 2, 3, 34, NULL, NULL),
(244, 19, 2, 3, 34, NULL, NULL),
(247, 9, 39, 4, 20, NULL, NULL),
(248, 6, 41, 3, 21, NULL, NULL),
(251, 1, 4, 2, 12, NULL, NULL),
(252, 1, 13, 2, 9, NULL, NULL),
(253, 1, 7, 2, 11, NULL, NULL),
(254, 1, 14, 3, 7, NULL, NULL),
(255, 1, 22, 2, 11, NULL, NULL),
(256, 2, 4, 2, 5, NULL, NULL),
(257, 2, 13, 2, 10, NULL, NULL),
(258, 2, 23, 3, 8, NULL, NULL),
(263, 6, 4, 2, 12, NULL, NULL),
(264, 6, 13, 2, 10, NULL, NULL),
(265, 7, 2, 3, 22, NULL, NULL),
(266, 7, 13, 2, 10, NULL, NULL),
(267, 8, 13, 2, 9, NULL, NULL),
(268, 9, 2, 3, 22, NULL, NULL),
(269, 9, 13, 2, 9, NULL, NULL),
(270, 4, 13, 2, 9, NULL, NULL),
(271, 4, 6, 2, 31, NULL, NULL),
(276, 10, 4, 2, 5, NULL, NULL),
(277, 10, 13, 2, 3, NULL, NULL),
(278, 10, 6, 2, 11, NULL, NULL),
(279, 10, 18, 2, 7, NULL, NULL),
(280, 10, 15, 2, 7, NULL, NULL),
(281, 10, 17, 2, 7, NULL, NULL),
(282, 10, 5, 3, 37, NULL, NULL),
(283, 11, 4, 2, 5, NULL, NULL),
(284, 11, 13, 2, 3, NULL, NULL),
(285, 11, 6, 2, 11, NULL, NULL),
(286, 11, 1, 5, 4, NULL, NULL),
(287, 11, 16, 3, 7, NULL, NULL),
(288, 11, 24, 4, 8, NULL, NULL),
(289, 11, 5, 3, 6, NULL, NULL),
(297, 15, 4, 2, 27, NULL, NULL),
(298, 15, 13, 2, 10, NULL, NULL),
(299, 15, 6, 2, 11, NULL, NULL),
(300, 15, 1, 5, 2, NULL, NULL),
(301, 15, 5, 3, 11, NULL, NULL),
(302, 16, 4, 2, 27, NULL, NULL),
(303, 16, 13, 2, 10, NULL, NULL),
(304, 16, 6, 2, 11, NULL, NULL),
(305, 16, 1, 5, 2, NULL, NULL),
(306, 16, 5, 3, 11, NULL, NULL),
(307, 17, 4, 2, 12, NULL, NULL),
(308, 17, 13, 2, 10, NULL, NULL),
(309, 17, 5, 3, 11, NULL, NULL),
(310, 13, 4, 2, 12, NULL, NULL),
(311, 13, 13, 2, 9, NULL, NULL),
(312, 13, 5, 3, 6, NULL, NULL),
(316, 18, 4, 2, 5, NULL, NULL),
(317, 18, 13, 2, 3, NULL, NULL),
(318, 18, 6, 2, 31, NULL, NULL),
(319, 18, 15, 4, 7, NULL, NULL),
(320, 18, 17, 2, 7, NULL, NULL),
(321, 18, 19, 2, 22, NULL, NULL),
(322, 18, 5, 3, 6, NULL, NULL),
(323, 19, 4, 2, 5, NULL, NULL),
(324, 19, 13, 2, 3, NULL, NULL),
(325, 19, 6, 2, 30, NULL, NULL),
(326, 19, 1, 5, 15, NULL, NULL),
(327, 19, 16, 3, 7, NULL, NULL),
(328, 19, 24, 4, 8, NULL, NULL),
(329, 19, 5, 3, 11, NULL, NULL),
(337, 23, 4, 2, 5, NULL, NULL),
(338, 23, 13, 2, 9, NULL, NULL),
(339, 23, 6, 2, 27, NULL, NULL),
(340, 23, 5, 3, 11, NULL, NULL),
(341, 24, 4, 2, 5, NULL, NULL),
(342, 24, 13, 2, 9, NULL, NULL),
(343, 24, 6, 2, 27, NULL, NULL),
(344, 24, 5, 3, 11, NULL, NULL),
(345, 25, 4, 2, 27, NULL, NULL),
(346, 25, 13, 2, 10, NULL, NULL),
(347, 25, 5, 3, 6, NULL, NULL),
(348, 26, 13, 2, 10, NULL, NULL),
(349, 26, 5, 3, 6, NULL, NULL),
(350, 21, 13, 2, 10, NULL, NULL),
(351, 21, 1, 5, 15, NULL, NULL),
(352, 21, 5, 3, 6, NULL, NULL),
(353, 22, 13, 2, 10, NULL, NULL),
(354, 22, 1, 5, 15, NULL, NULL),
(355, 22, 5, 3, 6, NULL, NULL),
(356, 4, 9, 2, 18, NULL, NULL),
(415, 10, 3, 4, 26, NULL, NULL),
(416, 12, 1, 5, 4, NULL, NULL),
(417, 12, 2, 3, 22, NULL, NULL),
(418, 12, 3, 4, 32, NULL, NULL),
(419, 12, 4, 2, 5, NULL, NULL),
(420, 12, 5, 3, 6, NULL, NULL),
(421, 12, 6, 2, 11, NULL, NULL),
(422, 12, 8, 2, 31, NULL, NULL),
(423, 12, 9, 2, 18, NULL, NULL),
(424, 12, 12, 2, 19, NULL, NULL),
(425, 12, 13, 2, 3, NULL, NULL),
(426, 12, 16, 3, 7, NULL, NULL),
(427, 12, 24, 4, 8, NULL, NULL),
(428, 12, 25, 2, 14, NULL, NULL),
(429, 12, 26, 2, 25, NULL, NULL),
(430, 12, 28, 2, 25, NULL, NULL),
(431, 17, 36, 5, 16, NULL, NULL),
(445, 18, 18, 2, 7, NULL, NULL),
(446, 19, 18, 2, 7, NULL, NULL),
(447, 20, 1, 5, 15, NULL, NULL),
(448, 20, 2, 3, 34, NULL, NULL),
(449, 20, 3, 4, 17, NULL, NULL),
(450, 20, 4, 2, 5, NULL, NULL),
(451, 20, 5, 3, 11, NULL, NULL),
(452, 20, 6, 2, 30, NULL, NULL),
(453, 20, 8, 2, 31, NULL, NULL),
(454, 20, 9, 2, 38, NULL, NULL),
(455, 20, 13, 2, 3, NULL, NULL),
(456, 20, 16, 3, 7, NULL, NULL),
(457, 20, 18, 2, 7, NULL, NULL),
(458, 20, 24, 4, 8, NULL, NULL),
(459, 20, 25, 2, 14, NULL, NULL),
(460, 20, 26, 4, 25, NULL, NULL),
(461, 5, 1, 5, 15, NULL, NULL),
(462, 5, 2, 3, 34, NULL, NULL),
(463, 5, 3, 4, 26, NULL, NULL),
(464, 5, 4, 2, 5, NULL, NULL),
(465, 5, 6, 2, 31, NULL, NULL),
(466, 5, 8, 2, 31, NULL, NULL),
(467, 5, 9, 2, 38, NULL, NULL),
(468, 5, 10, 3, 37, NULL, NULL),
(469, 5, 11, 2, 28, NULL, NULL),
(470, 5, 13, 2, 9, NULL, NULL),
(471, 5, 38, 4, 35, NULL, NULL),
(472, 5, 39, 4, 20, NULL, NULL),
(473, 5, 40, 3, 21, NULL, NULL),
(474, 5, 41, 2, 21, NULL, NULL),
(475, 3, 1, 5, 33, NULL, NULL),
(476, 3, 2, 3, 13, NULL, NULL),
(477, 3, 3, 4, 32, NULL, NULL),
(478, 3, 4, 2, 5, NULL, NULL),
(479, 3, 6, 2, 11, NULL, NULL),
(480, 3, 8, 2, 39, NULL, NULL),
(481, 3, 9, 2, 38, NULL, NULL),
(482, 3, 10, 3, 24, NULL, NULL),
(483, 3, 11, 2, 28, NULL, NULL),
(484, 3, 13, 2, 10, NULL, NULL),
(485, 3, 23, 3, 8, NULL, NULL),
(486, 3, 24, 3, 25, NULL, NULL),
(487, 3, 27, 3, 25, NULL, NULL),
(488, 3, 30, 2, 28, NULL, NULL),
(489, 3, 41, 2, 21, NULL, NULL),
(490, 19, 28, 2, 25, NULL, NULL),
(493, 14, 1, 5, 15, NULL, NULL),
(494, 14, 2, 3, 34, NULL, NULL),
(495, 14, 3, 4, 17, NULL, NULL),
(496, 14, 4, 2, 12, NULL, NULL),
(497, 14, 5, 3, 6, NULL, NULL),
(498, 14, 6, 2, 30, NULL, NULL),
(499, 14, 8, 2, 31, NULL, NULL),
(500, 14, 9, 2, 38, NULL, NULL),
(501, 14, 12, 2, 19, NULL, NULL),
(502, 14, 13, 2, 9, NULL, NULL),
(503, 14, 33, 4, 35, NULL, NULL),
(504, 14, 34, 5, 35, NULL, NULL),
(505, 14, 35, 4, 20, NULL, NULL),
(506, 17, 35, 4, 20, NULL, NULL),
(507, 68, 1, 5, 33, NULL, NULL),
(508, 68, 2, 3, 13, NULL, NULL),
(509, 68, 3, 4, 17, NULL, NULL),
(510, 68, 4, 2, 12, NULL, NULL),
(511, 68, 5, 3, 11, NULL, NULL),
(512, 68, 6, 2, 31, NULL, NULL),
(513, 68, 8, 2, 31, NULL, NULL),
(514, 68, 9, 2, 38, NULL, NULL),
(515, 68, 12, 2, 19, NULL, NULL),
(516, 68, 13, 2, 10, NULL, NULL),
(517, 68, 32, 4, 20, NULL, NULL),
(518, 68, 35, 4, 20, NULL, NULL),
(519, 68, 36, 5, 16, NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `events`
--

CREATE TABLE `events` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `nama_event` varchar(255) NOT NULL,
  `tanggal` date NOT NULL,
  `target_shift` enum('PAGI','SIANG') DEFAULT NULL,
  `jam_ke` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`jam_ke`)),
  `target_kelas` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`target_kelas`)),
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `failed_jobs`
--

CREATE TABLE `failed_jobs` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `uuid` varchar(255) NOT NULL,
  `connection` text NOT NULL,
  `queue` text NOT NULL,
  `payload` longtext NOT NULL,
  `exception` longtext NOT NULL,
  `failed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `grade_configs`
--

CREATE TABLE `grade_configs` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `bobot_formatif` int(11) NOT NULL DEFAULT 50,
  `bobot_sumatif` int(11) NOT NULL DEFAULT 50,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `jobs`
--

CREATE TABLE `jobs` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `queue` varchar(255) NOT NULL,
  `payload` longtext NOT NULL,
  `attempts` tinyint(3) UNSIGNED NOT NULL,
  `reserved_at` int(10) UNSIGNED DEFAULT NULL,
  `available_at` int(10) UNSIGNED NOT NULL,
  `created_at` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `job_batches`
--

CREATE TABLE `job_batches` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `total_jobs` int(11) NOT NULL,
  `pending_jobs` int(11) NOT NULL,
  `failed_jobs` int(11) NOT NULL,
  `failed_job_ids` longtext NOT NULL,
  `options` mediumtext DEFAULT NULL,
  `cancelled_at` int(11) DEFAULT NULL,
  `created_at` int(11) NOT NULL,
  `finished_at` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `jp_schedules`
--

CREATE TABLE `jp_schedules` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `shift` enum('PAGI','SIANG') NOT NULL,
  `hari` enum('SENIN','SELASA','RABU','KAMIS','JUMAT','SABTU') NOT NULL,
  `jam_ke` int(11) NOT NULL,
  `waktu_mulai` time NOT NULL,
  `waktu_selesai` time NOT NULL,
  `is_kbm` tinyint(1) NOT NULL DEFAULT 1,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `kbm_sessions`
--

CREATE TABLE `kbm_sessions` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `tanggal` date NOT NULL,
  `id_timetable` bigint(20) UNSIGNED DEFAULT NULL,
  `id_kelas` bigint(20) UNSIGNED DEFAULT NULL,
  `id_mapel` bigint(20) UNSIGNED DEFAULT NULL,
  `jam_ke` int(11) DEFAULT NULL,
  `id_guru_terjadwal` bigint(20) UNSIGNED DEFAULT NULL,
  `id_guru_aktual` bigint(20) UNSIGNED DEFAULT NULL,
  `status_sesi` enum('PENDING','AKTIF','SELESAI','KOSONG','EVENT') NOT NULL DEFAULT 'PENDING',
  `status_guru` enum('PENDING','HADIR','TERLAMBAT','ALPA','DISPENSASI') NOT NULL DEFAULT 'PENDING',
  `waktu_scan_masuk` timestamp NULL DEFAULT NULL,
  `waktu_scan_keluar` timestamp NULL DEFAULT NULL,
  `materi_log` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `learning_objectives`
--

CREATE TABLE `learning_objectives` (
  `id_tp` bigint(20) UNSIGNED NOT NULL,
  `id_guru` bigint(20) UNSIGNED NOT NULL,
  `id_mapel` bigint(20) UNSIGNED NOT NULL,
  `kode_tp` varchar(255) NOT NULL,
  `deskripsi_tp` text NOT NULL,
  `semester` enum('GANJIL','GENAP') NOT NULL DEFAULT 'GANJIL',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `live_exams`
--

CREATE TABLE `live_exams` (
  `id_exam` bigint(20) UNSIGNED NOT NULL,
  `id_kbm_session` bigint(20) UNSIGNED NOT NULL,
  `id_bank` bigint(20) UNSIGNED NOT NULL,
  `status` enum('DRAFT','ACTIVE','FINISHED') NOT NULL DEFAULT 'DRAFT',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `lms_endpoints`
--

CREATE TABLE `lms_endpoints` (
  `id` int(11) NOT NULL,
  `nama_label` varchar(100) NOT NULL,
  `endpoint_url` varchar(500) NOT NULL,
  `bearer_token` text NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `migrations`
--

CREATE TABLE `migrations` (
  `id` int(10) UNSIGNED NOT NULL,
  `migration` varchar(255) NOT NULL,
  `batch` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `migrations`
--

INSERT INTO `migrations` (`id`, `migration`, `batch`) VALUES
(1, '0001_01_01_000000_create_users_table', 1),
(2, '0001_01_01_000001_create_cache_table', 1),
(3, '0001_01_01_000002_create_jobs_table', 1),
(4, '2026_06_21_000001_create_teachers_table', 1),
(5, '2026_06_21_000002_create_classes_table', 1),
(6, '2026_06_21_000003_create_subjects_table', 1),
(7, '2026_06_21_000004_create_teacher_subjects_table', 1),
(8, '2026_06_21_000005_create_class_subjects_table', 1),
(9, '2026_06_21_000006_create_timetable_table', 1),
(10, '2026_06_21_041557_create_personal_access_tokens_table', 1),
(11, '2026_06_21_100000_create_jp_schedules_table', 2),
(12, '2026_06_21_100001_create_students_table', 2),
(13, '2026_06_21_100002_add_roles_to_users_table', 2),
(14, '2026_06_21_110000_create_learning_objectives_table', 3),
(15, '2026_06_21_110001_create_student_grades_table', 3),
(16, '2026_06_21_110002_create_report_cards_table', 3),
(17, '2026_06_22_000001_add_id_guru_wali_to_classes_table', 4),
(18, '2026_06_22_000002_create_kbm_sessions_table', 4),
(19, '2026_06_22_000003_create_events_table', 4),
(20, '2026_06_22_000004_create_question_banks_table', 4),
(21, '2026_06_22_000005_create_questions_table', 4),
(22, '2026_06_22_000006_create_live_exams_table', 4),
(23, '2026_06_22_000007_create_student_answers_table', 4),
(24, '2026_06_22_000008_create_questionnaires_table', 5),
(25, '2026_06_22_000009_create_questionnaire_questions_table', 5),
(26, '2026_06_22_000010_create_questionnaire_responses_table', 5),
(27, '2026_06_22_000011_create_grade_configs_table', 6);

-- --------------------------------------------------------

--
-- Struktur dari tabel `password_reset_tokens`
--

CREATE TABLE `password_reset_tokens` (
  `email` varchar(255) NOT NULL,
  `token` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `personal_access_tokens`
--

CREATE TABLE `personal_access_tokens` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `tokenable_type` varchar(255) NOT NULL,
  `tokenable_id` bigint(20) UNSIGNED NOT NULL,
  `name` text NOT NULL,
  `token` varchar(64) NOT NULL,
  `abilities` text DEFAULT NULL,
  `last_used_at` timestamp NULL DEFAULT NULL,
  `expires_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `questionnaires`
--

CREATE TABLE `questionnaires` (
  `id_questionnaire` bigint(20) UNSIGNED NOT NULL,
  `judul` varchar(255) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `tipe` enum('GURU_MAPEL','WALI_KELAS') NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `questionnaire_questions`
--

CREATE TABLE `questionnaire_questions` (
  `id_q_question` bigint(20) UNSIGNED NOT NULL,
  `id_questionnaire` bigint(20) UNSIGNED NOT NULL,
  `pertanyaan` text NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `questionnaire_responses`
--

CREATE TABLE `questionnaire_responses` (
  `id_response` bigint(20) UNSIGNED NOT NULL,
  `id_questionnaire` bigint(20) UNSIGNED NOT NULL,
  `id_siswa` bigint(20) UNSIGNED NOT NULL,
  `id_guru_target` bigint(20) UNSIGNED NOT NULL,
  `id_q_question` bigint(20) UNSIGNED NOT NULL,
  `rating_score` int(11) NOT NULL DEFAULT 0,
  `komentar` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `questions`
--

CREATE TABLE `questions` (
  `id_question` bigint(20) UNSIGNED NOT NULL,
  `id_bank` bigint(20) UNSIGNED NOT NULL,
  `pertanyaan` text NOT NULL,
  `opsi_a` text NOT NULL,
  `opsi_b` text NOT NULL,
  `opsi_c` text NOT NULL,
  `opsi_d` text NOT NULL,
  `opsi_e` text NOT NULL,
  `jawaban_benar` enum('A','B','C','D','E') NOT NULL,
  `pembahasan` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `question_banks`
--

CREATE TABLE `question_banks` (
  `id_bank` bigint(20) UNSIGNED NOT NULL,
  `id_guru` bigint(20) UNSIGNED NOT NULL,
  `id_mapel` bigint(20) UNSIGNED NOT NULL,
  `judul` varchar(255) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `report_cards`
--

CREATE TABLE `report_cards` (
  `id_rapor` bigint(20) UNSIGNED NOT NULL,
  `id_siswa` bigint(20) UNSIGNED NOT NULL,
  `id_class_subject` bigint(20) UNSIGNED NOT NULL,
  `nilai_sas` int(11) NOT NULL DEFAULT 0,
  `nilai_akhir` int(11) NOT NULL DEFAULT 0,
  `deskripsi_capaian` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `sessions`
--

CREATE TABLE `sessions` (
  `id` varchar(255) NOT NULL,
  `user_id` bigint(20) UNSIGNED DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `payload` longtext NOT NULL,
  `last_activity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `students`
--

CREATE TABLE `students` (
  `id_siswa` bigint(20) UNSIGNED NOT NULL,
  `nis` varchar(20) NOT NULL,
  `nisn` varchar(20) DEFAULT NULL,
  `nama_siswa` varchar(255) NOT NULL,
  `id_kelas` bigint(20) UNSIGNED NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `student_answers`
--

CREATE TABLE `student_answers` (
  `id_answer` bigint(20) UNSIGNED NOT NULL,
  `id_exam` bigint(20) UNSIGNED NOT NULL,
  `id_siswa` bigint(20) UNSIGNED NOT NULL,
  `id_question` bigint(20) UNSIGNED NOT NULL,
  `jawaban_siswa` enum('A','B','C','D','E') DEFAULT NULL,
  `is_correct` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `student_grades`
--

CREATE TABLE `student_grades` (
  `id_grade` bigint(20) UNSIGNED NOT NULL,
  `id_siswa` bigint(20) UNSIGNED NOT NULL,
  `id_tp` bigint(20) UNSIGNED NOT NULL,
  `nilai` int(11) NOT NULL DEFAULT 0,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `subjects`
--

CREATE TABLE `subjects` (
  `id_mapel` bigint(20) UNSIGNED NOT NULL,
  `nama_mapel` varchar(255) NOT NULL,
  `kategori_mapel` varchar(255) NOT NULL,
  `tingkat` varchar(255) DEFAULT NULL,
  `jurusan` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `subjects`
--

INSERT INTO `subjects` (`id_mapel`, `nama_mapel`, `kategori_mapel`, `tingkat`, `jurusan`, `created_at`, `updated_at`) VALUES
(1, 'Matematika', 'UMUM', NULL, NULL, NULL, NULL),
(2, 'Bahasa Indonesia', 'UMUM', NULL, NULL, NULL, NULL),
(3, 'Bahasa Inggris', 'UMUM', NULL, NULL, NULL, NULL),
(4, 'PPKn', 'UMUM', NULL, NULL, NULL, NULL),
(5, 'PKK', 'UMUM', NULL, NULL, NULL, NULL),
(6, 'Sejarah Indonesia', 'UMUM', NULL, NULL, NULL, NULL),
(7, 'Etika Profesi', 'UMUM', NULL, NULL, NULL, NULL),
(8, 'Seni Budaya', 'UMUM', NULL, NULL, NULL, NULL),
(9, 'Pendidikan Agama Islam', 'UMUM', NULL, NULL, NULL, NULL),
(10, 'Informatika', 'UMUM', NULL, NULL, NULL, NULL),
(11, 'IPAS', 'UMUM', NULL, NULL, NULL, NULL),
(12, 'KKA / Coding', 'UMUM', NULL, NULL, NULL, NULL),
(13, 'Penjasorkes', 'OLAHRAGA', NULL, NULL, NULL, NULL),
(14, 'Akuntansi Dasar', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(15, 'Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(16, 'OTK Keuangan', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(17, 'AK Lembaga', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(18, 'Ekonomi Bisnis', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(19, 'AK Keuangan', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(20, 'Komputer Akuntansi', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(21, 'Spreadsheet', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(22, 'Perbankan Dasar', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(23, 'Korespondensi', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(24, 'OTK Humas', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(25, 'OTK Kepegawaian', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(26, 'OTK Sarpras', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(27, 'Teknologi Perkantoran', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(28, 'Kearsipan', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(29, 'Adm Pajak', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(30, 'Adm Umum', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(31, 'Kelistrikan Kendaraan', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(32, 'Kelistrikan Kendaraan Ringan', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(33, 'Kelistrikan Sepeda Motor', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(34, 'Main. Mesin Sepeda Motor', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(35, 'Main. Sasis Sepeda Motor', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(36, 'Main. Mesin Kendaraan', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(37, 'Main. Sasis Kendaraan', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(38, 'TDO', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(39, 'PDTO', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(40, 'Gambar Teknik', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(41, 'K3LH', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(42, 'Dasar Jaringan Komputer', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(43, 'Wide Area Network (WAN)', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(44, 'Teknik Infrastruktur Jaringan', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(45, 'Adm Sistem Jaringan', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(46, 'Tek Jaringan Komputer', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(47, 'Bisnis Teknologi Informasi', 'PRODUKTIF', NULL, NULL, NULL, NULL),
(48, 'Tek Layanan Jaringan', 'PRODUKTIF', NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `system_settings`
--

CREATE TABLE `system_settings` (
  `key` varchar(100) NOT NULL,
  `value` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `teachers`
--

CREATE TABLE `teachers` (
  `id_guru` bigint(20) UNSIGNED NOT NULL,
  `nama_guru` varchar(255) NOT NULL,
  `kode_guru` int(11) NOT NULL,
  `hari_tersedia` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`hari_tersedia`)),
  `shift_pagi` tinyint(1) NOT NULL DEFAULT 1,
  `shift_siang` tinyint(1) NOT NULL DEFAULT 1,
  `hari_tersedia_pagi` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`hari_tersedia_pagi`)),
  `hari_tersedia_siang` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`hari_tersedia_siang`)),
  `min_jp` int(11) NOT NULL DEFAULT 2,
  `max_jp` int(11) NOT NULL DEFAULT 60,
  `allowed_jp_pagi` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`allowed_jp_pagi`)),
  `allowed_jp_siang` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`allowed_jp_siang`)),
  `no_wa` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `teachers`
--

INSERT INTO `teachers` (`id_guru`, `nama_guru`, `kode_guru`, `hari_tersedia`, `shift_pagi`, `shift_siang`, `hari_tersedia_pagi`, `hari_tersedia_siang`, `min_jp`, `max_jp`, `allowed_jp_pagi`, `allowed_jp_siang`, `no_wa`, `created_at`, `updated_at`) VALUES
(1, 'REZA PATRIOTA PUTRA, S.Kom', 1, '[]', 0, 0, '[]', '[]', 2, 60, NULL, NULL, '081234560001', NULL, NULL),
(2, 'TAMAN SASTRA DIKARNA, S.Pd', 2, '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560002', NULL, NULL),
(3, 'SUHARNO, S.Pdi', 3, '[\"SELASA\"]', 1, 1, '[\"SELASA\"]', '[\"SELASA\"]', 2, 60, NULL, NULL, '081234560003', NULL, NULL),
(4, 'SAMSUL HUDA, S.Pd', 4, '[\"SELASA\", \"RABU\"]', 1, 1, '[\"SELASA\", \"RABU\"]', '[\"SELASA\", \"RABU\"]', 2, 60, NULL, NULL, '081234560004', NULL, NULL),
(5, 'AHMAD HUSEN NASUTION, SS', 5, '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"KAMIS\", \"JUMAT\"]', 2, 60, '{\"SENIN\": [3, 4, 6, 7], \"KAMIS\": [3, 4, 6, 7], \"JUMAT\": [3, 4, 6, 7], \"SABTU\": [3, 4, 6, 7]}', NULL, '081234560005', NULL, NULL),
(6, 'WISNU NARA UTAMA, S.Pd', 6, '[\"SELASA\", \"KAMIS\", \"SABTU\"]', 1, 1, '[\"SELASA\", \"KAMIS\", \"SABTU\"]', '[\"SELASA\", \"KAMIS\"]', 2, 60, NULL, NULL, '081234560006', NULL, NULL),
(7, 'FITRI MULYANI, S.Pd', 7, '[\"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SELASA\", \"RABU\", \"KAMIS\"]', 2, 60, NULL, NULL, '081234560007', NULL, NULL),
(8, 'DERA ISMAWATI, S.PdI', 8, '[\"SELASA\", \"RABU\"]', 1, 1, '[\"SELASA\", \"RABU\"]', '[\"SELASA\", \"RABU\"]', 2, 60, NULL, NULL, '081234560008', NULL, NULL),
(9, 'WIDONI SANTOSO, S.Pd', 9, '[\"RABU\", \"KAMIS\"]', 1, 1, '[\"RABU\", \"KAMIS\"]', '[\"RABU\", \"KAMIS\"]', 2, 60, NULL, NULL, '081234560009', NULL, NULL),
(10, 'SRI TITA MULYATI', 10, '[\"SENIN\", \"SELASA\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"SELASA\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560010', NULL, NULL),
(11, 'EUIS SUPRIHATIN, S.Pd', 11, '[\"SENIN\", \"SELASA\", \"KAMIS\", \"JUMAT\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"KAMIS\", \"JUMAT\"]', '[\"SENIN\", \"SELASA\", \"KAMIS\", \"JUMAT\"]', 2, 60, NULL, NULL, '081234560011', NULL, NULL),
(12, 'WIDA HARTANI, S.Pd', 12, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SABTU\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560012', NULL, NULL),
(13, 'LUTHFI AHMAD NAZHIF, S.Pd', 13, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 0, 1, '[]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560013', NULL, NULL),
(14, 'WIDJAYANTI, S.Sos', 14, '[\"JUMAT\", \"SABTU\"]', 1, 1, '[\"JUMAT\", \"SABTU\"]', '[\"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560014', NULL, NULL),
(15, 'DEDE HIDAYATULLAH', 15, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"SELASA\", \"KAMIS\", \"JUMAT\"]', 2, 60, NULL, NULL, '081234560015', NULL, NULL),
(16, 'KOKO, ST', 16, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560016', NULL, NULL),
(17, 'CHRISTIN SIREGAR, S.Pd', 17, '[\"SELASA\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SELASA\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SELASA\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, '{\"SELASA\": [1, 2, 3, 4, 5, 6], \"KAMIS\": [1, 2, 3, 4, 5, 6], \"SABTU\": [1, 2, 3, 4, 5, 6]}', '{\"SELASA\": [3, 4, 5, 6, 7], \"KAMIS\": [3, 4, 5, 6, 7], \"SABTU\": [3, 4, 5, 6, 7]}', '081234560017', NULL, NULL),
(18, 'MUHAMMAD SYAFE\'I', 18, '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560018', NULL, NULL),
(19, 'MUHAMMAD ANDIKA PRAWIRA, S.Kom', 19, '[\"SENIN\", \"RABU\", \"JUMAT\"]', 1, 1, '[\"SENIN\", \"RABU\", \"JUMAT\"]', '[\"SENIN\", \"RABU\", \"JUMAT\"]', 2, 60, NULL, NULL, '081234560019', NULL, NULL),
(20, 'YULISTIO HARDIYANTO, ST', 20, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560020', NULL, NULL),
(21, 'KUAT SUPARTO, ST', 21, '[\"SELASA\", \"RABU\", \"SABTU\"]', 1, 1, '[\"SELASA\", \"RABU\", \"SABTU\"]', '[\"SELASA\", \"RABU\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560021', NULL, NULL),
(22, 'ASTRI WULANDARI, S.Ak', 22, '[\"SELASA\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SELASA\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SELASA\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560022', NULL, NULL),
(23, 'AGUNG AINUL HAKIM', 23, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"KAMIS\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560023', NULL, NULL),
(24, 'SUTRISNO', 24, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560024', NULL, NULL),
(25, 'MUHAMMAD ALBAR SAPIN', 25, '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"KAMIS\", \"JUMAT\"]', 2, 60, NULL, NULL, '081234560025', NULL, NULL),
(26, 'TIARA SHANTI HARTONO, S.Sos', 26, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', 1, 1, '[\"SELASA\", \"JUMAT\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\"]', 2, 60, NULL, NULL, '081234560026', NULL, NULL),
(27, 'OKTARI QOMIMIS SYATUN, S.Pd', 27, '[\"SENIN\", \"SELASA\", \"RABU\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"SABTU\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560027', NULL, NULL),
(28, 'CATUR WULANDARI, A.Md', 28, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"SABTU\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', 2, 60, '{\"SENIN\": [1, 2, 3, 4, 5, 6], \"SELASA\": [1, 2, 3, 4, 5, 6], \"RABU\": [1, 2, 3, 4, 5, 6], \"KAMIS\": [1, 2, 3, 4, 5, 6], \"JUMAT\": [1, 2, 3, 4, 5, 6]}', NULL, '081234560028', NULL, NULL),
(29, 'DWIANA RIKASARI, S.Ap', 29, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560029', NULL, NULL),
(30, 'IDAYATUL MUSTAFIDAH', 30, '[\"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560030', NULL, NULL),
(31, 'RISKA AMELIA, S.M', 31, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', 2, 60, NULL, NULL, '081234560031', NULL, NULL),
(32, 'SISTER NINDA PUTRI, S.Pd', 32, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', '[\"SENIN\", \"SELASA\", \"KAMIS\"]', 2, 60, NULL, NULL, '081234560032', NULL, NULL),
(33, 'DELA AMELIA PUTRI, S.Pd', 33, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', 1, 1, '[\"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', 2, 60, NULL, NULL, '081234560033', NULL, NULL),
(34, 'WIWIK UMAYAH, S.Pd', 34, '[\"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', 1, 1, '[\"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', '[\"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\"]', 2, 60, NULL, NULL, '081234560034', NULL, NULL),
(35, 'ENDANG KURNIAWAN, ST', 35, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560035', NULL, NULL),
(36, 'SEPTIANI RAKA SIWI, M.Pd', 36, '[\"SABTU\"]', 1, 1, '[\"SABTU\"]', '[\"SABTU\"]', 2, 60, NULL, NULL, '081234560036', NULL, NULL),
(37, 'FAUZI, S.Kom', 37, '[\"SELASA\", \"KAMIS\"]', 1, 1, '[\"SELASA\", \"KAMIS\"]', '[\"SELASA\", \"KAMIS\"]', 2, 60, NULL, NULL, '081234560037', NULL, NULL),
(38, 'AZMIRAL AZIS, S.Pd', 38, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 1, 1, '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', '[\"SENIN\", \"SELASA\", \"RABU\", \"KAMIS\", \"JUMAT\", \"SABTU\"]', 2, 60, NULL, NULL, '081234560038', NULL, NULL),
(39, 'MUHAMMAD SYACHTIKO, S.Pd', 39, '[\"RABU\", \"KAMIS\"]', 1, 1, '[\"RABU\", \"KAMIS\"]', '[\"RABU\", \"KAMIS\"]', 2, 60, '{\"RABU\": [3, 4, 5, 6, 7], \"KAMIS\": [3, 4, 5, 6, 7]}', '{\"RABU\": [1, 2, 3, 4, 5], \"KAMIS\": [1, 2, 3, 4, 5]}', '081234560039', NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `teacher_subjects`
--

CREATE TABLE `teacher_subjects` (
  `id_teacher_subject` bigint(20) UNSIGNED NOT NULL,
  `id_guru` bigint(20) UNSIGNED NOT NULL,
  `id_mapel` bigint(20) UNSIGNED NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `teacher_subjects`
--

INSERT INTO `teacher_subjects` (`id_teacher_subject`, `id_guru`, `id_mapel`, `created_at`, `updated_at`) VALUES
(1, 2, 1, NULL, NULL),
(2, 3, 13, NULL, NULL),
(3, 4, 1, NULL, NULL),
(4, 5, 4, NULL, NULL),
(5, 6, 5, NULL, NULL),
(6, 7, 14, NULL, NULL),
(7, 7, 15, NULL, NULL),
(8, 7, 16, NULL, NULL),
(9, 7, 17, NULL, NULL),
(10, 7, 18, NULL, NULL),
(11, 8, 23, NULL, NULL),
(12, 8, 24, NULL, NULL),
(13, 9, 13, NULL, NULL),
(14, 10, 13, NULL, NULL),
(15, 11, 6, NULL, NULL),
(16, 11, 7, NULL, NULL),
(17, 11, 22, NULL, NULL),
(18, 11, 5, NULL, NULL),
(19, 12, 4, NULL, NULL),
(20, 13, 2, NULL, NULL),
(21, 14, 25, NULL, NULL),
(22, 14, 29, NULL, NULL),
(23, 15, 1, NULL, NULL),
(24, 16, 31, NULL, NULL),
(25, 16, 34, NULL, NULL),
(26, 16, 38, NULL, NULL),
(27, 16, 39, NULL, NULL),
(28, 16, 35, NULL, NULL),
(29, 16, 33, NULL, NULL),
(30, 17, 3, NULL, NULL),
(31, 18, 9, NULL, NULL),
(32, 19, 44, NULL, NULL),
(33, 19, 12, NULL, NULL),
(34, 19, 48, NULL, NULL),
(35, 20, 36, NULL, NULL),
(36, 20, 37, NULL, NULL),
(37, 20, 39, NULL, NULL),
(38, 20, 38, NULL, NULL),
(39, 20, 35, NULL, NULL),
(40, 20, 32, NULL, NULL),
(41, 21, 40, NULL, NULL),
(42, 21, 38, NULL, NULL),
(43, 21, 41, NULL, NULL),
(44, 21, 39, NULL, NULL),
(45, 22, 2, NULL, NULL),
(46, 22, 21, NULL, NULL),
(47, 22, 19, NULL, NULL),
(48, 23, 42, NULL, NULL),
(49, 23, 43, NULL, NULL),
(50, 23, 44, NULL, NULL),
(51, 23, 45, NULL, NULL),
(52, 23, 10, NULL, NULL),
(53, 24, 46, NULL, NULL),
(54, 24, 47, NULL, NULL),
(55, 24, 48, NULL, NULL),
(56, 24, 43, NULL, NULL),
(57, 24, 10, NULL, NULL),
(58, 25, 27, NULL, NULL),
(59, 25, 24, NULL, NULL),
(60, 25, 26, NULL, NULL),
(61, 25, 28, NULL, NULL),
(62, 26, 3, NULL, NULL),
(63, 27, 4, NULL, NULL),
(64, 27, 6, NULL, NULL),
(65, 28, 30, NULL, NULL),
(66, 28, 11, NULL, NULL),
(67, 30, 20, NULL, NULL),
(68, 31, 8, NULL, NULL),
(69, 32, 3, NULL, NULL),
(70, 33, 1, NULL, NULL),
(71, 34, 2, NULL, NULL),
(72, 35, 38, NULL, NULL),
(73, 35, 39, NULL, NULL),
(74, 35, 41, NULL, NULL),
(75, 35, 36, NULL, NULL),
(226, 38, 9, NULL, NULL),
(227, 16, 36, NULL, NULL),
(228, 16, 37, NULL, NULL),
(229, 16, 32, NULL, NULL),
(230, 35, 33, NULL, NULL),
(231, 35, 32, NULL, NULL),
(232, 35, 37, NULL, NULL),
(233, 35, 35, NULL, NULL),
(234, 39, 8, NULL, NULL),
(235, 37, 10, NULL, NULL),
(236, 37, 5, NULL, NULL),
(237, 37, 21, NULL, NULL),
(238, 31, 6, NULL, NULL),
(239, 30, 6, NULL, NULL),
(240, 20, 34, NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `timetable`
--

CREATE TABLE `timetable` (
  `id_timetable` bigint(20) UNSIGNED NOT NULL,
  `id_class_subject` bigint(20) UNSIGNED NOT NULL,
  `hari` varchar(255) NOT NULL,
  `jam_ke` int(11) NOT NULL,
  `id_guru` bigint(20) UNSIGNED DEFAULT NULL,
  `is_fallback` tinyint(1) NOT NULL DEFAULT 0,
  `original_guru_id` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `timetable`
--

INSERT INTO `timetable` (`id_timetable`, `id_class_subject`, `hari`, `jam_ke`, `id_guru`, `is_fallback`, `original_guru_id`, `created_at`, `updated_at`) VALUES
(12961, 33, 'SENIN', 2, 32, 0, NULL, NULL, NULL),
(12962, 118, 'SENIN', 3, 18, 0, NULL, NULL, NULL),
(12963, 118, 'SENIN', 4, 18, 0, NULL, NULL, NULL),
(12964, 33, 'SENIN', 5, 32, 0, NULL, NULL, NULL),
(12965, 253, 'SENIN', 6, 11, 0, NULL, NULL, NULL),
(12966, 253, 'SENIN', 7, 11, 0, NULL, NULL, NULL),
(12967, 185, 'SELASA', 1, 28, 0, NULL, NULL, NULL),
(12968, 185, 'SELASA', 2, 28, 0, NULL, NULL, NULL),
(12969, 33, 'SELASA', 3, 32, 0, NULL, NULL, NULL),
(12970, 116, 'SELASA', 4, 37, 0, NULL, NULL, NULL),
(12971, 116, 'SELASA', 5, 37, 0, NULL, NULL, NULL),
(12972, 238, 'SELASA', 6, 22, 0, NULL, NULL, NULL),
(12973, 238, 'SELASA', 7, 22, 0, NULL, NULL, NULL),
(12974, 233, 'RABU', 1, 33, 0, NULL, NULL, NULL),
(12975, 233, 'RABU', 2, 33, 0, NULL, NULL, NULL),
(12976, 93, 'RABU', 3, 21, 0, NULL, NULL, NULL),
(12977, 93, 'RABU', 4, 21, 0, NULL, NULL, NULL),
(12978, 197, 'RABU', 5, 39, 0, NULL, NULL, NULL),
(12979, 178, 'RABU', 6, 30, 0, NULL, NULL, NULL),
(12980, 178, 'RABU', 7, 30, 0, NULL, NULL, NULL),
(12981, 252, 'KAMIS', 1, 9, 0, NULL, NULL, NULL),
(12982, 252, 'KAMIS', 2, 9, 0, NULL, NULL, NULL),
(12983, 150, 'KAMIS', 3, 37, 0, NULL, NULL, NULL),
(12984, 150, 'KAMIS', 4, 37, 0, NULL, NULL, NULL),
(12985, 33, 'KAMIS', 5, 32, 0, NULL, NULL, NULL),
(12986, 150, 'KAMIS', 6, 37, 0, NULL, NULL, NULL),
(12987, 197, 'KAMIS', 7, 39, 0, NULL, NULL, NULL),
(12988, 233, 'JUMAT', 1, 33, 0, NULL, NULL, NULL),
(12989, 233, 'JUMAT', 2, 33, 0, NULL, NULL, NULL),
(12990, 233, 'JUMAT', 3, 33, 0, NULL, NULL, NULL),
(12991, 238, 'JUMAT', 4, 22, 0, NULL, NULL, NULL),
(12992, 255, 'JUMAT', 5, 11, 0, NULL, NULL, NULL),
(12993, 255, 'JUMAT', 6, 11, 0, NULL, NULL, NULL),
(12994, 254, 'SABTU', 1, 7, 0, NULL, NULL, NULL),
(12995, 254, 'SABTU', 2, 7, 0, NULL, NULL, NULL),
(12996, 254, 'SABTU', 3, 7, 0, NULL, NULL, NULL),
(12997, 194, 'SABTU', 4, 30, 0, NULL, NULL, NULL),
(12998, 194, 'SABTU', 5, 30, 0, NULL, NULL, NULL),
(12999, 251, 'SABTU', 6, 12, 0, NULL, NULL, NULL),
(13000, 251, 'SABTU', 7, 12, 0, NULL, NULL, NULL),
(13001, 179, 'SENIN', 2, 11, 0, NULL, NULL, NULL),
(13002, 256, 'SENIN', 3, 5, 0, NULL, NULL, NULL),
(13003, 256, 'SENIN', 4, 5, 0, NULL, NULL, NULL),
(13004, 257, 'SENIN', 5, 10, 0, NULL, NULL, NULL),
(13005, 257, 'SENIN', 6, 10, 0, NULL, NULL, NULL),
(13006, 42, 'SENIN', 7, 18, 0, NULL, NULL, NULL),
(13007, 258, 'SELASA', 1, 8, 0, NULL, NULL, NULL),
(13008, 258, 'SELASA', 2, 8, 0, NULL, NULL, NULL),
(13009, 258, 'SELASA', 3, 8, 0, NULL, NULL, NULL),
(13010, 179, 'SELASA', 4, 11, 0, NULL, NULL, NULL),
(13011, 234, 'SELASA', 5, 33, 0, NULL, NULL, NULL),
(13012, 234, 'SELASA', 6, 33, 0, NULL, NULL, NULL),
(13013, 234, 'SELASA', 7, 33, 0, NULL, NULL, NULL),
(13014, 94, 'RABU', 1, 21, 0, NULL, NULL, NULL),
(13015, 94, 'RABU', 2, 21, 0, NULL, NULL, NULL),
(13016, 151, 'RABU', 3, 24, 0, NULL, NULL, NULL),
(13017, 151, 'RABU', 4, 24, 0, NULL, NULL, NULL),
(13018, 151, 'RABU', 5, 24, 0, NULL, NULL, NULL),
(13019, 234, 'RABU', 6, 33, 0, NULL, NULL, NULL),
(13020, 234, 'RABU', 7, 33, 0, NULL, NULL, NULL),
(13021, 102, 'KAMIS', 1, 22, 0, NULL, NULL, NULL),
(13022, 102, 'KAMIS', 2, 22, 0, NULL, NULL, NULL),
(13023, 102, 'KAMIS', 3, 22, 0, NULL, NULL, NULL),
(13024, 198, 'KAMIS', 4, 39, 0, NULL, NULL, NULL),
(13025, 198, 'KAMIS', 5, 39, 0, NULL, NULL, NULL),
(13026, 223, 'KAMIS', 6, 32, 0, NULL, NULL, NULL),
(13027, 223, 'KAMIS', 7, 32, 0, NULL, NULL, NULL),
(13028, 155, 'JUMAT', 1, 25, 0, NULL, NULL, NULL),
(13029, 155, 'JUMAT', 2, 25, 0, NULL, NULL, NULL),
(13030, 155, 'JUMAT', 3, 25, 0, NULL, NULL, NULL),
(13031, 223, 'JUMAT', 4, 32, 0, NULL, NULL, NULL),
(13032, 223, 'JUMAT', 5, 32, 0, NULL, NULL, NULL),
(13033, 42, 'JUMAT', 6, 18, 0, NULL, NULL, NULL),
(13034, 186, 'SABTU', 1, 28, 0, NULL, NULL, NULL),
(13035, 186, 'SABTU', 2, 28, 0, NULL, NULL, NULL),
(13036, 182, 'SABTU', 3, 28, 0, NULL, NULL, NULL),
(13037, 182, 'SABTU', 4, 28, 0, NULL, NULL, NULL),
(13038, 157, 'SABTU', 5, 25, 0, NULL, NULL, NULL),
(13039, 157, 'SABTU', 6, 25, 0, NULL, NULL, NULL),
(13040, 157, 'SABTU', 7, 25, 0, NULL, NULL, NULL),
(13041, 476, 'SENIN', 1, 13, 0, NULL, NULL, NULL),
(13042, 483, 'SENIN', 2, 28, 0, NULL, NULL, NULL),
(13043, 483, 'SENIN', 3, 28, 0, NULL, NULL, NULL),
(13044, 478, 'SENIN', 4, 5, 0, NULL, NULL, NULL),
(13045, 478, 'SENIN', 5, 5, 0, NULL, NULL, NULL),
(13046, 479, 'SENIN', 6, 11, 0, NULL, NULL, NULL),
(13047, 479, 'SENIN', 7, 11, 0, NULL, NULL, NULL),
(13048, 481, 'SELASA', 1, 38, 0, NULL, NULL, NULL),
(13049, 488, 'SELASA', 2, 28, 0, NULL, NULL, NULL),
(13050, 488, 'SELASA', 3, 28, 0, NULL, NULL, NULL),
(13051, 477, 'SELASA', 4, 32, 0, NULL, NULL, NULL),
(13052, 477, 'SELASA', 5, 32, 0, NULL, NULL, NULL),
(13053, 477, 'SELASA', 6, 32, 0, NULL, NULL, NULL),
(13054, 477, 'SELASA', 7, 32, 0, NULL, NULL, NULL),
(13055, 485, 'RABU', 1, 8, 0, NULL, NULL, NULL),
(13056, 485, 'RABU', 2, 8, 0, NULL, NULL, NULL),
(13057, 485, 'RABU', 3, 8, 0, NULL, NULL, NULL),
(13058, 480, 'RABU', 4, 39, 0, NULL, NULL, NULL),
(13059, 480, 'RABU', 5, 39, 0, NULL, NULL, NULL),
(13060, 475, 'RABU', 6, 33, 0, NULL, NULL, NULL),
(13061, 475, 'RABU', 7, 33, 0, NULL, NULL, NULL),
(13062, 481, 'KAMIS', 1, 38, 0, NULL, NULL, NULL),
(13063, 482, 'KAMIS', 2, 24, 0, NULL, NULL, NULL),
(13064, 482, 'KAMIS', 3, 24, 0, NULL, NULL, NULL),
(13065, 482, 'KAMIS', 4, 24, 0, NULL, NULL, NULL),
(13066, 487, 'KAMIS', 5, 25, 0, NULL, NULL, NULL),
(13067, 487, 'KAMIS', 6, 25, 0, NULL, NULL, NULL),
(13068, 487, 'KAMIS', 7, 25, 0, NULL, NULL, NULL),
(13069, 475, 'JUMAT', 1, 33, 0, NULL, NULL, NULL),
(13070, 475, 'JUMAT', 2, 33, 0, NULL, NULL, NULL),
(13071, 475, 'JUMAT', 3, 33, 0, NULL, NULL, NULL),
(13072, 486, 'JUMAT', 4, 25, 0, NULL, NULL, NULL),
(13073, 486, 'JUMAT', 5, 25, 0, NULL, NULL, NULL),
(13074, 486, 'JUMAT', 6, 25, 0, NULL, NULL, NULL),
(13075, 476, 'SABTU', 1, 13, 0, NULL, NULL, NULL),
(13076, 476, 'SABTU', 2, 13, 0, NULL, NULL, NULL),
(13077, 489, 'SABTU', 3, 21, 0, NULL, NULL, NULL),
(13078, 489, 'SABTU', 4, 21, 0, NULL, NULL, NULL),
(13079, 484, 'SABTU', 5, 10, 0, NULL, NULL, NULL),
(13080, 484, 'SABTU', 6, 10, 0, NULL, NULL, NULL),
(13081, 140, 'SENIN', 2, 23, 0, NULL, NULL, NULL),
(13082, 140, 'SENIN', 3, 23, 0, NULL, NULL, NULL),
(13083, 10, 'SENIN', 4, 15, 0, NULL, NULL, NULL),
(13084, 10, 'SENIN', 5, 15, 0, NULL, NULL, NULL),
(13085, 84, 'SENIN', 6, 35, 0, NULL, NULL, NULL),
(13086, 84, 'SENIN', 7, 35, 0, NULL, NULL, NULL),
(13087, 99, 'SELASA', 1, 21, 0, NULL, NULL, NULL),
(13088, 99, 'SELASA', 2, 21, 0, NULL, NULL, NULL),
(13089, 10, 'SELASA', 3, 15, 0, NULL, NULL, NULL),
(13090, 10, 'SELASA', 4, 15, 0, NULL, NULL, NULL),
(13091, 10, 'SELASA', 5, 15, 0, NULL, NULL, NULL),
(13092, 101, 'SELASA', 6, 16, 0, NULL, NULL, NULL),
(13093, 101, 'SELASA', 7, 16, 0, NULL, NULL, NULL),
(13094, 192, 'RABU', 1, 28, 0, NULL, NULL, NULL),
(13095, 192, 'RABU', 2, 28, 0, NULL, NULL, NULL),
(13096, 270, 'RABU', 3, 9, 0, NULL, NULL, NULL),
(13097, 270, 'RABU', 4, 9, 0, NULL, NULL, NULL),
(13098, 271, 'RABU', 5, 31, 0, NULL, NULL, NULL),
(13099, 174, 'RABU', 6, 27, 0, NULL, NULL, NULL),
(13100, 174, 'RABU', 7, 27, 0, NULL, NULL, NULL),
(13101, 105, 'KAMIS', 1, 34, 0, NULL, NULL, NULL),
(13102, 105, 'KAMIS', 2, 34, 0, NULL, NULL, NULL),
(13103, 105, 'KAMIS', 3, 34, 0, NULL, NULL, NULL),
(13104, 204, 'KAMIS', 4, 31, 0, NULL, NULL, NULL),
(13105, 204, 'KAMIS', 5, 31, 0, NULL, NULL, NULL),
(13106, 101, 'KAMIS', 6, 16, 0, NULL, NULL, NULL),
(13107, 101, 'KAMIS', 7, 16, 0, NULL, NULL, NULL),
(13108, 140, 'JUMAT', 1, 23, 0, NULL, NULL, NULL),
(13109, 167, 'JUMAT', 2, 26, 0, NULL, NULL, NULL),
(13110, 167, 'JUMAT', 3, 26, 0, NULL, NULL, NULL),
(13111, 167, 'JUMAT', 4, 26, 0, NULL, NULL, NULL),
(13112, 167, 'JUMAT', 5, 26, 0, NULL, NULL, NULL),
(13113, 271, 'JUMAT', 6, 31, 0, NULL, NULL, NULL),
(13114, 356, 'SABTU', 1, 18, 0, NULL, NULL, NULL),
(13115, 356, 'SABTU', 2, 18, 0, NULL, NULL, NULL),
(13116, 84, 'SABTU', 3, 35, 0, NULL, NULL, NULL),
(13117, 84, 'SABTU', 4, 35, 0, NULL, NULL, NULL),
(13118, 90, 'SABTU', 5, 21, 0, NULL, NULL, NULL),
(13119, 90, 'SABTU', 6, 21, 0, NULL, NULL, NULL),
(13120, 90, 'SABTU', 7, 21, 0, NULL, NULL, NULL),
(13121, 464, 'SENIN', 1, 5, 0, NULL, NULL, NULL),
(13122, 464, 'SENIN', 2, 5, 0, NULL, NULL, NULL),
(13123, 463, 'SENIN', 3, 26, 0, NULL, NULL, NULL),
(13124, 465, 'SENIN', 4, 31, 0, NULL, NULL, NULL),
(13125, 461, 'SENIN', 5, 15, 0, NULL, NULL, NULL),
(13126, 461, 'SENIN', 6, 15, 0, NULL, NULL, NULL),
(13127, 461, 'SENIN', 7, 15, 0, NULL, NULL, NULL),
(13128, 468, 'SELASA', 1, 37, 0, NULL, NULL, NULL),
(13129, 468, 'SELASA', 2, 37, 0, NULL, NULL, NULL),
(13130, 468, 'SELASA', 3, 37, 0, NULL, NULL, NULL),
(13131, 465, 'SELASA', 4, 31, 0, NULL, NULL, NULL),
(13132, 462, 'SELASA', 5, 34, 0, NULL, NULL, NULL),
(13133, 474, 'SELASA', 6, 21, 0, NULL, NULL, NULL),
(13134, 474, 'SELASA', 7, 21, 0, NULL, NULL, NULL),
(13135, 473, 'RABU', 1, 21, 0, NULL, NULL, NULL),
(13136, 473, 'RABU', 2, 21, 0, NULL, NULL, NULL),
(13137, 473, 'RABU', 3, 21, 0, NULL, NULL, NULL),
(13138, 472, 'RABU', 4, 20, 0, NULL, NULL, NULL),
(13139, 472, 'RABU', 5, 20, 0, NULL, NULL, NULL),
(13140, 470, 'RABU', 6, 9, 0, NULL, NULL, NULL),
(13141, 470, 'RABU', 7, 9, 0, NULL, NULL, NULL),
(13142, 463, 'KAMIS', 1, 26, 0, NULL, NULL, NULL),
(13143, 463, 'KAMIS', 2, 26, 0, NULL, NULL, NULL),
(13144, 463, 'KAMIS', 3, 26, 0, NULL, NULL, NULL),
(13145, 462, 'KAMIS', 4, 34, 0, NULL, NULL, NULL),
(13146, 462, 'KAMIS', 5, 34, 0, NULL, NULL, NULL),
(13147, 461, 'KAMIS', 6, 15, 0, NULL, NULL, NULL),
(13148, 461, 'KAMIS', 7, 15, 0, NULL, NULL, NULL),
(13149, 466, 'JUMAT', 1, 31, 0, NULL, NULL, NULL),
(13150, 466, 'JUMAT', 2, 31, 0, NULL, NULL, NULL),
(13151, 469, 'JUMAT', 3, 28, 0, NULL, NULL, NULL),
(13152, 469, 'JUMAT', 4, 28, 0, NULL, NULL, NULL),
(13153, 472, 'JUMAT', 5, 20, 0, NULL, NULL, NULL),
(13154, 472, 'JUMAT', 6, 20, 0, NULL, NULL, NULL),
(13155, 471, 'SABTU', 1, 35, 0, NULL, NULL, NULL),
(13156, 471, 'SABTU', 2, 35, 0, NULL, NULL, NULL),
(13157, 471, 'SABTU', 3, 35, 0, NULL, NULL, NULL),
(13158, 471, 'SABTU', 4, 35, 0, NULL, NULL, NULL),
(13159, 467, 'SABTU', 5, 38, 0, NULL, NULL, NULL),
(13160, 467, 'SABTU', 6, 38, 0, NULL, NULL, NULL),
(13161, 188, 'SENIN', 2, 28, 0, NULL, NULL, NULL),
(13162, 225, 'SENIN', 3, 32, 0, NULL, NULL, NULL),
(13163, 225, 'SENIN', 4, 32, 0, NULL, NULL, NULL),
(13164, 144, 'SENIN', 5, 24, 0, NULL, NULL, NULL),
(13165, 144, 'SENIN', 6, 24, 0, NULL, NULL, NULL),
(13166, 144, 'SENIN', 7, 24, 0, NULL, NULL, NULL),
(13167, 153, 'SELASA', 1, 37, 0, NULL, NULL, NULL),
(13168, 153, 'SELASA', 2, 37, 0, NULL, NULL, NULL),
(13169, 153, 'SELASA', 3, 37, 0, NULL, NULL, NULL),
(13170, 128, 'SELASA', 4, 23, 0, NULL, NULL, NULL),
(13171, 128, 'SELASA', 5, 23, 0, NULL, NULL, NULL),
(13172, 128, 'SELASA', 6, 23, 0, NULL, NULL, NULL),
(13173, 128, 'SELASA', 7, 23, 0, NULL, NULL, NULL),
(13174, 235, 'RABU', 1, 15, 0, NULL, NULL, NULL),
(13175, 235, 'RABU', 2, 15, 0, NULL, NULL, NULL),
(13176, 235, 'RABU', 3, 15, 0, NULL, NULL, NULL),
(13177, 200, 'RABU', 4, 39, 0, NULL, NULL, NULL),
(13178, 248, 'RABU', 5, 21, 0, NULL, NULL, NULL),
(13179, 248, 'RABU', 6, 21, 0, NULL, NULL, NULL),
(13180, 248, 'RABU', 7, 21, 0, NULL, NULL, NULL),
(13181, 142, 'KAMIS', 1, 24, 0, NULL, NULL, NULL),
(13182, 142, 'KAMIS', 2, 24, 0, NULL, NULL, NULL),
(13183, 142, 'KAMIS', 3, 24, 0, NULL, NULL, NULL),
(13184, 103, 'KAMIS', 4, 22, 0, NULL, NULL, NULL),
(13185, 188, 'KAMIS', 5, 28, 0, NULL, NULL, NULL),
(13186, 200, 'KAMIS', 6, 39, 0, NULL, NULL, NULL),
(13187, 103, 'KAMIS', 7, 22, 0, NULL, NULL, NULL),
(13188, 181, 'JUMAT', 1, 30, 0, NULL, NULL, NULL),
(13189, 225, 'JUMAT', 2, 32, 0, NULL, NULL, NULL),
(13190, 225, 'JUMAT', 3, 32, 0, NULL, NULL, NULL),
(13191, 119, 'JUMAT', 4, 18, 0, NULL, NULL, NULL),
(13192, 119, 'JUMAT', 5, 18, 0, NULL, NULL, NULL),
(13193, 181, 'JUMAT', 6, 30, 0, NULL, NULL, NULL),
(13194, 103, 'SABTU', 1, 22, 0, NULL, NULL, NULL),
(13195, 263, 'SABTU', 2, 12, 0, NULL, NULL, NULL),
(13196, 263, 'SABTU', 3, 12, 0, NULL, NULL, NULL),
(13197, 235, 'SABTU', 4, 15, 0, NULL, NULL, NULL),
(13198, 235, 'SABTU', 5, 15, 0, NULL, NULL, NULL),
(13199, 264, 'SABTU', 6, 10, 0, NULL, NULL, NULL),
(13200, 264, 'SABTU', 7, 10, 0, NULL, NULL, NULL),
(13201, 143, 'SENIN', 1, 24, 0, NULL, NULL, NULL),
(13202, 143, 'SENIN', 2, 24, 0, NULL, NULL, NULL),
(13203, 143, 'SENIN', 3, 24, 0, NULL, NULL, NULL),
(13204, 236, 'SENIN', 4, 15, 0, NULL, NULL, NULL),
(13205, 226, 'SENIN', 5, 32, 0, NULL, NULL, NULL),
(13206, 171, 'SENIN', 6, 5, 0, NULL, NULL, NULL),
(13207, 171, 'SENIN', 7, 5, 0, NULL, NULL, NULL),
(13208, 226, 'SELASA', 1, 32, 0, NULL, NULL, NULL),
(13209, 226, 'SELASA', 2, 32, 0, NULL, NULL, NULL),
(13210, 226, 'SELASA', 3, 32, 0, NULL, NULL, NULL),
(13211, 236, 'SELASA', 4, 15, 0, NULL, NULL, NULL),
(13212, 236, 'SELASA', 5, 15, 0, NULL, NULL, NULL),
(13213, 236, 'SELASA', 6, 15, 0, NULL, NULL, NULL),
(13214, 68, 'SELASA', 7, 30, 0, NULL, NULL, NULL),
(13215, 201, 'RABU', 1, 39, 0, NULL, NULL, NULL),
(13216, 201, 'RABU', 2, 39, 0, NULL, NULL, NULL),
(13217, 43, 'RABU', 3, 38, 0, NULL, NULL, NULL),
(13218, 43, 'RABU', 4, 38, 0, NULL, NULL, NULL),
(13219, 96, 'RABU', 5, 21, 0, NULL, NULL, NULL),
(13220, 96, 'RABU', 6, 21, 0, NULL, NULL, NULL),
(13221, 96, 'RABU', 7, 21, 0, NULL, NULL, NULL),
(13222, 154, 'KAMIS', 1, 37, 0, NULL, NULL, NULL),
(13223, 154, 'KAMIS', 2, 37, 0, NULL, NULL, NULL),
(13224, 154, 'KAMIS', 3, 37, 0, NULL, NULL, NULL),
(13225, 189, 'KAMIS', 4, 28, 0, NULL, NULL, NULL),
(13226, 189, 'KAMIS', 5, 28, 0, NULL, NULL, NULL),
(13227, 129, 'KAMIS', 6, 23, 0, NULL, NULL, NULL),
(13228, 129, 'KAMIS', 7, 23, 0, NULL, NULL, NULL),
(13229, 266, 'JUMAT', 1, 10, 0, NULL, NULL, NULL),
(13230, 266, 'JUMAT', 2, 10, 0, NULL, NULL, NULL),
(13231, 236, 'JUMAT', 3, 15, 0, NULL, NULL, NULL),
(13232, 265, 'JUMAT', 4, 22, 0, NULL, NULL, NULL),
(13233, 265, 'JUMAT', 5, 22, 0, NULL, NULL, NULL),
(13234, 265, 'JUMAT', 6, 22, 0, NULL, NULL, NULL),
(13235, 129, 'SABTU', 1, 23, 0, NULL, NULL, NULL),
(13236, 129, 'SABTU', 2, 23, 0, NULL, NULL, NULL),
(13237, 68, 'SABTU', 3, 30, 0, NULL, NULL, NULL),
(13238, 145, 'SABTU', 4, 24, 0, NULL, NULL, NULL),
(13239, 145, 'SABTU', 5, 24, 0, NULL, NULL, NULL),
(13240, 145, 'SABTU', 6, 24, 0, NULL, NULL, NULL),
(13241, 24, 'SENIN', 2, 16, 0, NULL, NULL, NULL),
(13242, 24, 'SENIN', 3, 16, 0, NULL, NULL, NULL),
(13243, 190, 'SENIN', 4, 28, 0, NULL, NULL, NULL),
(13244, 190, 'SENIN', 5, 28, 0, NULL, NULL, NULL),
(13245, 202, 'SENIN', 6, 31, 0, NULL, NULL, NULL),
(13246, 202, 'SENIN', 7, 31, 0, NULL, NULL, NULL),
(13247, 165, 'SELASA', 1, 26, 0, NULL, NULL, NULL),
(13248, 165, 'SELASA', 2, 26, 0, NULL, NULL, NULL),
(13249, 97, 'SELASA', 3, 21, 0, NULL, NULL, NULL),
(13250, 97, 'SELASA', 4, 21, 0, NULL, NULL, NULL),
(13251, 69, 'SELASA', 5, 30, 0, NULL, NULL, NULL),
(13252, 165, 'SELASA', 6, 26, 0, NULL, NULL, NULL),
(13253, 165, 'SELASA', 7, 26, 0, NULL, NULL, NULL),
(13254, 82, 'RABU', 1, 20, 0, NULL, NULL, NULL),
(13255, 82, 'RABU', 2, 20, 0, NULL, NULL, NULL),
(13256, 8, 'RABU', 3, 33, 0, NULL, NULL, NULL),
(13257, 8, 'RABU', 4, 33, 0, NULL, NULL, NULL),
(13258, 8, 'RABU', 5, 33, 0, NULL, NULL, NULL),
(13259, 267, 'RABU', 6, 9, 0, NULL, NULL, NULL),
(13260, 267, 'RABU', 7, 9, 0, NULL, NULL, NULL),
(13261, 138, 'KAMIS', 1, 37, 0, NULL, NULL, NULL),
(13262, 138, 'KAMIS', 2, 37, 0, NULL, NULL, NULL),
(13263, 82, 'KAMIS', 3, 20, 0, NULL, NULL, NULL),
(13264, 82, 'KAMIS', 4, 20, 0, NULL, NULL, NULL),
(13265, 138, 'KAMIS', 5, 37, 0, NULL, NULL, NULL),
(13266, 44, 'KAMIS', 6, 18, 0, NULL, NULL, NULL),
(13267, 44, 'KAMIS', 7, 18, 0, NULL, NULL, NULL),
(13268, 104, 'JUMAT', 1, 22, 0, NULL, NULL, NULL),
(13269, 104, 'JUMAT', 2, 22, 0, NULL, NULL, NULL),
(13270, 104, 'JUMAT', 3, 22, 0, NULL, NULL, NULL),
(13271, 69, 'JUMAT', 4, 30, 0, NULL, NULL, NULL),
(13272, 8, 'JUMAT', 5, 33, 0, NULL, NULL, NULL),
(13273, 8, 'JUMAT', 6, 33, 0, NULL, NULL, NULL),
(13274, 88, 'SABTU', 1, 21, 0, NULL, NULL, NULL),
(13275, 88, 'SABTU', 2, 21, 0, NULL, NULL, NULL),
(13276, 88, 'SABTU', 3, 21, 0, NULL, NULL, NULL),
(13277, 172, 'SABTU', 4, 12, 0, NULL, NULL, NULL),
(13278, 172, 'SABTU', 5, 12, 0, NULL, NULL, NULL),
(13279, 24, 'SABTU', 6, 16, 0, NULL, NULL, NULL),
(13280, 24, 'SABTU', 7, 16, 0, NULL, NULL, NULL),
(13281, 166, 'SENIN', 1, 26, 0, NULL, NULL, NULL),
(13282, 166, 'SENIN', 2, 26, 0, NULL, NULL, NULL),
(13283, 120, 'SENIN', 3, 38, 0, NULL, NULL, NULL),
(13284, 247, 'SENIN', 4, 20, 0, NULL, NULL, NULL),
(13285, 247, 'SENIN', 5, 20, 0, NULL, NULL, NULL),
(13286, 247, 'SENIN', 6, 20, 0, NULL, NULL, NULL),
(13287, 247, 'SENIN', 7, 20, 0, NULL, NULL, NULL),
(13288, 89, 'SELASA', 1, 21, 0, NULL, NULL, NULL),
(13289, 89, 'SELASA', 2, 21, 0, NULL, NULL, NULL),
(13290, 89, 'SELASA', 3, 21, 0, NULL, NULL, NULL),
(13291, 139, 'SELASA', 4, 37, 0, NULL, NULL, NULL),
(13292, 203, 'SELASA', 5, 31, 0, NULL, NULL, NULL),
(13293, 139, 'SELASA', 6, 37, 0, NULL, NULL, NULL),
(13294, 139, 'SELASA', 7, 37, 0, NULL, NULL, NULL),
(13295, 120, 'RABU', 1, 38, 0, NULL, NULL, NULL),
(13296, 166, 'RABU', 2, 26, 0, NULL, NULL, NULL),
(13297, 166, 'RABU', 3, 26, 0, NULL, NULL, NULL),
(13298, 70, 'RABU', 4, 30, 0, NULL, NULL, NULL),
(13299, 70, 'RABU', 5, 30, 0, NULL, NULL, NULL),
(13300, 191, 'RABU', 6, 28, 0, NULL, NULL, NULL),
(13301, 191, 'RABU', 7, 28, 0, NULL, NULL, NULL),
(13302, 269, 'KAMIS', 1, 9, 0, NULL, NULL, NULL),
(13303, 269, 'KAMIS', 2, 9, 0, NULL, NULL, NULL),
(13304, 9, 'KAMIS', 3, 15, 0, NULL, NULL, NULL),
(13305, 9, 'KAMIS', 4, 15, 0, NULL, NULL, NULL),
(13306, 268, 'KAMIS', 5, 22, 0, NULL, NULL, NULL),
(13307, 268, 'KAMIS', 6, 22, 0, NULL, NULL, NULL),
(13308, 268, 'KAMIS', 7, 22, 0, NULL, NULL, NULL),
(13309, 173, 'JUMAT', 1, 12, 0, NULL, NULL, NULL),
(13310, 173, 'JUMAT', 2, 12, 0, NULL, NULL, NULL),
(13311, 203, 'JUMAT', 3, 31, 0, NULL, NULL, NULL),
(13312, 9, 'JUMAT', 4, 15, 0, NULL, NULL, NULL),
(13313, 9, 'JUMAT', 5, 15, 0, NULL, NULL, NULL),
(13314, 9, 'JUMAT', 6, 15, 0, NULL, NULL, NULL),
(13315, 98, 'SABTU', 1, 21, 0, NULL, NULL, NULL),
(13316, 98, 'SABTU', 2, 21, 0, NULL, NULL, NULL),
(13317, 92, 'SABTU', 3, 16, 0, NULL, NULL, NULL),
(13318, 92, 'SABTU', 4, 16, 0, NULL, NULL, NULL),
(13319, 92, 'SABTU', 5, 16, 0, NULL, NULL, NULL),
(13320, 92, 'SABTU', 6, 16, 0, NULL, NULL, NULL),
(13321, 58, 'SENIN', 1, 19, 0, NULL, NULL, NULL),
(13322, 58, 'SENIN', 2, 19, 0, NULL, NULL, NULL),
(13323, 12, 'SENIN', 3, 2, 0, NULL, NULL, NULL),
(13324, 12, 'SENIN', 4, 2, 0, NULL, NULL, NULL),
(13325, 415, 'SENIN', 5, 26, 0, NULL, NULL, NULL),
(13326, 415, 'SENIN', 6, 26, 0, NULL, NULL, NULL),
(13327, 415, 'SENIN', 7, 26, 0, NULL, NULL, NULL),
(13328, 195, 'SELASA', 1, 30, 0, NULL, NULL, NULL),
(13329, 195, 'SELASA', 2, 30, 0, NULL, NULL, NULL),
(13330, 277, 'SELASA', 3, 3, 0, NULL, NULL, NULL),
(13331, 277, 'SELASA', 4, 3, 0, NULL, NULL, NULL),
(13332, 282, 'SELASA', 5, 37, 0, NULL, NULL, NULL),
(13333, 281, 'SELASA', 6, 7, 0, NULL, NULL, NULL),
(13334, 281, 'SELASA', 7, 7, 0, NULL, NULL, NULL),
(13335, 415, 'RABU', 1, 26, 0, NULL, NULL, NULL),
(13336, 279, 'RABU', 2, 7, 0, NULL, NULL, NULL),
(13337, 279, 'RABU', 3, 7, 0, NULL, NULL, NULL),
(13338, 184, 'RABU', 4, 28, 0, NULL, NULL, NULL),
(13339, 184, 'RABU', 5, 28, 0, NULL, NULL, NULL),
(13340, 280, 'RABU', 6, 7, 0, NULL, NULL, NULL),
(13341, 280, 'RABU', 7, 7, 0, NULL, NULL, NULL),
(13342, 278, 'KAMIS', 1, 11, 0, NULL, NULL, NULL),
(13343, 278, 'KAMIS', 2, 11, 0, NULL, NULL, NULL),
(13344, 276, 'KAMIS', 3, 5, 0, NULL, NULL, NULL),
(13345, 282, 'KAMIS', 4, 37, 0, NULL, NULL, NULL),
(13346, 206, 'KAMIS', 5, 31, 0, NULL, NULL, NULL),
(13347, 206, 'KAMIS', 6, 31, 0, NULL, NULL, NULL),
(13348, 282, 'KAMIS', 7, 37, 0, NULL, NULL, NULL),
(13349, 276, 'JUMAT', 1, 5, 0, NULL, NULL, NULL),
(13350, 117, 'JUMAT', 2, 22, 0, NULL, NULL, NULL),
(13351, 117, 'JUMAT', 3, 22, 0, NULL, NULL, NULL),
(13352, 5, 'JUMAT', 4, 14, 0, NULL, NULL, NULL),
(13353, 5, 'JUMAT', 5, 14, 0, NULL, NULL, NULL),
(13354, 12, 'JUMAT', 6, 2, 0, NULL, NULL, NULL),
(13355, 122, 'SABTU', 1, 18, 0, NULL, NULL, NULL),
(13356, 122, 'SABTU', 2, 18, 0, NULL, NULL, NULL),
(13357, 12, 'SABTU', 3, 2, 0, NULL, NULL, NULL),
(13358, 12, 'SABTU', 4, 2, 0, NULL, NULL, NULL),
(13359, 239, 'SABTU', 5, 13, 0, NULL, NULL, NULL),
(13360, 239, 'SABTU', 6, 13, 0, NULL, NULL, NULL),
(13361, 227, 'SENIN', 1, 32, 0, NULL, NULL, NULL),
(13362, 227, 'SENIN', 2, 32, 0, NULL, NULL, NULL),
(13363, 227, 'SENIN', 3, 32, 0, NULL, NULL, NULL),
(13364, 227, 'SENIN', 4, 32, 0, NULL, NULL, NULL),
(13365, 207, 'SENIN', 5, 31, 0, NULL, NULL, NULL),
(13366, 159, 'SENIN', 6, 25, 0, NULL, NULL, NULL),
(13367, 159, 'SENIN', 7, 25, 0, NULL, NULL, NULL),
(13368, 284, 'SELASA', 1, 3, 0, NULL, NULL, NULL),
(13369, 284, 'SELASA', 2, 3, 0, NULL, NULL, NULL),
(13370, 288, 'SELASA', 3, 8, 0, NULL, NULL, NULL),
(13371, 288, 'SELASA', 4, 8, 0, NULL, NULL, NULL),
(13372, 286, 'SELASA', 5, 4, 0, NULL, NULL, NULL),
(13373, 286, 'SELASA', 6, 4, 0, NULL, NULL, NULL),
(13374, 286, 'SELASA', 7, 4, 0, NULL, NULL, NULL),
(13375, 59, 'RABU', 1, 19, 0, NULL, NULL, NULL),
(13376, 59, 'RABU', 2, 19, 0, NULL, NULL, NULL),
(13377, 207, 'RABU', 3, 31, 0, NULL, NULL, NULL),
(13378, 286, 'RABU', 4, 4, 0, NULL, NULL, NULL),
(13379, 286, 'RABU', 5, 4, 0, NULL, NULL, NULL),
(13380, 288, 'RABU', 6, 8, 0, NULL, NULL, NULL),
(13381, 288, 'RABU', 7, 8, 0, NULL, NULL, NULL),
(13382, 287, 'KAMIS', 1, 7, 0, NULL, NULL, NULL),
(13383, 287, 'KAMIS', 2, 7, 0, NULL, NULL, NULL),
(13384, 287, 'KAMIS', 3, 7, 0, NULL, NULL, NULL),
(13385, 289, 'KAMIS', 4, 6, 0, NULL, NULL, NULL),
(13386, 285, 'KAMIS', 5, 11, 0, NULL, NULL, NULL),
(13387, 289, 'KAMIS', 6, 6, 0, NULL, NULL, NULL),
(13388, 289, 'KAMIS', 7, 6, 0, NULL, NULL, NULL),
(13389, 163, 'JUMAT', 1, 25, 0, NULL, NULL, NULL),
(13390, 163, 'JUMAT', 2, 25, 0, NULL, NULL, NULL),
(13391, 285, 'JUMAT', 3, 11, 0, NULL, NULL, NULL),
(13392, 123, 'JUMAT', 4, 18, 0, NULL, NULL, NULL),
(13393, 283, 'JUMAT', 5, 5, 0, NULL, NULL, NULL),
(13394, 283, 'JUMAT', 6, 5, 0, NULL, NULL, NULL),
(13395, 106, 'SABTU', 1, 22, 0, NULL, NULL, NULL),
(13396, 106, 'SABTU', 2, 22, 0, NULL, NULL, NULL),
(13397, 106, 'SABTU', 3, 22, 0, NULL, NULL, NULL),
(13398, 1, 'SABTU', 4, 14, 0, NULL, NULL, NULL),
(13399, 1, 'SABTU', 5, 14, 0, NULL, NULL, NULL),
(13400, 123, 'SABTU', 6, 18, 0, NULL, NULL, NULL),
(13401, 429, 'SENIN', 1, 25, 0, NULL, NULL, NULL),
(13402, 429, 'SENIN', 2, 25, 0, NULL, NULL, NULL),
(13403, 422, 'SENIN', 3, 31, 0, NULL, NULL, NULL),
(13404, 430, 'SENIN', 4, 25, 0, NULL, NULL, NULL),
(13405, 430, 'SENIN', 5, 25, 0, NULL, NULL, NULL),
(13406, 418, 'SENIN', 6, 32, 0, NULL, NULL, NULL),
(13407, 418, 'SENIN', 7, 32, 0, NULL, NULL, NULL),
(13408, 427, 'SELASA', 1, 8, 0, NULL, NULL, NULL),
(13409, 427, 'SELASA', 2, 8, 0, NULL, NULL, NULL),
(13410, 426, 'SELASA', 3, 7, 0, NULL, NULL, NULL),
(13411, 426, 'SELASA', 4, 7, 0, NULL, NULL, NULL),
(13412, 426, 'SELASA', 5, 7, 0, NULL, NULL, NULL),
(13413, 425, 'SELASA', 6, 3, 0, NULL, NULL, NULL),
(13414, 425, 'SELASA', 7, 3, 0, NULL, NULL, NULL),
(13415, 416, 'RABU', 1, 4, 0, NULL, NULL, NULL),
(13416, 416, 'RABU', 2, 4, 0, NULL, NULL, NULL),
(13417, 416, 'RABU', 3, 4, 0, NULL, NULL, NULL),
(13418, 427, 'RABU', 4, 8, 0, NULL, NULL, NULL),
(13419, 427, 'RABU', 5, 8, 0, NULL, NULL, NULL),
(13420, 416, 'RABU', 6, 4, 0, NULL, NULL, NULL),
(13421, 416, 'RABU', 7, 4, 0, NULL, NULL, NULL),
(13422, 420, 'KAMIS', 1, 6, 0, NULL, NULL, NULL),
(13423, 420, 'KAMIS', 2, 6, 0, NULL, NULL, NULL),
(13424, 420, 'KAMIS', 3, 6, 0, NULL, NULL, NULL),
(13425, 419, 'KAMIS', 4, 5, 0, NULL, NULL, NULL),
(13426, 419, 'KAMIS', 5, 5, 0, NULL, NULL, NULL),
(13427, 418, 'KAMIS', 6, 32, 0, NULL, NULL, NULL),
(13428, 418, 'KAMIS', 7, 32, 0, NULL, NULL, NULL),
(13429, 417, 'JUMAT', 1, 22, 0, NULL, NULL, NULL),
(13430, 424, 'JUMAT', 2, 19, 0, NULL, NULL, NULL),
(13431, 424, 'JUMAT', 3, 19, 0, NULL, NULL, NULL),
(13432, 422, 'JUMAT', 4, 31, 0, NULL, NULL, NULL),
(13433, 421, 'JUMAT', 5, 11, 0, NULL, NULL, NULL),
(13434, 421, 'JUMAT', 6, 11, 0, NULL, NULL, NULL),
(13435, 428, 'SABTU', 1, 14, 0, NULL, NULL, NULL),
(13436, 428, 'SABTU', 2, 14, 0, NULL, NULL, NULL),
(13437, 423, 'SABTU', 3, 18, 0, NULL, NULL, NULL),
(13438, 423, 'SABTU', 4, 18, 0, NULL, NULL, NULL),
(13439, 417, 'SABTU', 5, 22, 0, NULL, NULL, NULL),
(13440, 417, 'SABTU', 6, 22, 0, NULL, NULL, NULL),
(13441, 13, 'SENIN', 1, 15, 0, NULL, NULL, NULL),
(13442, 13, 'SENIN', 2, 15, 0, NULL, NULL, NULL),
(13443, 13, 'SENIN', 3, 15, 0, NULL, NULL, NULL),
(13444, 64, 'SENIN', 4, 19, 0, NULL, NULL, NULL),
(13445, 64, 'SENIN', 5, 19, 0, NULL, NULL, NULL),
(13446, 310, 'SENIN', 6, 12, 0, NULL, NULL, NULL),
(13447, 310, 'SENIN', 7, 12, 0, NULL, NULL, NULL),
(13448, 312, 'SELASA', 1, 6, 0, NULL, NULL, NULL),
(13449, 312, 'SELASA', 2, 6, 0, NULL, NULL, NULL),
(13450, 312, 'SELASA', 3, 6, 0, NULL, NULL, NULL),
(13451, 48, 'SELASA', 4, 38, 0, NULL, NULL, NULL),
(13452, 25, 'SELASA', 5, 20, 0, NULL, NULL, NULL),
(13453, 25, 'SELASA', 6, 20, 0, NULL, NULL, NULL),
(13454, 13, 'SELASA', 7, 15, 0, NULL, NULL, NULL),
(13455, 25, 'RABU', 1, 20, 0, NULL, NULL, NULL),
(13456, 25, 'RABU', 2, 20, 0, NULL, NULL, NULL),
(13457, 311, 'RABU', 3, 9, 0, NULL, NULL, NULL),
(13458, 311, 'RABU', 4, 9, 0, NULL, NULL, NULL),
(13459, 212, 'RABU', 5, 31, 0, NULL, NULL, NULL),
(13460, 212, 'RABU', 6, 31, 0, NULL, NULL, NULL),
(13461, 48, 'RABU', 7, 38, 0, NULL, NULL, NULL),
(13462, 241, 'KAMIS', 1, 34, 0, NULL, NULL, NULL),
(13463, 241, 'KAMIS', 2, 34, 0, NULL, NULL, NULL),
(13464, 241, 'KAMIS', 3, 34, 0, NULL, NULL, NULL),
(13465, 29, 'KAMIS', 4, 16, 0, NULL, NULL, NULL),
(13466, 29, 'KAMIS', 5, 16, 0, NULL, NULL, NULL),
(13467, 29, 'KAMIS', 6, 16, 0, NULL, NULL, NULL),
(13468, 29, 'KAMIS', 7, 16, 0, NULL, NULL, NULL),
(13469, 13, 'JUMAT', 1, 15, 0, NULL, NULL, NULL),
(13470, 20, 'JUMAT', 2, 35, 0, NULL, NULL, NULL),
(13471, 20, 'JUMAT', 3, 35, 0, NULL, NULL, NULL),
(13472, 20, 'JUMAT', 4, 35, 0, NULL, NULL, NULL),
(13473, 35, 'JUMAT', 5, 17, 0, NULL, NULL, NULL),
(13474, 35, 'JUMAT', 6, 17, 0, NULL, NULL, NULL),
(13475, 72, 'SABTU', 1, 30, 0, NULL, NULL, NULL),
(13476, 72, 'SABTU', 2, 30, 0, NULL, NULL, NULL),
(13477, 35, 'SABTU', 3, 17, 0, NULL, NULL, NULL),
(13478, 35, 'SABTU', 4, 17, 0, NULL, NULL, NULL),
(13479, 20, 'SABTU', 5, 35, 0, NULL, NULL, NULL),
(13480, 20, 'SABTU', 6, 35, 0, NULL, NULL, NULL),
(13481, 499, 'SENIN', 1, 31, 0, NULL, NULL, NULL),
(13482, 499, 'SENIN', 2, 31, 0, NULL, NULL, NULL),
(13483, 503, 'SENIN', 3, 35, 0, NULL, NULL, NULL),
(13484, 503, 'SENIN', 4, 35, 0, NULL, NULL, NULL),
(13485, 503, 'SENIN', 5, 35, 0, NULL, NULL, NULL),
(13486, 503, 'SENIN', 6, 35, 0, NULL, NULL, NULL),
(13487, 501, 'SENIN', 7, 19, 0, NULL, NULL, NULL),
(13488, 493, 'SELASA', 1, 15, 0, NULL, NULL, NULL),
(13489, 493, 'SELASA', 2, 15, 0, NULL, NULL, NULL),
(13490, 493, 'SELASA', 3, 15, 0, NULL, NULL, NULL),
(13491, 494, 'SELASA', 4, 34, 0, NULL, NULL, NULL),
(13492, 497, 'SELASA', 5, 6, 0, NULL, NULL, NULL),
(13493, 497, 'SELASA', 6, 6, 0, NULL, NULL, NULL),
(13494, 497, 'SELASA', 7, 6, 0, NULL, NULL, NULL),
(13495, 502, 'RABU', 1, 9, 0, NULL, NULL, NULL),
(13496, 502, 'RABU', 2, 9, 0, NULL, NULL, NULL),
(13497, 504, 'RABU', 3, 35, 0, NULL, NULL, NULL),
(13498, 504, 'RABU', 4, 35, 0, NULL, NULL, NULL),
(13499, 504, 'RABU', 5, 35, 0, NULL, NULL, NULL),
(13500, 504, 'RABU', 6, 35, 0, NULL, NULL, NULL),
(13501, 504, 'RABU', 7, 35, 0, NULL, NULL, NULL),
(13502, 493, 'KAMIS', 1, 15, 0, NULL, NULL, NULL),
(13503, 493, 'KAMIS', 2, 15, 0, NULL, NULL, NULL),
(13504, 495, 'KAMIS', 3, 17, 0, NULL, NULL, NULL),
(13505, 496, 'KAMIS', 4, 12, 0, NULL, NULL, NULL),
(13506, 496, 'KAMIS', 5, 12, 0, NULL, NULL, NULL),
(13507, 505, 'KAMIS', 6, 20, 0, NULL, NULL, NULL),
(13508, 505, 'KAMIS', 7, 20, 0, NULL, NULL, NULL),
(13509, 501, 'JUMAT', 1, 19, 0, NULL, NULL, NULL),
(13510, 495, 'JUMAT', 2, 17, 0, NULL, NULL, NULL),
(13511, 495, 'JUMAT', 3, 17, 0, NULL, NULL, NULL),
(13512, 495, 'JUMAT', 4, 17, 0, NULL, NULL, NULL),
(13513, 494, 'JUMAT', 5, 34, 0, NULL, NULL, NULL),
(13514, 494, 'JUMAT', 6, 34, 0, NULL, NULL, NULL),
(13515, 500, 'SABTU', 1, 38, 0, NULL, NULL, NULL),
(13516, 500, 'SABTU', 2, 38, 0, NULL, NULL, NULL),
(13517, 505, 'SABTU', 3, 20, 0, NULL, NULL, NULL),
(13518, 505, 'SABTU', 4, 20, 0, NULL, NULL, NULL),
(13519, 498, 'SABTU', 5, 30, 0, NULL, NULL, NULL),
(13520, 498, 'SABTU', 6, 30, 0, NULL, NULL, NULL),
(13521, 301, 'SENIN', 1, 11, 0, NULL, NULL, NULL),
(13522, 132, 'SENIN', 2, 23, 0, NULL, NULL, NULL),
(13523, 132, 'SENIN', 3, 23, 0, NULL, NULL, NULL),
(13524, 132, 'SENIN', 4, 23, 0, NULL, NULL, NULL),
(13525, 148, 'SENIN', 5, 24, 0, NULL, NULL, NULL),
(13526, 148, 'SENIN', 6, 24, 0, NULL, NULL, NULL),
(13527, 148, 'SENIN', 7, 24, 0, NULL, NULL, NULL),
(13528, 108, 'SELASA', 1, 22, 0, NULL, NULL, NULL),
(13529, 108, 'SELASA', 2, 22, 0, NULL, NULL, NULL),
(13530, 301, 'SELASA', 3, 11, 0, NULL, NULL, NULL),
(13531, 301, 'SELASA', 4, 11, 0, NULL, NULL, NULL),
(13532, 169, 'SELASA', 5, 26, 0, NULL, NULL, NULL),
(13533, 169, 'SELASA', 6, 26, 0, NULL, NULL, NULL),
(13534, 169, 'SELASA', 7, 26, 0, NULL, NULL, NULL),
(13535, 209, 'RABU', 1, 31, 0, NULL, NULL, NULL),
(13536, 209, 'RABU', 2, 31, 0, NULL, NULL, NULL),
(13537, 297, 'RABU', 3, 27, 0, NULL, NULL, NULL),
(13538, 297, 'RABU', 4, 27, 0, NULL, NULL, NULL),
(13539, 61, 'RABU', 5, 19, 0, NULL, NULL, NULL),
(13540, 61, 'RABU', 6, 19, 0, NULL, NULL, NULL),
(13541, 169, 'RABU', 7, 26, 0, NULL, NULL, NULL),
(13542, 134, 'KAMIS', 1, 23, 0, NULL, NULL, NULL),
(13543, 134, 'KAMIS', 2, 23, 0, NULL, NULL, NULL),
(13544, 134, 'KAMIS', 3, 23, 0, NULL, NULL, NULL),
(13545, 134, 'KAMIS', 4, 23, 0, NULL, NULL, NULL),
(13546, 300, 'KAMIS', 5, 2, 0, NULL, NULL, NULL),
(13547, 300, 'KAMIS', 6, 2, 0, NULL, NULL, NULL),
(13548, 300, 'KAMIS', 7, 2, 0, NULL, NULL, NULL),
(13549, 299, 'JUMAT', 1, 11, 0, NULL, NULL, NULL),
(13550, 299, 'JUMAT', 2, 11, 0, NULL, NULL, NULL),
(13551, 298, 'JUMAT', 3, 10, 0, NULL, NULL, NULL),
(13552, 298, 'JUMAT', 4, 10, 0, NULL, NULL, NULL),
(13553, 45, 'JUMAT', 5, 18, 0, NULL, NULL, NULL),
(13554, 45, 'JUMAT', 6, 18, 0, NULL, NULL, NULL),
(13555, 146, 'SABTU', 1, 24, 0, NULL, NULL, NULL),
(13556, 146, 'SABTU', 2, 24, 0, NULL, NULL, NULL),
(13557, 146, 'SABTU', 3, 24, 0, NULL, NULL, NULL),
(13558, 108, 'SABTU', 4, 22, 0, NULL, NULL, NULL),
(13559, 300, 'SABTU', 5, 2, 0, NULL, NULL, NULL),
(13560, 300, 'SABTU', 6, 2, 0, NULL, NULL, NULL),
(13561, 305, 'SENIN', 1, 2, 0, NULL, NULL, NULL),
(13562, 305, 'SENIN', 2, 2, 0, NULL, NULL, NULL),
(13563, 304, 'SENIN', 3, 11, 0, NULL, NULL, NULL),
(13564, 304, 'SENIN', 4, 11, 0, NULL, NULL, NULL),
(13565, 133, 'SENIN', 5, 23, 0, NULL, NULL, NULL),
(13566, 133, 'SENIN', 6, 23, 0, NULL, NULL, NULL),
(13567, 133, 'SENIN', 7, 23, 0, NULL, NULL, NULL),
(13568, 170, 'SELASA', 1, 26, 0, NULL, NULL, NULL),
(13569, 170, 'SELASA', 2, 26, 0, NULL, NULL, NULL),
(13570, 109, 'SELASA', 3, 22, 0, NULL, NULL, NULL),
(13571, 109, 'SELASA', 4, 22, 0, NULL, NULL, NULL),
(13572, 306, 'SELASA', 5, 11, 0, NULL, NULL, NULL),
(13573, 306, 'SELASA', 6, 11, 0, NULL, NULL, NULL),
(13574, 306, 'SELASA', 7, 11, 0, NULL, NULL, NULL),
(13575, 302, 'RABU', 1, 27, 0, NULL, NULL, NULL),
(13576, 302, 'RABU', 2, 27, 0, NULL, NULL, NULL),
(13577, 62, 'RABU', 3, 19, 0, NULL, NULL, NULL),
(13578, 62, 'RABU', 4, 19, 0, NULL, NULL, NULL),
(13579, 170, 'RABU', 5, 26, 0, NULL, NULL, NULL),
(13580, 170, 'RABU', 6, 26, 0, NULL, NULL, NULL),
(13581, 210, 'RABU', 7, 31, 0, NULL, NULL, NULL),
(13582, 109, 'KAMIS', 1, 22, 0, NULL, NULL, NULL),
(13583, 46, 'KAMIS', 2, 18, 0, NULL, NULL, NULL),
(13584, 46, 'KAMIS', 3, 18, 0, NULL, NULL, NULL),
(13585, 210, 'KAMIS', 4, 31, 0, NULL, NULL, NULL),
(13586, 147, 'KAMIS', 5, 24, 0, NULL, NULL, NULL),
(13587, 147, 'KAMIS', 6, 24, 0, NULL, NULL, NULL),
(13588, 147, 'KAMIS', 7, 24, 0, NULL, NULL, NULL),
(13589, 305, 'JUMAT', 1, 2, 0, NULL, NULL, NULL),
(13590, 305, 'JUMAT', 2, 2, 0, NULL, NULL, NULL),
(13591, 305, 'JUMAT', 3, 2, 0, NULL, NULL, NULL),
(13592, 149, 'JUMAT', 4, 24, 0, NULL, NULL, NULL),
(13593, 149, 'JUMAT', 5, 24, 0, NULL, NULL, NULL),
(13594, 149, 'JUMAT', 6, 24, 0, NULL, NULL, NULL),
(13595, 303, 'SABTU', 1, 10, 0, NULL, NULL, NULL),
(13596, 303, 'SABTU', 2, 10, 0, NULL, NULL, NULL),
(13597, 135, 'SABTU', 3, 23, 0, NULL, NULL, NULL),
(13598, 135, 'SABTU', 4, 23, 0, NULL, NULL, NULL),
(13599, 135, 'SABTU', 5, 23, 0, NULL, NULL, NULL),
(13600, 135, 'SABTU', 6, 23, 0, NULL, NULL, NULL),
(13601, 308, 'SENIN', 1, 10, 0, NULL, NULL, NULL),
(13602, 308, 'SENIN', 2, 10, 0, NULL, NULL, NULL),
(13603, 237, 'SENIN', 3, 33, 0, NULL, NULL, NULL),
(13604, 237, 'SENIN', 4, 33, 0, NULL, NULL, NULL),
(13605, 309, 'SENIN', 5, 11, 0, NULL, NULL, NULL),
(13606, 71, 'SENIN', 6, 31, 0, NULL, NULL, NULL),
(13607, 71, 'SENIN', 7, 31, 0, NULL, NULL, NULL),
(13608, 431, 'SELASA', 1, 16, 0, NULL, NULL, NULL),
(13609, 431, 'SELASA', 2, 16, 0, NULL, NULL, NULL),
(13610, 34, 'SELASA', 3, 17, 0, NULL, NULL, NULL),
(13611, 34, 'SELASA', 4, 17, 0, NULL, NULL, NULL),
(13612, 34, 'SELASA', 5, 17, 0, NULL, NULL, NULL),
(13613, 47, 'SELASA', 6, 38, 0, NULL, NULL, NULL),
(13614, 47, 'SELASA', 7, 38, 0, NULL, NULL, NULL),
(13615, 431, 'RABU', 1, 16, 0, NULL, NULL, NULL),
(13616, 431, 'RABU', 2, 16, 0, NULL, NULL, NULL),
(13617, 431, 'RABU', 3, 16, 0, NULL, NULL, NULL),
(13618, 240, 'RABU', 4, 13, 0, NULL, NULL, NULL),
(13619, 240, 'RABU', 5, 13, 0, NULL, NULL, NULL),
(13620, 240, 'RABU', 6, 13, 0, NULL, NULL, NULL),
(13621, 63, 'RABU', 7, 19, 0, NULL, NULL, NULL),
(13622, 237, 'KAMIS', 1, 33, 0, NULL, NULL, NULL),
(13623, 237, 'KAMIS', 2, 33, 0, NULL, NULL, NULL),
(13624, 237, 'KAMIS', 3, 33, 0, NULL, NULL, NULL),
(13625, 506, 'KAMIS', 4, 20, 0, NULL, NULL, NULL),
(13626, 506, 'KAMIS', 5, 20, 0, NULL, NULL, NULL),
(13627, 309, 'KAMIS', 6, 11, 0, NULL, NULL, NULL),
(13628, 309, 'KAMIS', 7, 11, 0, NULL, NULL, NULL),
(13629, 34, 'JUMAT', 1, 17, 0, NULL, NULL, NULL),
(13630, 85, 'JUMAT', 2, 20, 0, NULL, NULL, NULL),
(13631, 85, 'JUMAT', 3, 20, 0, NULL, NULL, NULL),
(13632, 63, 'JUMAT', 4, 19, 0, NULL, NULL, NULL),
(13633, 211, 'JUMAT', 5, 31, 0, NULL, NULL, NULL),
(13634, 211, 'JUMAT', 6, 31, 0, NULL, NULL, NULL),
(13635, 85, 'SABTU', 1, 20, 0, NULL, NULL, NULL),
(13636, 85, 'SABTU', 2, 20, 0, NULL, NULL, NULL),
(13637, 307, 'SABTU', 3, 12, 0, NULL, NULL, NULL),
(13638, 307, 'SABTU', 4, 12, 0, NULL, NULL, NULL),
(13639, 506, 'SABTU', 5, 20, 0, NULL, NULL, NULL),
(13640, 506, 'SABTU', 6, 20, 0, NULL, NULL, NULL),
(13641, 318, 'SENIN', 2, 31, 0, NULL, NULL, NULL),
(13642, 15, 'SENIN', 3, 2, 0, NULL, NULL, NULL),
(13643, 15, 'SENIN', 4, 2, 0, NULL, NULL, NULL),
(13644, 15, 'SENIN', 5, 2, 0, NULL, NULL, NULL),
(13645, 316, 'SENIN', 6, 5, 0, NULL, NULL, NULL),
(13646, 15, 'SENIN', 7, 2, 0, NULL, NULL, NULL),
(13647, 318, 'SELASA', 1, 31, 0, NULL, NULL, NULL),
(13648, 321, 'SELASA', 2, 22, 0, NULL, NULL, NULL),
(13649, 321, 'SELASA', 3, 22, 0, NULL, NULL, NULL),
(13650, 320, 'SELASA', 4, 7, 0, NULL, NULL, NULL),
(13651, 320, 'SELASA', 5, 7, 0, NULL, NULL, NULL),
(13652, 317, 'SELASA', 6, 3, 0, NULL, NULL, NULL),
(13653, 317, 'SELASA', 7, 3, 0, NULL, NULL, NULL),
(13654, 445, 'RABU', 1, 7, 0, NULL, NULL, NULL),
(13655, 445, 'RABU', 2, 7, 0, NULL, NULL, NULL),
(13656, 214, 'RABU', 3, 39, 0, NULL, NULL, NULL),
(13657, 243, 'RABU', 4, 34, 0, NULL, NULL, NULL),
(13658, 243, 'RABU', 5, 34, 0, NULL, NULL, NULL),
(13659, 243, 'RABU', 6, 34, 0, NULL, NULL, NULL),
(13660, 214, 'RABU', 7, 39, 0, NULL, NULL, NULL),
(13661, 319, 'KAMIS', 1, 7, 0, NULL, NULL, NULL),
(13662, 319, 'KAMIS', 2, 7, 0, NULL, NULL, NULL),
(13663, 319, 'KAMIS', 3, 7, 0, NULL, NULL, NULL),
(13664, 319, 'KAMIS', 4, 7, 0, NULL, NULL, NULL),
(13665, 322, 'KAMIS', 5, 6, 0, NULL, NULL, NULL),
(13666, 322, 'KAMIS', 6, 6, 0, NULL, NULL, NULL),
(13667, 322, 'KAMIS', 7, 6, 0, NULL, NULL, NULL),
(13668, 37, 'JUMAT', 1, 17, 0, NULL, NULL, NULL),
(13669, 37, 'JUMAT', 2, 17, 0, NULL, NULL, NULL),
(13670, 6, 'JUMAT', 3, 14, 0, NULL, NULL, NULL),
(13671, 6, 'JUMAT', 4, 14, 0, NULL, NULL, NULL),
(13672, 37, 'JUMAT', 5, 17, 0, NULL, NULL, NULL),
(13673, 37, 'JUMAT', 6, 17, 0, NULL, NULL, NULL),
(13674, 196, 'SABTU', 1, 30, 0, NULL, NULL, NULL),
(13675, 196, 'SABTU', 2, 30, 0, NULL, NULL, NULL),
(13676, 196, 'SABTU', 3, 30, 0, NULL, NULL, NULL),
(13677, 125, 'SABTU', 4, 18, 0, NULL, NULL, NULL),
(13678, 125, 'SABTU', 5, 18, 0, NULL, NULL, NULL),
(13679, 316, 'SABTU', 6, 5, 0, NULL, NULL, NULL),
(13680, 15, 'SABTU', 7, 2, 0, NULL, NULL, NULL),
(13681, 490, 'SENIN', 2, 25, 0, NULL, NULL, NULL),
(13682, 490, 'SENIN', 3, 25, 0, NULL, NULL, NULL),
(13683, 329, 'SENIN', 4, 11, 0, NULL, NULL, NULL),
(13684, 329, 'SENIN', 5, 11, 0, NULL, NULL, NULL),
(13685, 326, 'SENIN', 6, 15, 0, NULL, NULL, NULL),
(13686, 326, 'SENIN', 7, 15, 0, NULL, NULL, NULL),
(13687, 446, 'SELASA', 1, 7, 0, NULL, NULL, NULL),
(13688, 446, 'SELASA', 2, 7, 0, NULL, NULL, NULL),
(13689, 324, 'SELASA', 3, 3, 0, NULL, NULL, NULL),
(13690, 324, 'SELASA', 4, 3, 0, NULL, NULL, NULL),
(13691, 126, 'SELASA', 5, 38, 0, NULL, NULL, NULL),
(13692, 215, 'SELASA', 6, 31, 0, NULL, NULL, NULL),
(13693, 215, 'SELASA', 7, 31, 0, NULL, NULL, NULL),
(13694, 126, 'RABU', 1, 38, 0, NULL, NULL, NULL),
(13695, 328, 'RABU', 2, 8, 0, NULL, NULL, NULL),
(13696, 328, 'RABU', 3, 8, 0, NULL, NULL, NULL),
(13697, 328, 'RABU', 4, 8, 0, NULL, NULL, NULL),
(13698, 328, 'RABU', 5, 8, 0, NULL, NULL, NULL),
(13699, 326, 'RABU', 6, 15, 0, NULL, NULL, NULL),
(13700, 326, 'RABU', 7, 15, 0, NULL, NULL, NULL),
(13701, 329, 'KAMIS', 1, 11, 0, NULL, NULL, NULL),
(13702, 38, 'KAMIS', 2, 17, 0, NULL, NULL, NULL),
(13703, 38, 'KAMIS', 3, 17, 0, NULL, NULL, NULL),
(13704, 161, 'KAMIS', 4, 25, 0, NULL, NULL, NULL),
(13705, 161, 'KAMIS', 5, 25, 0, NULL, NULL, NULL),
(13706, 323, 'KAMIS', 6, 5, 0, NULL, NULL, NULL),
(13707, 323, 'KAMIS', 7, 5, 0, NULL, NULL, NULL),
(13708, 326, 'JUMAT', 1, 15, 0, NULL, NULL, NULL),
(13709, 325, 'JUMAT', 2, 30, 0, NULL, NULL, NULL),
(13710, 325, 'JUMAT', 3, 30, 0, NULL, NULL, NULL),
(13711, 244, 'JUMAT', 4, 34, 0, NULL, NULL, NULL),
(13712, 244, 'JUMAT', 5, 34, 0, NULL, NULL, NULL),
(13713, 244, 'JUMAT', 6, 34, 0, NULL, NULL, NULL),
(13714, 38, 'SABTU', 1, 17, 0, NULL, NULL, NULL),
(13715, 38, 'SABTU', 2, 17, 0, NULL, NULL, NULL),
(13716, 3, 'SABTU', 3, 14, 0, NULL, NULL, NULL),
(13717, 3, 'SABTU', 4, 14, 0, NULL, NULL, NULL),
(13718, 327, 'SABTU', 5, 7, 0, NULL, NULL, NULL),
(13719, 327, 'SABTU', 6, 7, 0, NULL, NULL, NULL),
(13720, 327, 'SABTU', 7, 7, 0, NULL, NULL, NULL),
(13721, 454, 'SENIN', 2, 38, 0, NULL, NULL, NULL),
(13722, 447, 'SENIN', 3, 15, 0, NULL, NULL, NULL),
(13723, 460, 'SENIN', 4, 25, 0, NULL, NULL, NULL),
(13724, 460, 'SENIN', 5, 25, 0, NULL, NULL, NULL),
(13725, 460, 'SENIN', 6, 25, 0, NULL, NULL, NULL),
(13726, 460, 'SENIN', 7, 25, 0, NULL, NULL, NULL),
(13727, 455, 'SELASA', 1, 3, 0, NULL, NULL, NULL),
(13728, 455, 'SELASA', 2, 3, 0, NULL, NULL, NULL),
(13729, 454, 'SELASA', 3, 38, 0, NULL, NULL, NULL),
(13730, 458, 'SELASA', 4, 8, 0, NULL, NULL, NULL),
(13731, 458, 'SELASA', 5, 8, 0, NULL, NULL, NULL),
(13732, 458, 'SELASA', 6, 8, 0, NULL, NULL, NULL),
(13733, 458, 'SELASA', 7, 8, 0, NULL, NULL, NULL),
(13734, 448, 'RABU', 1, 34, 0, NULL, NULL, NULL),
(13735, 448, 'RABU', 2, 34, 0, NULL, NULL, NULL),
(13736, 448, 'RABU', 3, 34, 0, NULL, NULL, NULL),
(13737, 447, 'RABU', 4, 15, 0, NULL, NULL, NULL),
(13738, 447, 'RABU', 5, 15, 0, NULL, NULL, NULL),
(13739, 453, 'RABU', 6, 31, 0, NULL, NULL, NULL),
(13740, 453, 'RABU', 7, 31, 0, NULL, NULL, NULL),
(13741, 449, 'KAMIS', 1, 17, 0, NULL, NULL, NULL),
(13742, 451, 'KAMIS', 2, 11, 0, NULL, NULL, NULL),
(13743, 451, 'KAMIS', 3, 11, 0, NULL, NULL, NULL),
(13744, 451, 'KAMIS', 4, 11, 0, NULL, NULL, NULL),
(13745, 456, 'KAMIS', 5, 7, 0, NULL, NULL, NULL),
(13746, 456, 'KAMIS', 6, 7, 0, NULL, NULL, NULL),
(13747, 456, 'KAMIS', 7, 7, 0, NULL, NULL, NULL),
(13748, 457, 'JUMAT', 1, 7, 0, NULL, NULL, NULL),
(13749, 457, 'JUMAT', 2, 7, 0, NULL, NULL, NULL),
(13750, 450, 'JUMAT', 3, 5, 0, NULL, NULL, NULL),
(13751, 450, 'JUMAT', 4, 5, 0, NULL, NULL, NULL),
(13752, 447, 'JUMAT', 5, 15, 0, NULL, NULL, NULL),
(13753, 447, 'JUMAT', 6, 15, 0, NULL, NULL, NULL),
(13754, 459, 'SABTU', 1, 14, 0, NULL, NULL, NULL),
(13755, 459, 'SABTU', 2, 14, 0, NULL, NULL, NULL),
(13756, 449, 'SABTU', 3, 17, 0, NULL, NULL, NULL),
(13757, 449, 'SABTU', 4, 17, 0, NULL, NULL, NULL),
(13758, 449, 'SABTU', 5, 17, 0, NULL, NULL, NULL),
(13759, 452, 'SABTU', 6, 30, 0, NULL, NULL, NULL),
(13760, 452, 'SABTU', 7, 30, 0, NULL, NULL, NULL),
(13761, 31, 'SENIN', 2, 35, 0, NULL, NULL, NULL),
(13762, 31, 'SENIN', 3, 35, 0, NULL, NULL, NULL),
(13763, 31, 'SENIN', 4, 35, 0, NULL, NULL, NULL),
(13764, 54, 'SENIN', 5, 18, 0, NULL, NULL, NULL),
(13765, 54, 'SENIN', 6, 18, 0, NULL, NULL, NULL),
(13766, 176, 'SENIN', 7, 27, 0, NULL, NULL, NULL),
(13767, 22, 'SELASA', 1, 20, 0, NULL, NULL, NULL),
(13768, 22, 'SELASA', 2, 20, 0, NULL, NULL, NULL),
(13769, 22, 'SELASA', 3, 20, 0, NULL, NULL, NULL),
(13770, 22, 'SELASA', 4, 20, 0, NULL, NULL, NULL),
(13771, 22, 'SELASA', 5, 20, 0, NULL, NULL, NULL),
(13772, 352, 'SELASA', 6, 6, 0, NULL, NULL, NULL),
(13773, 352, 'SELASA', 7, 6, 0, NULL, NULL, NULL),
(13774, 176, 'RABU', 1, 27, 0, NULL, NULL, NULL),
(13775, 231, 'RABU', 2, 32, 0, NULL, NULL, NULL),
(13776, 231, 'RABU', 3, 32, 0, NULL, NULL, NULL),
(13777, 231, 'RABU', 4, 32, 0, NULL, NULL, NULL),
(13778, 231, 'RABU', 5, 32, 0, NULL, NULL, NULL),
(13779, 31, 'RABU', 6, 35, 0, NULL, NULL, NULL),
(13780, 31, 'RABU', 7, 35, 0, NULL, NULL, NULL),
(13781, 27, 'KAMIS', 1, 16, 0, NULL, NULL, NULL),
(13782, 27, 'KAMIS', 2, 16, 0, NULL, NULL, NULL),
(13783, 27, 'KAMIS', 3, 16, 0, NULL, NULL, NULL),
(13784, 27, 'KAMIS', 4, 16, 0, NULL, NULL, NULL),
(13785, 27, 'KAMIS', 5, 16, 0, NULL, NULL, NULL),
(13786, 221, 'KAMIS', 6, 31, 0, NULL, NULL, NULL),
(13787, 221, 'KAMIS', 7, 31, 0, NULL, NULL, NULL),
(13788, 76, 'JUMAT', 1, 31, 0, NULL, NULL, NULL),
(13789, 76, 'JUMAT', 2, 31, 0, NULL, NULL, NULL),
(13790, 351, 'JUMAT', 3, 15, 0, NULL, NULL, NULL),
(13791, 351, 'JUMAT', 4, 15, 0, NULL, NULL, NULL),
(13792, 114, 'JUMAT', 5, 22, 0, NULL, NULL, NULL),
(13793, 114, 'JUMAT', 6, 22, 0, NULL, NULL, NULL),
(13794, 351, 'SABTU', 1, 15, 0, NULL, NULL, NULL),
(13795, 114, 'SABTU', 2, 22, 0, NULL, NULL, NULL),
(13796, 350, 'SABTU', 3, 10, 0, NULL, NULL, NULL),
(13797, 350, 'SABTU', 4, 10, 0, NULL, NULL, NULL),
(13798, 352, 'SABTU', 5, 6, 0, NULL, NULL, NULL),
(13799, 351, 'SABTU', 6, 15, 0, NULL, NULL, NULL),
(13800, 351, 'SABTU', 7, 15, 0, NULL, NULL, NULL),
(13801, 354, 'SENIN', 2, 15, 0, NULL, NULL, NULL),
(13802, 23, 'SENIN', 3, 20, 0, NULL, NULL, NULL),
(13803, 23, 'SENIN', 4, 20, 0, NULL, NULL, NULL),
(13804, 23, 'SENIN', 5, 20, 0, NULL, NULL, NULL),
(13805, 23, 'SENIN', 6, 20, 0, NULL, NULL, NULL),
(13806, 23, 'SENIN', 7, 20, 0, NULL, NULL, NULL),
(13807, 28, 'SELASA', 1, 16, 0, NULL, NULL, NULL),
(13808, 28, 'SELASA', 2, 16, 0, NULL, NULL, NULL),
(13809, 28, 'SELASA', 3, 16, 0, NULL, NULL, NULL),
(13810, 28, 'SELASA', 4, 16, 0, NULL, NULL, NULL),
(13811, 28, 'SELASA', 5, 16, 0, NULL, NULL, NULL),
(13812, 232, 'SELASA', 6, 32, 0, NULL, NULL, NULL),
(13813, 232, 'SELASA', 7, 32, 0, NULL, NULL, NULL),
(13814, 32, 'RABU', 1, 35, 0, NULL, NULL, NULL),
(13815, 32, 'RABU', 2, 35, 0, NULL, NULL, NULL),
(13816, 32, 'RABU', 3, 35, 0, NULL, NULL, NULL),
(13817, 177, 'RABU', 4, 27, 0, NULL, NULL, NULL),
(13818, 177, 'RABU', 5, 27, 0, NULL, NULL, NULL),
(13819, 232, 'RABU', 6, 32, 0, NULL, NULL, NULL),
(13820, 232, 'RABU', 7, 32, 0, NULL, NULL, NULL),
(13821, 354, 'KAMIS', 1, 15, 0, NULL, NULL, NULL),
(13822, 222, 'KAMIS', 2, 31, 0, NULL, NULL, NULL),
(13823, 222, 'KAMIS', 3, 31, 0, NULL, NULL, NULL),
(13824, 355, 'KAMIS', 4, 6, 0, NULL, NULL, NULL),
(13825, 354, 'KAMIS', 5, 15, 0, NULL, NULL, NULL),
(13826, 354, 'KAMIS', 6, 15, 0, NULL, NULL, NULL),
(13827, 354, 'KAMIS', 7, 15, 0, NULL, NULL, NULL),
(13828, 55, 'JUMAT', 1, 18, 0, NULL, NULL, NULL),
(13829, 55, 'JUMAT', 2, 18, 0, NULL, NULL, NULL),
(13830, 77, 'JUMAT', 3, 31, 0, NULL, NULL, NULL),
(13831, 77, 'JUMAT', 4, 31, 0, NULL, NULL, NULL),
(13832, 32, 'JUMAT', 5, 35, 0, NULL, NULL, NULL),
(13833, 32, 'JUMAT', 6, 35, 0, NULL, NULL, NULL),
(13834, 353, 'SABTU', 1, 10, 0, NULL, NULL, NULL),
(13835, 353, 'SABTU', 2, 10, 0, NULL, NULL, NULL),
(13836, 115, 'SABTU', 3, 22, 0, NULL, NULL, NULL),
(13837, 115, 'SABTU', 4, 22, 0, NULL, NULL, NULL),
(13838, 115, 'SABTU', 5, 22, 0, NULL, NULL, NULL),
(13839, 355, 'SABTU', 6, 6, 0, NULL, NULL, NULL),
(13840, 355, 'SABTU', 7, 6, 0, NULL, NULL, NULL),
(13841, 339, 'SENIN', 2, 27, 0, NULL, NULL, NULL),
(13842, 340, 'SENIN', 3, 11, 0, NULL, NULL, NULL),
(13843, 136, 'SENIN', 4, 23, 0, NULL, NULL, NULL),
(13844, 136, 'SENIN', 5, 23, 0, NULL, NULL, NULL),
(13845, 136, 'SENIN', 6, 23, 0, NULL, NULL, NULL),
(13846, 136, 'SENIN', 7, 23, 0, NULL, NULL, NULL),
(13847, 40, 'SELASA', 1, 17, 0, NULL, NULL, NULL),
(13848, 40, 'SELASA', 2, 17, 0, NULL, NULL, NULL),
(13849, 40, 'SELASA', 3, 17, 0, NULL, NULL, NULL),
(13850, 217, 'SELASA', 4, 31, 0, NULL, NULL, NULL),
(13851, 217, 'SELASA', 5, 31, 0, NULL, NULL, NULL),
(13852, 110, 'SELASA', 6, 34, 0, NULL, NULL, NULL),
(13853, 110, 'SELASA', 7, 34, 0, NULL, NULL, NULL),
(13854, 130, 'RABU', 1, 23, 0, NULL, NULL, NULL),
(13855, 130, 'RABU', 2, 23, 0, NULL, NULL, NULL),
(13856, 130, 'RABU', 3, 23, 0, NULL, NULL, NULL),
(13857, 56, 'RABU', 4, 19, 0, NULL, NULL, NULL),
(13858, 56, 'RABU', 5, 19, 0, NULL, NULL, NULL),
(13859, 56, 'RABU', 6, 19, 0, NULL, NULL, NULL),
(13860, 56, 'RABU', 7, 19, 0, NULL, NULL, NULL),
(13861, 16, 'KAMIS', 1, 2, 0, NULL, NULL, NULL),
(13862, 16, 'KAMIS', 2, 2, 0, NULL, NULL, NULL),
(13863, 337, 'KAMIS', 3, 5, 0, NULL, NULL, NULL),
(13864, 337, 'KAMIS', 4, 5, 0, NULL, NULL, NULL),
(13865, 110, 'KAMIS', 5, 34, 0, NULL, NULL, NULL),
(13866, 338, 'KAMIS', 6, 9, 0, NULL, NULL, NULL),
(13867, 338, 'KAMIS', 7, 9, 0, NULL, NULL, NULL),
(13868, 340, 'JUMAT', 1, 11, 0, NULL, NULL, NULL),
(13869, 340, 'JUMAT', 2, 11, 0, NULL, NULL, NULL),
(13870, 66, 'JUMAT', 3, 19, 0, NULL, NULL, NULL),
(13871, 66, 'JUMAT', 4, 19, 0, NULL, NULL, NULL),
(13872, 66, 'JUMAT', 5, 19, 0, NULL, NULL, NULL),
(13873, 66, 'JUMAT', 6, 19, 0, NULL, NULL, NULL),
(13874, 50, 'SABTU', 1, 38, 0, NULL, NULL, NULL),
(13875, 50, 'SABTU', 2, 38, 0, NULL, NULL, NULL),
(13876, 16, 'SABTU', 3, 2, 0, NULL, NULL, NULL),
(13877, 16, 'SABTU', 4, 2, 0, NULL, NULL, NULL),
(13878, 16, 'SABTU', 5, 2, 0, NULL, NULL, NULL),
(13879, 40, 'SABTU', 6, 17, 0, NULL, NULL, NULL),
(13880, 339, 'SABTU', 7, 27, 0, NULL, NULL, NULL),
(13881, 17, 'SENIN', 2, 2, 0, NULL, NULL, NULL),
(13882, 57, 'SENIN', 3, 19, 0, NULL, NULL, NULL),
(13883, 57, 'SENIN', 4, 19, 0, NULL, NULL, NULL),
(13884, 57, 'SENIN', 5, 19, 0, NULL, NULL, NULL),
(13885, 57, 'SENIN', 6, 19, 0, NULL, NULL, NULL),
(13886, 341, 'SENIN', 7, 5, 0, NULL, NULL, NULL),
(13887, 111, 'SELASA', 1, 34, 0, NULL, NULL, NULL),
(13888, 218, 'SELASA', 2, 31, 0, NULL, NULL, NULL),
(13889, 218, 'SELASA', 3, 31, 0, NULL, NULL, NULL),
(13890, 111, 'SELASA', 4, 34, 0, NULL, NULL, NULL),
(13891, 111, 'SELASA', 5, 34, 0, NULL, NULL, NULL),
(13892, 41, 'SELASA', 6, 17, 0, NULL, NULL, NULL),
(13893, 343, 'SELASA', 7, 27, 0, NULL, NULL, NULL),
(13894, 342, 'RABU', 1, 9, 0, NULL, NULL, NULL),
(13895, 342, 'RABU', 2, 9, 0, NULL, NULL, NULL),
(13896, 343, 'RABU', 3, 27, 0, NULL, NULL, NULL),
(13897, 137, 'RABU', 4, 23, 0, NULL, NULL, NULL),
(13898, 137, 'RABU', 5, 23, 0, NULL, NULL, NULL),
(13899, 137, 'RABU', 6, 23, 0, NULL, NULL, NULL),
(13900, 137, 'RABU', 7, 23, 0, NULL, NULL, NULL),
(13901, 131, 'KAMIS', 1, 23, 0, NULL, NULL, NULL),
(13902, 131, 'KAMIS', 2, 23, 0, NULL, NULL, NULL),
(13903, 131, 'KAMIS', 3, 23, 0, NULL, NULL, NULL),
(13904, 41, 'KAMIS', 4, 17, 0, NULL, NULL, NULL),
(13905, 41, 'KAMIS', 5, 17, 0, NULL, NULL, NULL),
(13906, 41, 'KAMIS', 6, 17, 0, NULL, NULL, NULL),
(13907, 344, 'KAMIS', 7, 11, 0, NULL, NULL, NULL),
(13908, 17, 'JUMAT', 1, 2, 0, NULL, NULL, NULL),
(13909, 17, 'JUMAT', 2, 2, 0, NULL, NULL, NULL),
(13910, 344, 'JUMAT', 3, 11, 0, NULL, NULL, NULL),
(13911, 344, 'JUMAT', 4, 11, 0, NULL, NULL, NULL),
(13912, 51, 'JUMAT', 5, 38, 0, NULL, NULL, NULL),
(13913, 51, 'JUMAT', 6, 38, 0, NULL, NULL, NULL),
(13914, 17, 'SABTU', 1, 2, 0, NULL, NULL, NULL),
(13915, 17, 'SABTU', 2, 2, 0, NULL, NULL, NULL),
(13916, 341, 'SABTU', 3, 5, 0, NULL, NULL, NULL),
(13917, 67, 'SABTU', 4, 24, 0, NULL, NULL, NULL),
(13918, 67, 'SABTU', 5, 24, 0, NULL, NULL, NULL),
(13919, 67, 'SABTU', 6, 24, 0, NULL, NULL, NULL),
(13920, 67, 'SABTU', 7, 24, 0, NULL, NULL, NULL),
(13921, 346, 'SENIN', 2, 10, 0, NULL, NULL, NULL),
(13922, 346, 'SENIN', 3, 10, 0, NULL, NULL, NULL),
(13923, 219, 'SENIN', 4, 31, 0, NULL, NULL, NULL),
(13924, 219, 'SENIN', 5, 31, 0, NULL, NULL, NULL),
(13925, 229, 'SENIN', 6, 32, 0, NULL, NULL, NULL),
(13926, 229, 'SENIN', 7, 32, 0, NULL, NULL, NULL),
(13927, 229, 'SELASA', 1, 32, 0, NULL, NULL, NULL),
(13928, 18, 'SELASA', 2, 4, 0, NULL, NULL, NULL),
(13929, 18, 'SELASA', 3, 4, 0, NULL, NULL, NULL),
(13930, 18, 'SELASA', 4, 4, 0, NULL, NULL, NULL),
(13931, 112, 'SELASA', 5, 22, 0, NULL, NULL, NULL),
(13932, 78, 'SELASA', 6, 20, 0, NULL, NULL, NULL),
(13933, 78, 'SELASA', 7, 20, 0, NULL, NULL, NULL),
(13934, 86, 'RABU', 1, 16, 0, NULL, NULL, NULL),
(13935, 86, 'RABU', 2, 16, 0, NULL, NULL, NULL),
(13936, 18, 'RABU', 3, 4, 0, NULL, NULL, NULL),
(13937, 18, 'RABU', 4, 4, 0, NULL, NULL, NULL),
(13938, 78, 'RABU', 5, 20, 0, NULL, NULL, NULL),
(13939, 78, 'RABU', 6, 20, 0, NULL, NULL, NULL),
(13940, 78, 'RABU', 7, 20, 0, NULL, NULL, NULL),
(13941, 347, 'KAMIS', 1, 6, 0, NULL, NULL, NULL),
(13942, 347, 'KAMIS', 2, 6, 0, NULL, NULL, NULL),
(13943, 347, 'KAMIS', 3, 6, 0, NULL, NULL, NULL),
(13944, 74, 'KAMIS', 4, 30, 0, NULL, NULL, NULL),
(13945, 112, 'KAMIS', 5, 22, 0, NULL, NULL, NULL),
(13946, 112, 'KAMIS', 6, 22, 0, NULL, NULL, NULL),
(13947, 74, 'KAMIS', 7, 30, 0, NULL, NULL, NULL),
(13948, 229, 'JUMAT', 1, 32, 0, NULL, NULL, NULL),
(13949, 80, 'JUMAT', 2, 16, 0, NULL, NULL, NULL),
(13950, 80, 'JUMAT', 3, 16, 0, NULL, NULL, NULL),
(13951, 80, 'JUMAT', 4, 16, 0, NULL, NULL, NULL),
(13952, 80, 'JUMAT', 5, 16, 0, NULL, NULL, NULL),
(13953, 80, 'JUMAT', 6, 16, 0, NULL, NULL, NULL),
(13954, 86, 'SABTU', 1, 16, 0, NULL, NULL, NULL),
(13955, 86, 'SABTU', 2, 16, 0, NULL, NULL, NULL),
(13956, 86, 'SABTU', 3, 16, 0, NULL, NULL, NULL),
(13957, 345, 'SABTU', 4, 27, 0, NULL, NULL, NULL),
(13958, 345, 'SABTU', 5, 27, 0, NULL, NULL, NULL),
(13959, 52, 'SABTU', 6, 18, 0, NULL, NULL, NULL),
(13960, 52, 'SABTU', 7, 18, 0, NULL, NULL, NULL),
(13961, 53, 'SENIN', 2, 18, 0, NULL, NULL, NULL),
(13962, 175, 'SENIN', 3, 27, 0, NULL, NULL, NULL),
(13963, 175, 'SENIN', 4, 27, 0, NULL, NULL, NULL),
(13964, 81, 'SENIN', 5, 16, 0, NULL, NULL, NULL),
(13965, 81, 'SENIN', 6, 16, 0, NULL, NULL, NULL),
(13966, 81, 'SENIN', 7, 16, 0, NULL, NULL, NULL),
(13967, 349, 'SELASA', 1, 6, 0, NULL, NULL, NULL),
(13968, 75, 'SELASA', 2, 30, 0, NULL, NULL, NULL),
(13969, 75, 'SELASA', 3, 30, 0, NULL, NULL, NULL),
(13970, 113, 'SELASA', 4, 22, 0, NULL, NULL, NULL),
(13971, 19, 'SELASA', 5, 4, 0, NULL, NULL, NULL),
(13972, 19, 'SELASA', 6, 4, 0, NULL, NULL, NULL),
(13973, 19, 'SELASA', 7, 4, 0, NULL, NULL, NULL),
(13974, 19, 'RABU', 1, 4, 0, NULL, NULL, NULL),
(13975, 19, 'RABU', 2, 4, 0, NULL, NULL, NULL),
(13976, 87, 'RABU', 3, 16, 0, NULL, NULL, NULL),
(13977, 87, 'RABU', 4, 16, 0, NULL, NULL, NULL),
(13978, 87, 'RABU', 5, 16, 0, NULL, NULL, NULL),
(13979, 87, 'RABU', 6, 16, 0, NULL, NULL, NULL),
(13980, 87, 'RABU', 7, 16, 0, NULL, NULL, NULL),
(13981, 220, 'KAMIS', 1, 31, 0, NULL, NULL, NULL),
(13982, 230, 'KAMIS', 2, 32, 0, NULL, NULL, NULL),
(13983, 230, 'KAMIS', 3, 32, 0, NULL, NULL, NULL),
(13984, 230, 'KAMIS', 4, 32, 0, NULL, NULL, NULL),
(13985, 79, 'KAMIS', 5, 20, 0, NULL, NULL, NULL),
(13986, 79, 'KAMIS', 6, 20, 0, NULL, NULL, NULL);
INSERT INTO `timetable` (`id_timetable`, `id_class_subject`, `hari`, `jam_ke`, `id_guru`, `is_fallback`, `original_guru_id`, `created_at`, `updated_at`) VALUES
(13987, 79, 'KAMIS', 7, 20, 0, NULL, NULL, NULL),
(13988, 79, 'JUMAT', 1, 20, 0, NULL, NULL, NULL),
(13989, 79, 'JUMAT', 2, 20, 0, NULL, NULL, NULL),
(13990, 348, 'JUMAT', 3, 10, 0, NULL, NULL, NULL),
(13991, 348, 'JUMAT', 4, 10, 0, NULL, NULL, NULL),
(13992, 220, 'JUMAT', 5, 31, 0, NULL, NULL, NULL),
(13993, 230, 'JUMAT', 6, 32, 0, NULL, NULL, NULL),
(13994, 349, 'SABTU', 1, 6, 0, NULL, NULL, NULL),
(13995, 349, 'SABTU', 2, 6, 0, NULL, NULL, NULL),
(13996, 53, 'SABTU', 3, 18, 0, NULL, NULL, NULL),
(13997, 81, 'SABTU', 4, 16, 0, NULL, NULL, NULL),
(13998, 81, 'SABTU', 5, 16, 0, NULL, NULL, NULL),
(13999, 113, 'SABTU', 6, 22, 0, NULL, NULL, NULL),
(14000, 113, 'SABTU', 7, 22, 0, NULL, NULL, NULL),
(14001, 517, 'SENIN', 1, 20, 0, NULL, NULL, NULL),
(14002, 517, 'SENIN', 2, 20, 0, NULL, NULL, NULL),
(14003, 519, 'SENIN', 3, 16, 0, NULL, NULL, NULL),
(14004, 519, 'SENIN', 4, 16, 0, NULL, NULL, NULL),
(14005, 519, 'SENIN', 5, 16, 0, NULL, NULL, NULL),
(14006, 514, 'SENIN', 6, 38, 0, NULL, NULL, NULL),
(14007, 514, 'SENIN', 7, 38, 0, NULL, NULL, NULL),
(14008, 518, 'SELASA', 1, 20, 0, NULL, NULL, NULL),
(14009, 518, 'SELASA', 2, 20, 0, NULL, NULL, NULL),
(14010, 518, 'SELASA', 3, 20, 0, NULL, NULL, NULL),
(14011, 518, 'SELASA', 4, 20, 0, NULL, NULL, NULL),
(14012, 507, 'SELASA', 5, 33, 0, NULL, NULL, NULL),
(14013, 507, 'SELASA', 6, 33, 0, NULL, NULL, NULL),
(14014, 513, 'SELASA', 7, 31, 0, NULL, NULL, NULL),
(14015, 510, 'RABU', 1, 12, 0, NULL, NULL, NULL),
(14016, 510, 'RABU', 2, 12, 0, NULL, NULL, NULL),
(14017, 507, 'RABU', 3, 33, 0, NULL, NULL, NULL),
(14018, 507, 'RABU', 4, 33, 0, NULL, NULL, NULL),
(14019, 507, 'RABU', 5, 33, 0, NULL, NULL, NULL),
(14020, 517, 'RABU', 6, 20, 0, NULL, NULL, NULL),
(14021, 517, 'RABU', 7, 20, 0, NULL, NULL, NULL),
(14022, 512, 'KAMIS', 1, 31, 0, NULL, NULL, NULL),
(14023, 512, 'KAMIS', 2, 31, 0, NULL, NULL, NULL),
(14024, 511, 'KAMIS', 3, 11, 0, NULL, NULL, NULL),
(14025, 511, 'KAMIS', 4, 11, 0, NULL, NULL, NULL),
(14026, 509, 'KAMIS', 5, 17, 0, NULL, NULL, NULL),
(14027, 509, 'KAMIS', 6, 17, 0, NULL, NULL, NULL),
(14028, 513, 'KAMIS', 7, 31, 0, NULL, NULL, NULL),
(14029, 508, 'JUMAT', 1, 13, 0, NULL, NULL, NULL),
(14030, 508, 'JUMAT', 2, 13, 0, NULL, NULL, NULL),
(14031, 508, 'JUMAT', 3, 13, 0, NULL, NULL, NULL),
(14032, 511, 'JUMAT', 4, 11, 0, NULL, NULL, NULL),
(14033, 515, 'JUMAT', 5, 19, 0, NULL, NULL, NULL),
(14034, 515, 'JUMAT', 6, 19, 0, NULL, NULL, NULL),
(14035, 519, 'SABTU', 1, 16, 0, NULL, NULL, NULL),
(14036, 519, 'SABTU', 2, 16, 0, NULL, NULL, NULL),
(14037, 516, 'SABTU', 3, 10, 0, NULL, NULL, NULL),
(14038, 516, 'SABTU', 4, 10, 0, NULL, NULL, NULL),
(14039, 509, 'SABTU', 5, 17, 0, NULL, NULL, NULL),
(14040, 509, 'SABTU', 6, 17, 0, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `email_verified_at` timestamp NULL DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('ADMIN','TEACHER','STUDENT') NOT NULL DEFAULT 'STUDENT',
  `id_guru` bigint(20) UNSIGNED DEFAULT NULL,
  `id_siswa` bigint(20) UNSIGNED DEFAULT NULL,
  `remember_token` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `cache`
--
ALTER TABLE `cache`
  ADD PRIMARY KEY (`key`),
  ADD KEY `cache_expiration_index` (`expiration`);

--
-- Indeks untuk tabel `cache_locks`
--
ALTER TABLE `cache_locks`
  ADD PRIMARY KEY (`key`),
  ADD KEY `cache_locks_expiration_index` (`expiration`);

--
-- Indeks untuk tabel `classes`
--
ALTER TABLE `classes`
  ADD PRIMARY KEY (`id_kelas`),
  ADD UNIQUE KEY `classes_nama_kelas_unique` (`nama_kelas`),
  ADD KEY `classes_id_guru_wali_foreign` (`id_guru_wali`);

--
-- Indeks untuk tabel `class_subjects`
--
ALTER TABLE `class_subjects`
  ADD PRIMARY KEY (`id_class_subject`),
  ADD UNIQUE KEY `class_subjects_id_kelas_id_mapel_unique` (`id_kelas`,`id_mapel`),
  ADD KEY `class_subjects_id_mapel_foreign` (`id_mapel`),
  ADD KEY `class_subjects_id_guru_mutlak_foreign` (`id_guru_mutlak`);

--
-- Indeks untuk tabel `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `failed_jobs`
--
ALTER TABLE `failed_jobs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `failed_jobs_uuid_unique` (`uuid`);

--
-- Indeks untuk tabel `grade_configs`
--
ALTER TABLE `grade_configs`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `jobs`
--
ALTER TABLE `jobs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `jobs_queue_index` (`queue`);

--
-- Indeks untuk tabel `job_batches`
--
ALTER TABLE `job_batches`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `jp_schedules`
--
ALTER TABLE `jp_schedules`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `jp_schedules_shift_hari_jam_ke_unique` (`shift`,`hari`,`jam_ke`);

--
-- Indeks untuk tabel `kbm_sessions`
--
ALTER TABLE `kbm_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `kbm_sessions_tanggal_id_kelas_jam_ke_unique` (`tanggal`,`id_kelas`,`jam_ke`),
  ADD KEY `kbm_sessions_id_timetable_foreign` (`id_timetable`),
  ADD KEY `kbm_sessions_id_guru_aktual_foreign` (`id_guru_aktual`);

--
-- Indeks untuk tabel `learning_objectives`
--
ALTER TABLE `learning_objectives`
  ADD PRIMARY KEY (`id_tp`),
  ADD KEY `learning_objectives_id_guru_foreign` (`id_guru`),
  ADD KEY `learning_objectives_id_mapel_foreign` (`id_mapel`);

--
-- Indeks untuk tabel `live_exams`
--
ALTER TABLE `live_exams`
  ADD PRIMARY KEY (`id_exam`),
  ADD KEY `live_exams_id_kbm_session_foreign` (`id_kbm_session`),
  ADD KEY `live_exams_id_bank_foreign` (`id_bank`);

--
-- Indeks untuk tabel `lms_endpoints`
--
ALTER TABLE `lms_endpoints`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `migrations`
--
ALTER TABLE `migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD PRIMARY KEY (`email`);

--
-- Indeks untuk tabel `personal_access_tokens`
--
ALTER TABLE `personal_access_tokens`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `personal_access_tokens_token_unique` (`token`),
  ADD KEY `personal_access_tokens_tokenable_type_tokenable_id_index` (`tokenable_type`,`tokenable_id`),
  ADD KEY `personal_access_tokens_expires_at_index` (`expires_at`);

--
-- Indeks untuk tabel `questionnaires`
--
ALTER TABLE `questionnaires`
  ADD PRIMARY KEY (`id_questionnaire`);

--
-- Indeks untuk tabel `questionnaire_questions`
--
ALTER TABLE `questionnaire_questions`
  ADD PRIMARY KEY (`id_q_question`),
  ADD KEY `questionnaire_questions_id_questionnaire_foreign` (`id_questionnaire`);

--
-- Indeks untuk tabel `questionnaire_responses`
--
ALTER TABLE `questionnaire_responses`
  ADD PRIMARY KEY (`id_response`),
  ADD UNIQUE KEY `unique_response` (`id_questionnaire`,`id_siswa`,`id_guru_target`,`id_q_question`),
  ADD KEY `questionnaire_responses_id_siswa_foreign` (`id_siswa`),
  ADD KEY `questionnaire_responses_id_guru_target_foreign` (`id_guru_target`),
  ADD KEY `questionnaire_responses_id_q_question_foreign` (`id_q_question`);

--
-- Indeks untuk tabel `questions`
--
ALTER TABLE `questions`
  ADD PRIMARY KEY (`id_question`),
  ADD KEY `questions_id_bank_foreign` (`id_bank`);

--
-- Indeks untuk tabel `question_banks`
--
ALTER TABLE `question_banks`
  ADD PRIMARY KEY (`id_bank`),
  ADD KEY `question_banks_id_guru_foreign` (`id_guru`),
  ADD KEY `question_banks_id_mapel_foreign` (`id_mapel`);

--
-- Indeks untuk tabel `report_cards`
--
ALTER TABLE `report_cards`
  ADD PRIMARY KEY (`id_rapor`),
  ADD KEY `report_cards_id_siswa_foreign` (`id_siswa`),
  ADD KEY `report_cards_id_class_subject_foreign` (`id_class_subject`);

--
-- Indeks untuk tabel `sessions`
--
ALTER TABLE `sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sessions_user_id_index` (`user_id`),
  ADD KEY `sessions_last_activity_index` (`last_activity`);

--
-- Indeks untuk tabel `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id_siswa`),
  ADD UNIQUE KEY `students_nis_unique` (`nis`),
  ADD UNIQUE KEY `students_nisn_unique` (`nisn`),
  ADD KEY `students_id_kelas_foreign` (`id_kelas`);

--
-- Indeks untuk tabel `student_answers`
--
ALTER TABLE `student_answers`
  ADD PRIMARY KEY (`id_answer`),
  ADD UNIQUE KEY `student_answers_id_exam_id_siswa_id_question_unique` (`id_exam`,`id_siswa`,`id_question`),
  ADD KEY `student_answers_id_siswa_foreign` (`id_siswa`),
  ADD KEY `student_answers_id_question_foreign` (`id_question`);

--
-- Indeks untuk tabel `student_grades`
--
ALTER TABLE `student_grades`
  ADD PRIMARY KEY (`id_grade`),
  ADD KEY `student_grades_id_siswa_foreign` (`id_siswa`),
  ADD KEY `student_grades_id_tp_foreign` (`id_tp`);

--
-- Indeks untuk tabel `subjects`
--
ALTER TABLE `subjects`
  ADD PRIMARY KEY (`id_mapel`),
  ADD UNIQUE KEY `subjects_nama_mapel_unique` (`nama_mapel`),
  ADD UNIQUE KEY `unique_nama_mapel` (`nama_mapel`);

--
-- Indeks untuk tabel `system_settings`
--
ALTER TABLE `system_settings`
  ADD PRIMARY KEY (`key`);

--
-- Indeks untuk tabel `teachers`
--
ALTER TABLE `teachers`
  ADD PRIMARY KEY (`id_guru`),
  ADD UNIQUE KEY `teachers_kode_guru_unique` (`kode_guru`);

--
-- Indeks untuk tabel `teacher_subjects`
--
ALTER TABLE `teacher_subjects`
  ADD PRIMARY KEY (`id_teacher_subject`),
  ADD UNIQUE KEY `teacher_subjects_id_guru_id_mapel_unique` (`id_guru`,`id_mapel`),
  ADD KEY `teacher_subjects_id_mapel_foreign` (`id_mapel`);

--
-- Indeks untuk tabel `timetable`
--
ALTER TABLE `timetable`
  ADD PRIMARY KEY (`id_timetable`),
  ADD KEY `timetable_id_class_subject_foreign` (`id_class_subject`),
  ADD KEY `timetable_id_guru_foreign` (`id_guru`),
  ADD KEY `timetable_original_guru_id_foreign` (`original_guru_id`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_email_unique` (`email`),
  ADD KEY `users_id_guru_foreign` (`id_guru`),
  ADD KEY `users_id_siswa_foreign` (`id_siswa`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `classes`
--
ALTER TABLE `classes`
  MODIFY `id_kelas` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;

--
-- AUTO_INCREMENT untuk tabel `class_subjects`
--
ALTER TABLE `class_subjects`
  MODIFY `id_class_subject` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=520;

--
-- AUTO_INCREMENT untuk tabel `events`
--
ALTER TABLE `events`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `failed_jobs`
--
ALTER TABLE `failed_jobs`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `grade_configs`
--
ALTER TABLE `grade_configs`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `jobs`
--
ALTER TABLE `jobs`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `jp_schedules`
--
ALTER TABLE `jp_schedules`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `kbm_sessions`
--
ALTER TABLE `kbm_sessions`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `learning_objectives`
--
ALTER TABLE `learning_objectives`
  MODIFY `id_tp` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `live_exams`
--
ALTER TABLE `live_exams`
  MODIFY `id_exam` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `lms_endpoints`
--
ALTER TABLE `lms_endpoints`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `migrations`
--
ALTER TABLE `migrations`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT untuk tabel `personal_access_tokens`
--
ALTER TABLE `personal_access_tokens`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `questionnaires`
--
ALTER TABLE `questionnaires`
  MODIFY `id_questionnaire` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `questionnaire_questions`
--
ALTER TABLE `questionnaire_questions`
  MODIFY `id_q_question` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `questionnaire_responses`
--
ALTER TABLE `questionnaire_responses`
  MODIFY `id_response` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `questions`
--
ALTER TABLE `questions`
  MODIFY `id_question` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `question_banks`
--
ALTER TABLE `question_banks`
  MODIFY `id_bank` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `report_cards`
--
ALTER TABLE `report_cards`
  MODIFY `id_rapor` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `students`
--
ALTER TABLE `students`
  MODIFY `id_siswa` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `student_answers`
--
ALTER TABLE `student_answers`
  MODIFY `id_answer` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `student_grades`
--
ALTER TABLE `student_grades`
  MODIFY `id_grade` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `subjects`
--
ALTER TABLE `subjects`
  MODIFY `id_mapel` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=145;

--
-- AUTO_INCREMENT untuk tabel `teachers`
--
ALTER TABLE `teachers`
  MODIFY `id_guru` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT untuk tabel `teacher_subjects`
--
ALTER TABLE `teacher_subjects`
  MODIFY `id_teacher_subject` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=241;

--
-- AUTO_INCREMENT untuk tabel `timetable`
--
ALTER TABLE `timetable`
  MODIFY `id_timetable` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14041;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `classes`
--
ALTER TABLE `classes`
  ADD CONSTRAINT `classes_id_guru_wali_foreign` FOREIGN KEY (`id_guru_wali`) REFERENCES `teachers` (`id_guru`) ON DELETE SET NULL;

--
-- Ketidakleluasaan untuk tabel `class_subjects`
--
ALTER TABLE `class_subjects`
  ADD CONSTRAINT `class_subjects_id_guru_mutlak_foreign` FOREIGN KEY (`id_guru_mutlak`) REFERENCES `teachers` (`id_guru`) ON DELETE SET NULL,
  ADD CONSTRAINT `class_subjects_id_kelas_foreign` FOREIGN KEY (`id_kelas`) REFERENCES `classes` (`id_kelas`) ON DELETE CASCADE,
  ADD CONSTRAINT `class_subjects_id_mapel_foreign` FOREIGN KEY (`id_mapel`) REFERENCES `subjects` (`id_mapel`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `kbm_sessions`
--
ALTER TABLE `kbm_sessions`
  ADD CONSTRAINT `kbm_sessions_id_guru_aktual_foreign` FOREIGN KEY (`id_guru_aktual`) REFERENCES `teachers` (`id_guru`) ON DELETE SET NULL,
  ADD CONSTRAINT `kbm_sessions_id_timetable_foreign` FOREIGN KEY (`id_timetable`) REFERENCES `timetable` (`id_timetable`) ON DELETE SET NULL;

--
-- Ketidakleluasaan untuk tabel `learning_objectives`
--
ALTER TABLE `learning_objectives`
  ADD CONSTRAINT `learning_objectives_id_guru_foreign` FOREIGN KEY (`id_guru`) REFERENCES `teachers` (`id_guru`) ON DELETE CASCADE,
  ADD CONSTRAINT `learning_objectives_id_mapel_foreign` FOREIGN KEY (`id_mapel`) REFERENCES `subjects` (`id_mapel`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `live_exams`
--
ALTER TABLE `live_exams`
  ADD CONSTRAINT `live_exams_id_bank_foreign` FOREIGN KEY (`id_bank`) REFERENCES `question_banks` (`id_bank`) ON DELETE CASCADE,
  ADD CONSTRAINT `live_exams_id_kbm_session_foreign` FOREIGN KEY (`id_kbm_session`) REFERENCES `kbm_sessions` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `questionnaire_questions`
--
ALTER TABLE `questionnaire_questions`
  ADD CONSTRAINT `questionnaire_questions_id_questionnaire_foreign` FOREIGN KEY (`id_questionnaire`) REFERENCES `questionnaires` (`id_questionnaire`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `questionnaire_responses`
--
ALTER TABLE `questionnaire_responses`
  ADD CONSTRAINT `questionnaire_responses_id_guru_target_foreign` FOREIGN KEY (`id_guru_target`) REFERENCES `teachers` (`id_guru`) ON DELETE CASCADE,
  ADD CONSTRAINT `questionnaire_responses_id_q_question_foreign` FOREIGN KEY (`id_q_question`) REFERENCES `questionnaire_questions` (`id_q_question`) ON DELETE CASCADE,
  ADD CONSTRAINT `questionnaire_responses_id_questionnaire_foreign` FOREIGN KEY (`id_questionnaire`) REFERENCES `questionnaires` (`id_questionnaire`) ON DELETE CASCADE,
  ADD CONSTRAINT `questionnaire_responses_id_siswa_foreign` FOREIGN KEY (`id_siswa`) REFERENCES `students` (`id_siswa`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `questions`
--
ALTER TABLE `questions`
  ADD CONSTRAINT `questions_id_bank_foreign` FOREIGN KEY (`id_bank`) REFERENCES `question_banks` (`id_bank`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `question_banks`
--
ALTER TABLE `question_banks`
  ADD CONSTRAINT `question_banks_id_guru_foreign` FOREIGN KEY (`id_guru`) REFERENCES `teachers` (`id_guru`) ON DELETE CASCADE,
  ADD CONSTRAINT `question_banks_id_mapel_foreign` FOREIGN KEY (`id_mapel`) REFERENCES `subjects` (`id_mapel`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `report_cards`
--
ALTER TABLE `report_cards`
  ADD CONSTRAINT `report_cards_id_class_subject_foreign` FOREIGN KEY (`id_class_subject`) REFERENCES `class_subjects` (`id_class_subject`) ON DELETE CASCADE,
  ADD CONSTRAINT `report_cards_id_siswa_foreign` FOREIGN KEY (`id_siswa`) REFERENCES `students` (`id_siswa`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `students`
--
ALTER TABLE `students`
  ADD CONSTRAINT `students_id_kelas_foreign` FOREIGN KEY (`id_kelas`) REFERENCES `classes` (`id_kelas`);

--
-- Ketidakleluasaan untuk tabel `student_answers`
--
ALTER TABLE `student_answers`
  ADD CONSTRAINT `student_answers_id_exam_foreign` FOREIGN KEY (`id_exam`) REFERENCES `live_exams` (`id_exam`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_answers_id_question_foreign` FOREIGN KEY (`id_question`) REFERENCES `questions` (`id_question`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_answers_id_siswa_foreign` FOREIGN KEY (`id_siswa`) REFERENCES `students` (`id_siswa`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `student_grades`
--
ALTER TABLE `student_grades`
  ADD CONSTRAINT `student_grades_id_siswa_foreign` FOREIGN KEY (`id_siswa`) REFERENCES `students` (`id_siswa`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_grades_id_tp_foreign` FOREIGN KEY (`id_tp`) REFERENCES `learning_objectives` (`id_tp`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `teacher_subjects`
--
ALTER TABLE `teacher_subjects`
  ADD CONSTRAINT `teacher_subjects_id_guru_foreign` FOREIGN KEY (`id_guru`) REFERENCES `teachers` (`id_guru`) ON DELETE CASCADE,
  ADD CONSTRAINT `teacher_subjects_id_mapel_foreign` FOREIGN KEY (`id_mapel`) REFERENCES `subjects` (`id_mapel`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `timetable`
--
ALTER TABLE `timetable`
  ADD CONSTRAINT `timetable_id_class_subject_foreign` FOREIGN KEY (`id_class_subject`) REFERENCES `class_subjects` (`id_class_subject`) ON DELETE CASCADE,
  ADD CONSTRAINT `timetable_id_guru_foreign` FOREIGN KEY (`id_guru`) REFERENCES `teachers` (`id_guru`) ON DELETE SET NULL,
  ADD CONSTRAINT `timetable_original_guru_id_foreign` FOREIGN KEY (`original_guru_id`) REFERENCES `teachers` (`id_guru`) ON DELETE SET NULL;

--
-- Ketidakleluasaan untuk tabel `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_id_guru_foreign` FOREIGN KEY (`id_guru`) REFERENCES `teachers` (`id_guru`) ON DELETE SET NULL,
  ADD CONSTRAINT `users_id_siswa_foreign` FOREIGN KEY (`id_siswa`) REFERENCES `students` (`id_siswa`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
