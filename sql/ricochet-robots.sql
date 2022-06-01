-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Erstellungszeit: 30. Mai 2022 um 21:50
-- Server-Version: 10.4.17-MariaDB
-- PHP-Version: 8.0.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Datenbank: `ricochet_robots`
--
CREATE DATABASE ricochet_robots;
USE ricochet_robots;
-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `chips`
--

CREATE TABLE `chips` (
  `chip_id` int(2) NOT NULL,
  `game_id` int(3) UNSIGNED NOT NULL,
  `color_name` varchar(255) NOT NULL,
  `symbol` varchar(255) NOT NULL,
  `position_column` int(2) UNSIGNED NOT NULL,
  `position_row` int(2) UNSIGNED NOT NULL,
  `revealed` tinyint(1) UNSIGNED NOT NULL DEFAULT 0,
  `obtained_by_player_id` int(10) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `games`
--

CREATE TABLE `games` (
  `game_id` int(10) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `duration` int(4) UNSIGNED NOT NULL DEFAULT 0,
  `round_number` int(2) UNSIGNED NOT NULL DEFAULT 1,
  `player_count` int(4) UNSIGNED NOT NULL DEFAULT 0,
  `winner_player_id` int(4) UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `players`
--

CREATE TABLE `players` (
  `player_id` int(10) NOT NULL,
  `game_id` int(10) NOT NULL,
  `name` varchar(255) NOT NULL,
  `score` int(2) NOT NULL DEFAULT 0,
  `solution` int(2) NOT NULL DEFAULT -1,
  `last_solution_change` timestamp NOT NULL DEFAULT current_timestamp(),
  `ready_for_round` tinyint(3) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `robots`
--

CREATE TABLE `robots` (
  `robot_id` int(8) UNSIGNED NOT NULL,
  `game_id` int(4) UNSIGNED NOT NULL,
  `color_name` varchar(255) NOT NULL,
  `home_position_column` int(2) UNSIGNED NOT NULL,
  `home_position_row` int(2) UNSIGNED NOT NULL,
  `position_column` int(2) UNSIGNED NOT NULL,
  `position_row` int(2) UNSIGNED NOT NULL,
  `in_use` tinyint(3) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `rounds`
--

CREATE TABLE `rounds` (
  `round_id` int(10) NOT NULL,
  `game_id` int(10) NOT NULL,
  `round_number` int(2) NOT NULL,
  `chip_id` varchar(255) NOT NULL,
  `started_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `duration` int(4) NOT NULL DEFAULT 0,
  `best_solution` int(2) DEFAULT NULL,
  `best_player_id` int(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `chips`
--
ALTER TABLE `chips`
  ADD PRIMARY KEY (`chip_id`);

--
-- Indizes für die Tabelle `games`
--
ALTER TABLE `games`
  ADD PRIMARY KEY (`game_id`);

--
-- Indizes für die Tabelle `players`
--
ALTER TABLE `players`
  ADD PRIMARY KEY (`player_id`);

--
-- Indizes für die Tabelle `robots`
--
ALTER TABLE `robots`
  ADD PRIMARY KEY (`robot_id`);

--
-- Indizes für die Tabelle `rounds`
--
ALTER TABLE `rounds`
  ADD PRIMARY KEY (`round_id`);

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `chips`
--
ALTER TABLE `chips`
  MODIFY `chip_id` int(2) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT für Tabelle `games`
--
ALTER TABLE `games`
  MODIFY `game_id` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT für Tabelle `players`
--
ALTER TABLE `players`
  MODIFY `player_id` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT für Tabelle `robots`
--
ALTER TABLE `robots`
  MODIFY `robot_id` int(8) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT für Tabelle `rounds`
--
ALTER TABLE `rounds`
  MODIFY `round_id` int(10) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
