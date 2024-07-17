-- Create the database
CREATE DATABASE IF NOT EXISTS file_renamer_db;

-- Use the created database
USE file_renamer_db;

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Create the uploads table
CREATE TABLE IF NOT EXISTS uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity VARCHAR(255) NOT NULL,
    user_data VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the error_logs table
CREATE TABLE IF NOT EXISTS error_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    error_message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INT PRIMARY KEY,
    full_name VARCHAR(255),
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    nationality VARCHAR(100),
    id_number VARCHAR(100),
    national_id_type VARCHAR(100),
    expiry_date DATE,
    email VARCHAR(255),
    phone_number VARCHAR(20),
    address_street VARCHAR(255),
    address_city VARCHAR(100),
    address_state VARCHAR(100),
    address_zip VARCHAR(20),
    address_country VARCHAR(100),
    occupation VARCHAR(100),
    company_name VARCHAR(100),
    account_creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_date DATETIME,
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    user_role ENUM('Admin', 'Regular User') DEFAULT 'Regular User',
    security_question VARCHAR(255),
    security_answer VARCHAR(255),
    two_factor_auth_enabled BOOLEAN DEFAULT FALSE,
    profile_picture VARCHAR(255),  -- Store path to the profile picture
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
-- CREATE TABLE IF NOT EXISTS user_profiles (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     user_id INT NOT NULL,
--     full_name VARCHAR(255),
--     date_of_birth DATE,
--     gender VARCHAR(50),
--     nationality VARCHAR(100),
--     id_number VARCHAR(100),
--     national_id_type VARCHAR(100),
--     expiry_date DATE,
--     email VARCHAR(255),
--     phone_number VARCHAR(50),
--     address_street VARCHAR(255),
--     address_city VARCHAR(100),
--     address_state VARCHAR(100),
--     address_zip VARCHAR(20),
--     address_country VARCHAR(100),
--     occupation VARCHAR(100),
--     company_name VARCHAR(100),
--     UNIQUE KEY (user_id)  -- Ensure user_id is unique for the profile
-- );


-- Optionally, you can add indexes for better performance
DROP INDEX IF EXISTS idx_uploads_timestamp ON uploads;
CREATE INDEX idx_uploads_timestamp ON uploads(timestamp);

DROP INDEX IF EXISTS idx_errors_timestamp ON error_logs;
CREATE INDEX idx_errors_timestamp ON error_logs(timestamp);
