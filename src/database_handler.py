#-- This is a comment, actual Python code below
import sqlite3
import os
from datetime import datetime
import logging

class DatabaseHandler:
    def __init__(self, db_path="data/attendance.db", schema_path="database/schema.sql"):
        self.db_path = db_path
        self.schema_path = schema_path
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.create_tables()
        logging.info(f"Database initialized at {self.db_path}")
    
    def create_tables(self):
        """Execute schema.sql to create all tables"""
        try:
            with open(self.schema_path, 'r') as schema_file:
                schema_sql = schema_file.read()
                self.connection.executescript(schema_sql)
            self.connection.commit()
            logging.info("Tables created successfully")
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
    
    def execute_query(self, query, params=None):
        """Execute SQL query and return cursor"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Exception as e:
            logging.error(f"Query execution error: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """Fetch all results from query"""
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return []
    
    def insert_student(self, student_id, name, department, year, email, phone):
        """Insert new student"""
        query = """
            INSERT INTO students (student_id, name, department, year, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (student_id, name, department, year, email, phone))
    
    def get_all_students(self):
        """Get all students"""
        query = "SELECT * FROM students WHERE is_active = 1"
        return self.fetch_all(query)
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed")