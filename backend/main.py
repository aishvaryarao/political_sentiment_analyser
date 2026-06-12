from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os
from dotenv import load_dotenv

from backend.database import db
from backend.sentiment import analyzer
from backend.newsapi_handler import news_api

load_dotenv()

app = FastAPI(
    title="Political Sentiment Dashboard API",
    description="Analyze political sentiment from news headlines",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Pydantic Models
# ========================

class KeywordRequest(BaseModel):
    keyword: str

class HeadlineResponse(BaseModel):
    headline: str
    sentiment: str
    score: float
    url: str
    source_name: str

class SentimentBreakdown(BaseModel):
    sentiment: str
    count: int
    avg_score: float

class TrendData(BaseModel):
    date: str
    sentiment: str
    count: int
    avg_score: float

# ========================
# Health Check
# ========================

@app.get("/health")
def health_check():
    """Check if API is running"""
    return {
        "status": "API is running",
        "service": "Political Sentiment Dashboard API"
    }

# ========================
# Database Health
# ========================

@app.get("/health/database")
def database_health():
    """Check database connection"""
    if db.connect():
        db.disconnect()
        return {
            "status": "Database is connected",
            "database": os.getenv('MYSQL_DATABASE', 'political_sentiment_db')
        }
    else:
        raise HTTPException(status_code=500, detail="Cannot connect to database")

# ========================
# NewsAPI Health
# ========================

@app.get("/health/newsapi")
def newsapi_health():
    """Check NewsAPI key validity"""
    validation = news_api.validate_api_key()
    if validation['valid']:
        return {
            "status": " NewsAPI key is valid",
            "message": validation['message']
        }
    else:
        raise HTTPException(status_code=400, detail=validation['message'])

# ========================
# Analyze Headlines Endpoint
# ========================

@app.post("/api/analyze")
def analyze_keyword(request: KeywordRequest):
    """
    Fetch headlines for a keyword and analyze sentiment
    
    Steps:
    1. Fetch headlines from NewsAPI
    2. Analyze sentiment of each headline using VADER
    3. Store in MySQL database
    4. Return results
    """
    keyword = request.keyword.strip()
    
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    
    if len(keyword) > 100:
        raise HTTPException(status_code=400, detail="Keyword too long (max 100 characters)")
    
    # Connect to database
    if not db.connect():
        raise HTTPException(status_code=500, detail="Cannot connect to database")
    
    try:
        # Fetch headlines from NewsAPI
        news_result = news_api.fetch_headlines(keyword, page_size=20)
        
        if not news_result['success']:
            raise HTTPException(status_code=400, detail=news_result['message'])
        
        articles = news_result['articles']
        
        if not articles:
            raise HTTPException(status_code=404, detail=f"No articles found for '{keyword}'")
        
        # Analyze sentiment and prepare data for storage
        headlines_to_store = []
        analyzed_results = []
        
        for article in articles:
            headline = article['headline']
            description = article['description']
            
            # Analyze sentiment (use headline + description for better analysis)
            text_to_analyze = f"{headline}. {description}"
            sentiment_result = analyzer.analyze(text_to_analyze)
            
            # Prepare data for database storage
            headlines_to_store.append((
                keyword,
                headline,
                description,
                article['url'],
                article['source_name'],
                sentiment_result['sentiment'],
                sentiment_result['score']
            ))
            
            # Prepare response data
            analyzed_results.append({
                'headline': headline,
                'description': description,
                'sentiment': sentiment_result['sentiment'],
                'score': sentiment_result['score'],
                'url': article['url'],
                'source_name': article['source_name'],
                'sentiment_details': sentiment_result['details']
            })
        
        # Store in database
        if headlines_to_store:
            db.insert_multiple_headlines(headlines_to_store)
        
        return {
            'status': 'Analysis complete',
            'keyword': keyword,
            'total_articles': len(analyzed_results),
            'articles': analyzed_results,
            'message': f"Analyzed {len(analyzed_results)} articles for '{keyword}'"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        db.disconnect()

# ========================
# Get Headlines by Keyword
# ========================

@app.get("/api/headlines/{keyword}")
def get_headlines(keyword: str, days: int = 7, limit: int = 10):
    """
    Get stored headlines for a keyword from the last N days
    """
    keyword = keyword.strip()
    
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    
    if not db.connect():
        raise HTTPException(status_code=500, detail="Cannot connect to database")
    
    try:
        headlines = db.get_latest_headlines(keyword, limit)
        
        if not headlines:
            raise HTTPException(status_code=404, detail=f"No headlines found for '{keyword}'")
        
        return {
            'status': ' Headlines retrieved',
            'keyword': keyword,
            'count': len(headlines),
            'headlines': headlines
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        db.disconnect()

# ========================
# Get Sentiment Breakdown
# ========================

@app.get("/api/sentiment-breakdown/{keyword}")
def get_sentiment_breakdown(keyword: str, days: int = 7):
    """
    Get sentiment breakdown (counts of positive, negative, neutral)
    for a keyword from the last N days
    """
    keyword = keyword.strip()
    
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    
    if not db.connect():
        raise HTTPException(status_code=500, detail="Cannot connect to database")
    
    try:
        breakdown = db.get_sentiment_breakdown(keyword, days)
        
        if not breakdown:
            raise HTTPException(status_code=404, detail=f"No sentiment data found for '{keyword}'")
        
        return {
            'status': 'Sentiment breakdown retrieved',
            'keyword': keyword,
            'days': days,
            'breakdown': breakdown
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        db.disconnect()

# ========================
# Get Sentiment Trend
# ========================

@app.get("/api/sentiment-trend/{keyword}")
def get_sentiment_trend(keyword: str, days: int = 7):
    """
    Get daily sentiment trend for a keyword
    """
    keyword = keyword.strip()
    
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    
    if not db.connect():
        raise HTTPException(status_code=500, detail="Cannot connect to database")
    
    try:
        trend = db.get_sentiment_trend(keyword, days)
        
        if not trend:
            raise HTTPException(status_code=404, detail=f"No trend data found for '{keyword}'")
        
        return {
            'status': 'Sentiment trend retrieved',
            'keyword': keyword,
            'days': days,
            'trend': trend
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        db.disconnect()

# ========================
# Get Top Words
# ========================

@app.get("/api/top-words/{keyword}")
def get_top_words(keyword: str, days: int = 7, limit: int = 20):
    """
    Get most common words from headlines for a keyword
    (used for wordcloud)
    """
    keyword = keyword.strip()
    
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    
    if not db.connect():
        raise HTTPException(status_code=500, detail="Cannot connect to database")
    
    try:
        words = db.get_top_words(keyword, days, limit)
        
        if not words:
            raise HTTPException(status_code=404, detail=f"No words found for '{keyword}'")
        
        return {
            'status': 'Top words retrieved',
            'keyword': keyword,
            'words': words
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        db.disconnect()

# ========================
# Get All Keywords
# ========================

@app.get("/api/keywords")
def get_all_keywords():
    """
    Get list of all keywords searched so far
    """
    if not db.connect():
        raise HTTPException(status_code=500, detail="Cannot connect to database")
    
    try:
        keywords = db.get_all_keywords()
        
        return {
            'status': 'Keywords retrieved',
            'count': len(keywords),
            'keywords': keywords
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        db.disconnect()

# ========================
# Root Endpoint
# ========================

@app.get("/")
def root():
    """Root endpoint with API documentation"""
    return {
        "message": " Political Sentiment Dashboard API",
        "docs": "Visit /docs for interactive API documentation",
        "endpoints": {
            "health": "/health",
            "database_health": "/health/database",
            "newsapi_health": "/health/newsapi",
            "analyze": "POST /api/analyze",
            "headlines": "GET /api/headlines/{keyword}",
            "sentiment_breakdown": "GET /api/sentiment-breakdown/{keyword}",
            "sentiment_trend": "GET /api/sentiment-trend/{keyword}",
            "top_words": "GET /api/top-words/{keyword}",
            "keywords": "GET /api/keywords"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv('FASTAPI_HOST', '0.0.0.0'),
        port=int(os.getenv('FASTAPI_PORT', 8000))
    )