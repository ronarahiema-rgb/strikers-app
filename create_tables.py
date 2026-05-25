"""Maakt de database tabellen aan via de HBO-ICT.cloud API."""

import requests
from dotenv import load_dotenv
from os import environ

load_dotenv()

API_URL = environ.get("API_URL")
API_KEY = environ.get("API_KEY")
DATABASE = environ.get("DATABASE")


def execute_query(query):
    response = requests.post(
        url=f"{API_URL}/db",
        json={"query": query, "database": DATABASE},
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=10,
    )
    return response.json()


tabellen = {
    "student": """
        CREATE TABLE IF NOT EXISTS student (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            surname VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
    """,
    "docent": """
        CREATE TABLE IF NOT EXISTS docent (
            docent_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            surname VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
    """,
    "ouder": """
        CREATE TABLE IF NOT EXISTS ouder (
            ouder_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            surname VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
    """,
    "ouder_student": """
        CREATE TABLE IF NOT EXISTS ouder_student (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ouder_id INT NOT NULL,
            student_id INT NOT NULL,
            FOREIGN KEY (ouder_id) REFERENCES ouder(ouder_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
            UNIQUE (ouder_id, student_id)
        )
    """,
}

for naam, query in tabellen.items():
    result = execute_query(query)
    print(f"{naam}: {result}")
