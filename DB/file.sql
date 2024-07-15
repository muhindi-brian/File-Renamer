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

-- Optionally, you can add indexes for better performance
DROP INDEX IF EXISTS idx_uploads_timestamp ON uploads;
CREATE INDEX idx_uploads_timestamp ON uploads(timestamp);

DROP INDEX IF EXISTS idx_errors_timestamp ON error_logs;
CREATE INDEX idx_errors_timestamp ON error_logs(timestamp);
