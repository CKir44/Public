import subprocess
# never got the master script to work but it feels pretty cool running them manually,
#this is a step guide in which order to run the procs

# Step 1: Run the Scrapy spider to collect articles and save them to articles.json
print("Running Scrapy spider...")
subprocess.run(["scrapy", "crawl", "article_spider", "-o", "articles.json"])
print("Scrapy spider completed.")

# Step 2: Upload the data from articles.json to the SQL database
print("Uploading data to SQL database...")
subprocess.run(["python", "upload_to_database.py"])
print("Data uploaded to SQL database.")

# Step 3: Analyze the articles from the database
print("Analyzing articles...")
subprocess.run(["python", "analyze_articles.py"])
print("Article analysis completed.")

# Step 4: Save the analysis results back to the SQL database
print("Saving analysis results to SQL database...")
subprocess.run(["python", "save_analysis_results.py"])
print("Analysis results saved.")

#then run chatbot
