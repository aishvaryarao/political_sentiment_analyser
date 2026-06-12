# Political Sentiment Dashboard

A real-time political sentiment analysis dashboard that fetches live news headlines, analyzes sentiment using Natural Language Processing (NLP), stores results in MySQL, and visualizes sentiment trends through an interactive dashboard.

## Features

* Fetches live political news using NewsAPI
* Performs sentiment analysis using VADER (NLTK)
* Classifies headlines as Positive, Negative, or Neutral
* Stores analyzed data in MySQL
* Interactive dashboard built with Plotly Dash
* Sentiment breakdown visualization
* Sentiment trend analysis
* Latest headlines table
* Word cloud generation for common headline keywords

## Tech Stack

### Frontend

* Plotly Dash
* HTML
* CSS

### Backend

* Python
* FastAPI

### Data Processing

* pandas
* NLTK (VADER Sentiment Analysis)

### Database

* MySQL

### External APIs

* NewsAPI

## Project Architecture

```text
User Keyword Input
        ↓
FastAPI Backend
        ↓
NewsAPI Headline Fetching
        ↓
VADER Sentiment Analysis
        ↓
MySQL Storage
        ↓
Plotly Dash Visualization
```

## Dashboard Components

* Sentiment Distribution Chart
* Sentiment Trend Analysis
* Latest Headlines Table
* Word Cloud Visualization

## Installation

### Clone Repository

```bash
git clone https://github.com/aishvaryarao/political_sentiment_analyser.git

cd political_sentiment_analyser
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
NEWS_API_KEY=your_newsapi_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=political_sentiment_db
MYSQL_PORT=3306
```

### Run Backend

```bash
uvicorn backend.main:app --reload
```

### Run Dashboard

```bash
python frontend/dashboard.py
```

## API Endpoints

* GET `/health`
* GET `/health/database`
* GET `/health/newsapi`
* POST `/api/analyze`
* GET `/api/headlines/{keyword}`
* GET `/api/sentiment-breakdown/{keyword}`
* GET `/api/sentiment-trend/{keyword}`

## Sample Workflow

1. Enter a political keyword (e.g., BJP, Congress, Narendra Modi)
2. Fetch latest news headlines from NewsAPI
3. Analyze sentiment using VADER
4. Store results in MySQL
5. Visualize sentiment insights through the dashboard

## Future Improvements

* Replace VADER with BERT/Transformer-based sentiment analysis for improved accuracy on political news.
* Add political bias detection to identify left-leaning, right-leaning, or neutral reporting.
* Support multiple news sources and compare sentiment across different media outlets.
* Implement historical trend analysis for long-term sentiment tracking.
* Add real-time dashboard updates without manual refresh.
* Deploy the application on cloud platforms.
* Improve keyword filtering to reduce irrelevant news results.

## Screenshots

*Add dashboard screenshots here.*

## Author

**Aishvarya V**
