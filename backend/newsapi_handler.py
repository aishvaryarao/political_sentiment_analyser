import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class NewsAPIHandler:
    def __init__(self):
        self.api_key = os.getenv('NEWSAPI_KEY', '')
        self.base_url = "https://newsapi.org/v2"
        
        if not self.api_key or self.api_key == 'your_newsapi_key_here':
            print("⚠️  Warning: NewsAPI key not configured in .env file")

    def fetch_headlines(self, keyword, sort_by='publishedAt', page_size=20):
        """
        Fetch headlines from NewsAPI for a given keyword
        
        Args:
            keyword: Search term (e.g., "BJP", "Congress", "elections")
            sort_by: 'publishedAt' | 'relevancy' | 'popularity'
            page_size: Number of articles to fetch (max 100)
        
        Returns:
            {
                'success': bool,
                'articles': list of articles,
                'total_results': int,
                'message': str
            }
        """
        try:
            if not self.api_key or self.api_key == 'your_newsapi_key_here':
                return {
                    'success': False,
                    'articles': [],
                    'total_results': 0,
                    'message': 'NewsAPI key not configured. Please add NEWSAPI_KEY to .env file'
                }
            
            # Endpoint: /v2/everything
            endpoint = f"{self.base_url}/everything"
            
            params = {
                'q': keyword,
                'sortBy': sort_by,
                'pageSize': page_size,
                'apiKey': self.api_key,
                'language': 'en'
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'ok':
                    articles = self._clean_articles(data.get('articles', []))
                    return {
                        'success': True,
                        'articles': articles,
                        'total_results': data.get('totalResults', 0),
                        'message': f"Fetched {len(articles)} articles for '{keyword}'"
                    }
                else:
                    error_msg = data.get('message', 'Unknown error')
                    return {
                        'success': False,
                        'articles': [],
                        'total_results': 0,
                        'message': f"API Error: {error_msg}"
                    }
            else:
                return {
                    'success': False,
                    'articles': [],
                    'total_results': 0,
                    'message': f"HTTP Error {response.status_code}"
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'articles': [],
                'total_results': 0,
                'message': 'Request timeout. Try again later.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'articles': [],
                'total_results': 0,
                'message': f"Request error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'articles': [],
                'total_results': 0,
                'message': f"Error fetching headlines: {str(e)}"
            }

    def _clean_articles(self, articles):
        """
        Clean and standardize article data
        """
        cleaned = []
        for article in articles:
            cleaned_article = {
                'headline': article.get('title', 'N/A'),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'source_name': article.get('source', {}).get('name', 'Unknown'),
                'published_at': article.get('publishedAt', ''),
                'image_url': article.get('urlToImage', ''),
                'author': article.get('author', 'Unknown')
            }
            cleaned.append(cleaned_article)
        return cleaned

    def validate_api_key(self):
        """
        Validate if API key is working
        """
        try:
            if not self.api_key or self.api_key == 'your_newsapi_key_here':
                return {
                    'valid': False,
                    'message': 'API key not configured'
                }
            
            endpoint = f"{self.base_url}/top-headlines"
            params = {
                'country': 'us',
                'pageSize': 1,
                'apiKey': self.api_key
            }
            
            response = requests.get(endpoint, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok':
                    return {
                        'valid': True,
                        'message': 'API key is valid'
                    }
                else:
                    return {
                        'valid': False,
                        'message': f"API Error: {data.get('message', 'Unknown error')}"
                    }
            elif response.status_code == 401:
                return {
                    'valid': False,
                    'message': 'Invalid API key (401 Unauthorized)'
                }
            else:
                return {
                    'valid': False,
                    'message': f"HTTP Error {response.status_code}"
                }
        
        except Exception as e:
            return {
                'valid': False,
                'message': f"Error validating API key: {str(e)}"
            }

# Create a global instance
news_api = NewsAPIHandler()