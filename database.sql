-- Local Service Finder with Trust Score
-- Complete Database Schema

CREATE DATABASE IF NOT EXISTS local_service_finder;
USE local_service_finder;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Services Table
CREATE TABLE IF NOT EXISTS services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(150) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    location VARCHAR(150) NOT NULL,
    description TEXT,
    price_range VARCHAR(50),
    image_filename VARCHAR(255) DEFAULT NULL,
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT NOT NULL,
    reviewer_name VARCHAR(100) NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    user_email VARCHAR(150),
    service_id INT,
    service_name VARCHAR(150) NOT NULL,
    service_type VARCHAR(100),
    location VARCHAR(150),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
    notes TEXT,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL
);

-- Sample Data
INSERT INTO users (name, email, password) VALUES
('Ali Hassan', 'ali@example.com', 'pbkdf2:sha256:samplehash'),
('Sara Khan', 'sara@example.com', 'pbkdf2:sha256:samplehash');

INSERT INTO services (user_id, name, service_type, location, description, price_range, rating, total_reviews) VALUES
(1, 'Ali Electric Works', 'Electrician', 'Rawalpindi', 'Professional electrical services for homes and offices. 10+ years experience.', 'Rs 500-2000', 4.80, 12),
(2, 'Sara Clean Home', 'Cleaning', 'Islamabad', 'Deep cleaning, regular maintenance, carpet cleaning.', 'Rs 800-3000', 4.50, 8),
(1, 'FastFix Plumbing', 'Plumber', 'Rawalpindi', 'All plumbing solutions — leaks, pipes, fittings.', 'Rs 400-1500', 4.20, 5),
(2, 'CoolAir AC Services', 'AC Technician', 'Islamabad', 'AC installation, repair, gas refill, maintenance.', 'Rs 1000-5000', 4.90, 20),
(1, 'Ahmed Math Tutor', 'Tutor', 'Rawalpindi', 'O/A Level Math and Physics tutor with 5 years experience.', 'Rs 500-1500/hr', 4.70, 15);

INSERT INTO reviews (service_id, reviewer_name, rating, comment) VALUES
(1, 'Bilal Ahmed', 5, 'Excellent work! Very professional and punctual.'),
(1, 'Hina Malik', 5, 'Fixed all wiring issues perfectly. Highly recommend!'),
(2, 'Zara Hussain', 4, 'Great cleaning service. Very thorough.'),
(3, 'Omar Sheikh', 4, 'Good plumbing work, fixed the leak quickly.'),
(4, 'Fatima Noor', 5, 'Best AC service in Islamabad! Super professional.'),
(5, 'Usman Qureshi', 5, 'My son improved from D to A in Math. Amazing tutor!');

INSERT INTO bookings (user_name, user_email, service_id, service_name, service_type, location, status) VALUES
('Bilal Ahmed', 'bilal@example.com', 1, 'Ali Electric Works', 'Electrician', 'Rawalpindi', 'completed'),
('Hina Malik', 'hina@example.com', 4, 'CoolAir AC Services', 'AC Technician', 'Islamabad', 'confirmed'),
('Zara Hussain', 'zara@example.com', 2, 'Sara Clean Home', 'Cleaning', 'Islamabad', 'pending');
