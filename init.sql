-- Drop existing tables if they exist (drop bookings first due to foreign key constraints)
DROP TABLE IF EXISTS `bookings`;
DROP TABLE IF EXISTS `rooms`;
DROP TABLE IF EXISTS `hotels`;

-- Create the hotels table
CREATE TABLE `hotels` (
  `hotel_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `location` VARCHAR(255) NOT NULL,
  `amenities` TEXT,
  `contact_info` VARCHAR(255),
  PRIMARY KEY (`hotel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create the rooms table
CREATE TABLE `rooms` (
  `room_id` INT NOT NULL AUTO_INCREMENT,
  `hotel_id` INT,
  `room_type` VARCHAR(100),
  `price` DECIMAL(10,2),
  `availability` INT,
  PRIMARY KEY (`room_id`),
  KEY `hotel_id` (`hotel_id`),
  CONSTRAINT `rooms_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create the bookings table
CREATE TABLE `bookings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `hotel_id` INT,
  `name` VARCHAR(255),
  `price` DECIMAL(10,2),
  `days` INT,
  `people` INT,
  `room_type` VARCHAR(100),
  `check_in_date` DATE,
  `check_out_date` DATE,
  PRIMARY KEY (`id`),
  KEY `hotel_id` (`hotel_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert initial hotel data
INSERT INTO `hotels` (name, location, amenities, contact_info) VALUES
('SilverStar', 'Bengaluru', 'Pool,ac', '1234567890'),
('Palm Retreat', 'Goa', 'Spa,WiFi,Bar', '9876543210'),
('HillTop Haven', 'Ooty', 'Heater,WiFi,View', '1122334455');

-- Insert initial room data
INSERT INTO `rooms` (hotel_id, room_type, price, availability) VALUES
(1, 'Single', 1500.00, 5),
(1, 'Double', 2500.00, 3),
(1, 'Suite', 4000.00, 2),
(2, 'Single', 1800.00, 4),
(2, 'Suite', 5000.00, 1),
(3, 'Double', 2200.00, 6),
(3, 'Suite', 4500.00, 2);

-- Insert sample bookings with check-in/check-out dates
INSERT INTO `bookings` (hotel_id, name, price, days, people, room_type, check_in_date, check_out_date) VALUES
(1, 'Alice', 5000.00, 2, 1, 'Double', '2025-04-10', '2025-04-12'),
(2, 'Bob', 10000.00, 4, 2, 'Suite', '2025-04-15', '2025-04-19'),
(1, 'Charlie', 3000.00, 1, 1, 'Single', '2025-04-09', '2025-04-10'),
(3, 'Diana', 9000.00, 3, 2, 'Suite', '2025-04-08', '2025-04-11'),
(2, 'Ethan', 3600.00, 2, 1, 'Single', '2025-04-11', '2025-04-13');
