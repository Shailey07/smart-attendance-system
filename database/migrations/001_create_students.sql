-- Migration 001: Create students table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    year INTEGER,
    email VARCHAR(100),
    phone VARCHAR(15),
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
);