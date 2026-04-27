-- Smart Attendance System - Database Schema

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    year INTEGER,
    semester INTEGER,
    email VARCHAR(100),
    phone VARCHAR(15),
    face_encoding BLOB,
    face_image_path VARCHAR(255),
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    notes TEXT
);

-- Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    check_in_time TIME,
    check_out_time TIME,
    status VARCHAR(20) DEFAULT 'present',
    marked_by VARCHAR(50) DEFAULT 'system',
    confidence_score FLOAT,
    remarks TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE(student_id, date)
);

-- Logs Table
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50),
    student_id VARCHAR(20),
    details TEXT,
    ip_address VARCHAR(45),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_student_id ON students(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);