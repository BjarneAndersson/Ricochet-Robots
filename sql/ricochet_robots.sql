SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `ricochet_robots` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `ricochet_robots`;

CREATE TABLE `chips` (
  `chip_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `color_name` varchar(6) NOT NULL,
  `symbol` varchar(8) NOT NULL,
  `position` varchar(7) NOT NULL,
  `revealed` tinyint(1) NOT NULL DEFAULT 0,
  `obtained_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `games` (
  `game_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `duration` int(11) NOT NULL DEFAULT 0,
  `round_number` int(11) NOT NULL DEFAULT 1,
  `player_count` int(11) NOT NULL DEFAULT 0,
  `winners` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `players` (
  `player_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `score` int(11) NOT NULL DEFAULT 0,
  `solution` int(11) DEFAULT NULL,
  `last_solution_change` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `ready_for_round` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `robots` (
  `robot_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `color_name` varchar(6) NOT NULL,
  `position` varchar(7) NOT NULL,
  `home_position` varchar(7) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `rounds` (
  `round_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `round_number` int(11) NOT NULL,
  `chip_id` int(11) NOT NULL,
  `started_at` datetime NOT NULL DEFAULT current_timestamp(),
  `duration` int(11) DEFAULT NULL,
  `solution` int(11) DEFAULT NULL,
  `winner` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


ALTER TABLE `chips`
  ADD PRIMARY KEY (`chip_id`);

ALTER TABLE `games`
  ADD PRIMARY KEY (`game_id`);

ALTER TABLE `players`
  ADD PRIMARY KEY (`player_id`);

ALTER TABLE `robots`
  ADD PRIMARY KEY (`robot_id`);

ALTER TABLE `rounds`
  ADD PRIMARY KEY (`round_id`);


ALTER TABLE `chips`
  MODIFY `chip_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `games`
  MODIFY `game_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `players`
  MODIFY `player_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `robots`
  MODIFY `robot_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `rounds`
  MODIFY `round_id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
