import pyodbc
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os


load_dotenv()
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

def authenticate_text_analytics_client():
    endpoint = os.environ.get("DB_ENDPOINT")
    api_key = os.environ.get("API_KEY")   # Replace with your Azure AI service API key
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

# Function to split the text into chunks of a specified max size
def split_text(text, max_size):
    return [text[i:i + max_size] for i in range(0, len(text), max_size)]

# Function to save key phrases to the database
def save_analysis_results(cursor, article_id, key_phrases):
    key_phrases_text = ', '.join(key_phrases)
    cursor.execute('''
        UPDATE dbo.Articles
        SET key_phrases = ?
        WHERE id = ?
    ''', (key_phrases_text, article_id))
    cursor.connection.commit()

# Main function to analyze articles and save the results
def analyze_and_save_results():
    conn = connect_to_database()
    cursor = conn.cursor()

    text_analytics_client = authenticate_text_analytics_client()

    cursor.execute("SELECT id, article_text FROM dbo.Articles")
    rows = cursor.fetchall()

    for row in rows:
        article_id = row[0]
        article_text = row[1]

        # Split the article text into chunks
        chunks = split_text(article_text, 5120)
        key_phrases_all = []

        for chunk in chunks:
            documents = [chunk]
            response = text_analytics_client.extract_key_phrases(documents=documents)
            for result in response:
                if not result.is_error:
                    key_phrases_all.extend(result.key_phrases)
                else:
                    print("Error:", result.error)

        # Save the key phrases to the database
        save_analysis_results(cursor, article_id, key_phrases_all)

    cursor.close()
    conn.close()
    print("Analysis completed and results saved.")

if __name__ == "__main__":
    analyze_and_save_results()
