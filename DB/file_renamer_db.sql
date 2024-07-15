-- Create the database
CREATE DATABASE IF NOT EXISTS file_renamer_db;

-- Use the created database
USE file_renamer_db;

-- Create the users table for registration
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

CREATE INDEX IF NOT EXISTS idx_uploads_timestamp ON uploads(timestamp);
CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON error_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
