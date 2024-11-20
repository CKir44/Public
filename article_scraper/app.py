from flask import Flask, request, jsonify
import pyodbc
import spacy
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv
from gensim.summarization import summarize

app = Flask(__name__)

# Load spaCy's language model
nlp = spacy.load("en_core_web_sm")

load_dotenv()
# Function to connect to your Azure SQL Database
def connect_to_database():
    server = os.environ.get("DB_SERVER")
    database = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    driver = os.environ.get("DB_DRIVER")

    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    return conn

# Function to clean up text
def clean_text(text):
    return text.replace("\n", " ").replace("\r", " ").strip()



def get_article_text(article_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT article_text FROM dbo.Articles WHERE id = ?", (article_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Article not found."

# Function to fetch article summary
def get_article_summary(article_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT summary FROM dbo.Articles WHERE id = ?", (article_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Summary not available."

# Function to fetch author information (update with actual data)
#Couldnt find correct html markers for each article so hard coded it in
def get_article_author(article_id):
    if article_id == 1:
        return "Author of the first article is: [Mark C. Gridley]"
    elif article_id == 2:
        return "Author of the second article is: [Nathalie Lyssenko]"
    else:
        return "Author information not available."

# Function to generate a summary using Gensim
def generate_summary(text):
    try:
        summary = summarize(text, word_count=100)  # Adjust word_count as needed
        return summary
    except ValueError:
        return "Summary could not be generated."

# Function to perform NLP analysis using spaCy
def analyze_text_with_spacy(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]  # Extract named entities
    return entities

# Function to compare articles
def compare_articles(article_text_1, article_text_2):
    words_1 = set(article_text_1.lower().split())
    words_2 = set(article_text_2.lower().split())
    common_words = words_1.intersection(words_2)
    common_words_list = list(common_words)[:30]  # Limiting to 30 common words
    if common_words_list:
        return f"Both articles share these common words or themes: {', '.join(common_words_list)}."
    else:
        return "The articles do not seem to have any obvious similarities based on common words."

# Function to find a sentence containing a specific keyword
def find_sentence_with_keyword(text, keyword):
    doc = nlp(text)
    for sentence in doc.sents:
        if keyword.lower() in sentence.text.lower():
            return sentence.text
    return "No sentence containing the keyword found."

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message").lower()

    # Initial greeting
    if user_input in ["hi", "hello", "hey"]:
        return jsonify({"response": "Hi, I am the Article Summarizer! How can I help you?"})

    # Define article_text_1 and article_text_2 at the beginning
    article_text_1 = get_article_text(1)
    article_text_2 = get_article_text(2)

    # Determine the article ID or process both if not specified
    if "first article" in user_input:
        article_id = 1
        article_text = article_text_1
    elif "second article" in user_input:
        article_id = 2
        article_text = article_text_2
    else:
        article_id = None
        # Combine text from both articles if no specific article is mentioned
        article_text = article_text_1 + " " + article_text_2

    # Handle "What is the first article about?" query
    if "what is the first article about" in user_input:
        response_text = generate_summary(article_text_1)
        response = {"response": f"Here's what the first article is about: {clean_text(response_text)}"}

    # Handle request for a sentence from each article containing a specific keyword
    elif "sentence from each article" in user_input and "abstract art" in user_input:
        sentence_1 = find_sentence_with_keyword(article_text_1, "abstract art")
        sentence_2 = find_sentence_with_keyword(article_text_2, "abstract art")
        response_text = (
            f"Here is a sentence from each article containing 'abstract art':\n1. {clean_text(sentence_1)}\n2. {clean_text(sentence_2)}"
        )
        response = {"response": response_text}

    # Custom response for "It took a lot of hours to create you, didn't it"
    elif "it took a lot of hours to create you" in user_input and "didn't it" in user_input:
        response = {
            "response": "Yes it did, but for your first try it wasn’t too bad at all. Why don’t you take a load off and maybe find something tasty to eat!"
        }

    # Handle similarity-related queries
    elif "similar" in user_input or "comparison" in user_input or "both articles" in user_input:
        response_text = compare_articles(article_text_1, article_text_2)
        response = {"response": response_text}

    # Handle summary-related queries
    elif any(keyword in user_input for keyword in ["summary", "topic", "subject", "summarize", "about"]):
        response_text = generate_summary(article_text)
        response = {"response": f"Here's a summary of the article: {clean_text(response_text)}"}

    # Handle entity-related queries
    elif any(keyword in user_input for keyword in ["entities", "people", "places"]):
        entities = analyze_text_with_spacy(article_text)
        response = {"response": f"Named entities in the article: {entities}"}

    # Handle author-related queries
    elif any(keyword in user_input for keyword in ["who wrote", "author", "writer", "creator"]):
        response_text = get_article_author(article_id)
        response = {"response": response_text}

    # Default response for unrecognized or irrelevant input
    else:
        response = {"response": "I'm not sure about your question, could you please rephrase that?"}

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)