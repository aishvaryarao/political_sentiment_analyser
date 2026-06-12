import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DATABASE', 'political_sentiment_db')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.connection = None

    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Disconnected from MySQL")

    def insert_headline(self, keyword, headline, description, url, source_name, sentiment, score):
        """Insert a single headline into the database"""
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO headlines 
                (keyword, headline, description, url, source_name, sentiment, score, date_created)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            values = (keyword, headline, description, url, source_name, sentiment, score)
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error inserting headline: {e}")
            return False

    def insert_multiple_headlines(self, headlines_data):
        """Insert multiple headlines at once"""
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO headlines 
                (keyword, headline, description, url, source_name, sentiment, score, date_created)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.executemany(query, headlines_data)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error inserting multiple headlines: {e}")
            return False

    def get_headlines_by_keyword(self, keyword, days=7):
        """Fetch headlines for a keyword from the last N days"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM headlines 
                WHERE keyword = %s AND date_created >= DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY date_created DESC
            """
            cursor.execute(query, (keyword, days))
            headlines = cursor.fetchall()
            cursor.close()
            return headlines
        except Error as e:
            print(f"Error fetching headlines: {e}")
            return []

    def get_sentiment_breakdown(self, keyword, days=7):
        """Get sentiment count breakdown for a keyword"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT sentiment, COUNT(*) as count, AVG(score) as avg_score
                FROM headlines 
                WHERE keyword = %s AND date_created >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY sentiment
            """
            cursor.execute(query, (keyword, days))
            breakdown = cursor.fetchall()
            cursor.close()
            return breakdown
        except Error as e:
            print(f"Error fetching sentiment breakdown: {e}")
            return []

    def get_sentiment_trend(self, keyword, days=7):
        """Get daily sentiment trend for a keyword"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT DATE(date_created) as date, sentiment, COUNT(*) as count, AVG(score) as avg_score
                FROM headlines 
                WHERE keyword = %s AND date_created >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY DATE(date_created), sentiment
                ORDER BY date ASC
            """
            cursor.execute(query, (keyword, days))
            trend = cursor.fetchall()
            cursor.close()
            return trend
        except Error as e:
            print(f"Error fetching sentiment trend: {e}")
            return []

    def get_all_keywords(self):
        """Get list of all unique keywords in database"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT DISTINCT keyword FROM headlines ORDER BY keyword ASC"
            cursor.execute(query)
            keywords = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return keywords
        except Error as e:
            print(f"Error fetching keywords: {e}")
            return []

    def get_top_words(self, keyword, days=7, limit=20):
        """Get most common words from headlines for a keyword"""
        try:
            headlines = self.get_headlines_by_keyword(keyword, days)
            if not headlines:
                return {}
            
            # Combine all headlines into one text
            all_text = " ".join([h['headline'] for h in headlines])
            
            # Simple word frequency (without stopwords for now)
            words = all_text.lower().split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort and get top words
            top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:limit])
            return top_words
        except Exception as e:
            print(f"Error getting top words: {e}")
            return {}

    def get_latest_headlines(self, keyword, limit=10):
        """Get latest headlines for a keyword"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT headline, sentiment, score, url, date_created
                FROM headlines 
                WHERE keyword = %s
                ORDER BY date_created DESC
                LIMIT %s
            """
            cursor.execute(query, (keyword, limit))
            headlines = cursor.fetchall()
            cursor.close()
            return headlines
        except Error as e:
            print(f"Error fetching latest headlines: {e}")
            return []

# Create a global instance
db = DatabaseManager()