import pyodbc
import json


import pyodbc
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
import os

load_dotenv()
# Connection details
server = os.environ.get("DB_SERVER")
database = os.environ.get("DB_NAME")
username = os.environ.get("DB_USERNAME")
password = os.environ.get("DB_PASSWORD")
driver = os.environ.get("DB_DRIVER")

# Construct the connection string
conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
)

print("Connected successfully!")

cursor = conn.cursor()

# Create a table to store article data (if not already created)
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Articles')
    BEGIN
        CREATE TABLE Articles (
            id INT PRIMARY KEY IDENTITY(1,1),
            file_name NVARCHAR(MAX),
            article_text NVARCHAR(MAX)
        )
    END
''')
conn.commit()

# Load articles from JSON file
with open("articles.json", "r", encoding="utf-8") as file:
    articles_data = json.load(file)


cursor = conn.cursor()
 # Insert each article into the database
for article in articles_data:
    # Extract file_name and article_text from the current article
    file_name = article.get('file')  # Use .get() to handle missing keys gracefully
    article_text = article.get('text')

 # Insert data into the database
    cursor.execute('''
            INSERT INTO Articles (file_name, article_text)
            VALUES (?, ?)
        ''', (file_name, article_text))

conn.commit()
print("Data uploaded to Azure SQL Database successfully.")
cursor.close()
conn.close()
