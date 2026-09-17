-- =========================================================
-- schema_mysql.sql
-- Reference schema if you want to run this project on MySQL
-- instead of the default SQLite (see database.py).
--
-- To use MySQL instead:
--   1. pip install mysql-connector-python
--   2. Run this schema against your MySQL server
--   3. Replace database.py's sqlite3 calls with mysql.connector calls
--      (connection details, and %s placeholders instead of ?)
-- =========================================================

CREATE DATABASE IF NOT EXISTS expense_tracker;
USE expense_tracker;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    txn_date DATE NOT NULL,
    note VARCHAR(255),
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Sample seed data (optional)
-- INSERT INTO users (name, email, password_hash, created_at)
-- VALUES ('Demo User', 'demo@example.com', '<bcrypt-or-werkzeug-hash>', NOW());
