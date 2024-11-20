import pyodbc
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import pyodbc
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Function to split text into chunks of a specified size
def split_text(text, max_size):
    return [text[i:i + max_size] for i in range(0, len(text), max_size)]

# Step 1: Connect to your Azure SQL Database
def connect_to_database():
    server = os.environ.get("DB_SERVER")
    database = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    driver = os.environ.get("DB_DRIVER")

    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    print("Connected to database successfully!")
    return conn

# Step 2: Set up Azure Text Analytics
def authenticate_text_analytics_client():
    endpoint = os.environ.get("DB_ENDPOINT")
    api_key = os.environ.get("API_KEY")


    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

# Step 3: Fetch and analyze articles
def analyze_articles():
    conn = connect_to_database()
    cursor = conn.cursor()

    text_analytics_client = authenticate_text_analytics_client()

    # Fetch the text data from your Articles table
    cursor.execute("SELECT article_text FROM dbo.Articles")
    rows = cursor.fetchall()

    # Analyze the text using Azure Text Analytics
    for row in rows:
        article_text = row[0]  # Get the article_text from the row

        # Split the text into chunks if it exceeds the size limit
        chunks = split_text(article_text, 5120)

        for chunk in chunks:
            documents = [chunk]  # Prepare the text chunk for analysis

            response = text_analytics_client.extract_key_phrases(documents=documents)
            for result in response:
                if not result.is_error:
                    print("Key Phrases:", result.key_phrases)
                else:
                    print("Error:", result.error)

    # Close the connection
    cursor.close()
    conn.close()
    print("Analysis completed.")

# Step 4: Run the analysis
if __name__ == "__main__":
    analyze_articles()
