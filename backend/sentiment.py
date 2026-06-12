from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import os

# Download VADER lexicon (run once)
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()

    def analyze(self, text):
        """
        Analyze sentiment of text using VADER
        Returns: {
            'sentiment': 'Positive' | 'Negative' | 'Neutral',
            'score': float (0.0 to 1.0),
            'details': {
                'positive': float,
                'negative': float,
                'neutral': float,
                'compound': float
            }
        }
        """
        try:
            scores = self.sia.polarity_scores(text)
            compound = scores['compound']
            
            # Determine sentiment based on compound score
            if compound >= 0.05:
                sentiment = 'Positive'
            elif compound <= -0.05:
                sentiment = 'Negative'
            else:
                sentiment = 'Neutral'
            
            # Normalize compound score to 0-1 range
            normalized_score = (compound + 1) / 2
            
            return {
                'sentiment': sentiment,
                'score': round(normalized_score, 4),
                'details': {
                    'positive': round(scores['pos'], 4),
                    'negative': round(scores['neg'], 4),
                    'neutral': round(scores['neu'], 4),
                    'compound': round(scores['compound'], 4)
                }
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'Neutral',
                'score': 0.5,
                'details': {}
            }

    def batch_analyze(self, texts):
        """
        Analyze sentiment of multiple texts
        Returns: list of sentiment analysis results
        """
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results

# Create a global instance
analyzer = SentimentAnalyzer()