import scrapy
import os
from pathlib import Path

class ArticleSpider(scrapy.Spider):
    name = "article_spider"

    # Define the local folder path where the articles are stored
    folder_path = r'C:\Users\crkir\PycharmProjects\AzureScraperProject\Articles Html'

    def start_requests(self):
        # Generate file URLs for all HTML files in the specified folder
        for file in os.listdir(self.folder_path):
            if file.endswith('.html'):
                file_path = Path(self.folder_path) / file
                file_url = f'file:///{file_path.as_posix()}'  # Ensure file URL format
                yield scrapy.Request(url=file_url, callback=self.parse)

    def parse(self, response):
        # Extract the article content (assuming <p> tags hold the article's text)
        paragraphs = response.css('p::text').getall()
        article_text = ' '.join(paragraphs)

        # Yield the scraped text to be saved in the output file
        yield {
            'file': response.url,
            'text': article_text
        }
