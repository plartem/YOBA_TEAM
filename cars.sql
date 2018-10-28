CREATE DATABASE IF NOT EXISTS `cars`;
USE `cars`;

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

CREATE TABLE `queries` (
  `id` int(11) NOT NULL,
  `mark` varchar(50) NOT NULL,
  `model` varchar(50) NOT NULL,
  `high_price` int(11) NOT NULL,
  `low_price` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `mileage` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `timeinterval` int(11) NOT NULL DEFAULT 15,
  `updatedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `queries` (`id`, `mark`, `model`, `high_price`, `low_price`, `year`, `mileage`, `user_id`) VALUES
(1, 'Ford', '', -1, 100, 2000, 10000, 9);

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  `surname` varchar(50) NOT NULL,
  `login` varchar(50) NOT NULL,
  `token` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `users` (`id`, `email`, `password`, `name`, `surname`, `login`, `token`) VALUES
(9, 'bcklmnop@gmail.com', '$2b$12$/2AI2MgRVQ9zirUKIZkKOOUx7V1r2thW2p5xcFc4rRbbpYhHf5evy', 'bcklmnop', 'bcklmnop', 'bcklmnop', '');

CREATE TABLE IF NOT EXISTS `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` char(50) DEFAULT NULL,
  `message` varchar(255) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

ALTER TABLE `queries`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `login` (`login`),
  ADD KEY `id` (`id`),
  ADD KEY `id_2` (`id`);

ALTER TABLE `queries`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;COMMIT;