import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objs as go
import plotly.express as px
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd
from wordcloud import WordCloud
import base64
from io import BytesIO

load_dotenv()

# API Configuration
FASTAPI_URL = f"http://localhost:{os.getenv('FASTAPI_PORT', 8000)}"

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Political Sentiment Dashboard"

# ========================
# Styling
# ========================

external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap',
        'rel': 'stylesheet'
    }
]

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Roboto', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .dashboard-container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                padding: 40px;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                border-bottom: 3px solid #667eea;
                padding-bottom: 20px;
            }
            .header h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            .input-section {
                display: flex;
                gap: 15px;
                margin-bottom: 30px;
                flex-wrap: wrap;
                align-items: center;
            }
            .input-section input {
                flex: 1;
                min-width: 250px;
                padding: 12px 15px;
                font-size: 1em;
                border: 2px solid #ddd;
                border-radius: 8px;
                transition: border-color 0.3s;
            }
            .input-section input:focus {
                outline: none;
                border-color: #667eea;
            }
            .input-section button {
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .input-section button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            .input-section button:active {
                transform: translateY(0);
            }
            .status-message {
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-weight: 500;
            }
            .status-message.success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status-message.error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .status-message.loading {
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .charts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 30px;
                margin-bottom: 30px;
            }
            .chart-container {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }
            .chart-container h3 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .full-width {
                grid-column: 1 / -1;
            }
            .table-container {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
            .table-container h3 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th {
                background: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }
            td {
                padding: 12px;
                border-bottom: 1px solid #ddd;
            }
            tr:hover {
                background: #f0f0f0;
            }
            .sentiment-positive {
                color: #28a745;
                font-weight: 600;
            }
            .sentiment-negative {
                color: #dc3545;
                font-weight: 600;
            }
            .sentiment-neutral {
                color: #6c757d;
                font-weight: 600;
            }
            .loading-spinner {
                text-align: center;
                padding: 40px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .no-data {
                text-align: center;
                padding: 40px;
                color: #999;
                font-size: 1.1em;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer></footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

# ========================
# App Layout
# ========================

app.layout = html.Div([
    html.Div([
        # Header
        html.Div([
            html.H1("Political Sentiment Dashboard"),
            html.P("Analyze sentiment from news headlines in real-time")
        ], className='header'),
        
        # Input Section
        html.Div([
            dcc.Input(
                id='keyword-input',
                type='text',
                placeholder='Enter keyword (e.g., BJP, Congress, Elections)',
                className='input-section',
                style={'flex': '1', 'minWidth': '250px', 'padding': '12px 15px', 
                       'fontSize': '1em', 'border': '2px solid #ddd', 'borderRadius': '8px'}
            ),
            html.Button(
                'Analyze Sentiment',
                id='analyze-button',
                n_clicks=0,
                style={'padding': '12px 30px', 'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                       'color': 'white', 'border': 'none', 'borderRadius': '8px', 'fontSize': '1em',
                       'fontWeight': '600', 'cursor': 'pointer', 'transition': 'transform 0.2s, box-shadow 0.2s'}
            )
        ], className='input-section'),
        
        # Status Message
        html.Div(id='status-message', style={'marginBottom': '20px'}),
        
        # Loading Indicator
        html.Div(id='loading-indicator'),
        
        # Charts Grid
        html.Div([
            # Sentiment Breakdown Bar Chart
            html.Div([
                html.H3("Sentiment Breakdown"),
                dcc.Graph(id='sentiment-breakdown-chart')
            ], className='chart-container'),
            
            # Sentiment Score Distribution
            html.Div([
                html.H3("Score Distribution"),
                dcc.Graph(id='score-distribution-chart')
            ], className='chart-container'),
        ], className='charts-grid'),
        
        # Sentiment Trend Chart
        html.Div([
            html.Div([
                html.H3("Sentiment Trend (7 Days)"),
                dcc.Graph(id='sentiment-trend-chart')
            ], className='chart-container')
        ], className='charts-grid'),
        
        # Wordcloud
        html.Div([
            html.Div([
                html.H3("Word Cloud"),
                html.Img(id='wordcloud-image', style={'width': '100%', 'borderRadius': '8px'})
            ], className='chart-container full-width')
        ], className='charts-grid'),
        
        # Headlines Table
        html.Div([
            html.H3("Latest Headlines"),
            html.Div(id='headlines-table-container')
        ], className='table-container full-width'),
        
        # Store data
        dcc.Store(id='analysis-data'),
        
    ], className='dashboard-container'),
], style={'backgroundColor': 'transparent'})

# ========================
# Callbacks
# ========================

@app.callback(
    [Output('status-message', 'children'),
     Output('status-message', 'className'),
     Output('analysis-data', 'data'),
     Output('loading-indicator', 'children')],
    Input('analyze-button', 'n_clicks'),
    State('keyword-input', 'value'),
    prevent_initial_call=True
)
def analyze_keyword(n_clicks, keyword):
    """Analyze sentiment for keyword"""
    if not keyword or keyword.strip() == '':
        return 'Please enter a keyword', 'status-message error', {}, ''
    
    keyword = keyword.strip()
    
    # Show loading
    loading = html.Div([
        html.Div(className='spinner'),
        html.P('Fetching and analyzing headlines...', style={'marginTop': '15px', 'color': '#666'})
    ], className='loading-spinner')
    
    try:
        # Call FastAPI endpoint
        response = requests.post(
            f'{FASTAPI_URL}/api/analyze',
            json={'keyword': keyword},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            status_msg = f" {data['message']} - {len(data['articles'])} articles analyzed"
            return status_msg, 'status-message success', data, ''
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            return f"Error: {error_msg}", 'status-message error', {}, ''
    
    except requests.exceptions.Timeout:
        return 'Request timeout. Please try again.', 'status-message error', {}, ''
    except Exception as e:
        return f'Error: {str(e)}', 'status-message error', {}, ''

@app.callback(
    Output('sentiment-breakdown-chart', 'figure'),
    Input('analysis-data', 'data'),
    prevent_initial_call=True
)
def update_sentiment_breakdown(data):
    """Update sentiment breakdown chart"""
    if not data or 'articles' not in data:
        return go.Figure().add_annotation(text='No data available', showarrow=False)
    
    articles = data['articles']
    sentiments = {}
    
    for article in articles:
        sentiment = article['sentiment']
        sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
    
    fig = go.Figure([
        go.Bar(
            x=list(sentiments.keys()),
            y=list(sentiments.values()),
            marker=dict(
                color=["#ff0000", "#21d727", '#6c757d'],
                line=dict(color='rgba(0,0,0,0)')
            ),
            text=list(sentiments.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Sentiment Breakdown',
        xaxis_title='Sentiment',
        yaxis_title='Count',
        showlegend=False,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

@app.callback(
    Output('score-distribution-chart', 'figure'),
    Input('analysis-data', 'data'),
    prevent_initial_call=True
)
def update_score_distribution(data):
    """Update score distribution chart"""
    if not data or 'articles' not in data:
        return go.Figure().add_annotation(text='No data available', showarrow=False)
    
    articles = data['articles']
    scores = [article['score'] for article in articles]
    
    fig = go.Figure([
        go.Histogram(
            x=scores,
            nbinsx=20,
            marker=dict(color='#667eea'),
        )
    ])
    
    fig.update_layout(
        title='Score Distribution',
        xaxis_title='Sentiment Score',
        yaxis_title='Frequency',
        showlegend=False,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

@app.callback(
    Output('sentiment-trend-chart', 'figure'),
    Input('analysis-data', 'data'),
    prevent_initial_call=True
)
def update_sentiment_trend(data):
    """Update sentiment trend chart"""
    if not data or 'keyword' not in data:
        return go.Figure().add_annotation(text='No data available', showarrow=False)
    
    keyword = data['keyword']
    
    try:
        response = requests.get(
            f'{FASTAPI_URL}/api/sentiment-trend/{keyword}?days=7',
            timeout=10
        )
        
        if response.status_code == 200:
            trend_data = response.json()['trend']
            df = pd.DataFrame(trend_data)
            
            fig = go.Figure()
            
            for sentiment in df['sentiment'].unique():
                df_sentiment = df[df['sentiment'] == sentiment]
                color = {'Positive': '#28a745', 'Negative': '#dc3545', 'Neutral': '#6c757d'}.get(sentiment, '#999')
                
                fig.add_trace(go.Scatter(
                    x=df_sentiment['date'],
                    y=df_sentiment['count'],
                    name=sentiment,
                    mode='lines+markers',
                    line=dict(color=color, width=2),
                    marker=dict(size=8)
                ))
            
            fig.update_layout(
                title='Sentiment Trend (7 Days)',
                xaxis_title='Date',
                yaxis_title='Count',
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
        else:
            return go.Figure().add_annotation(text='No trend data available', showarrow=False)
    
    except Exception as e:
        return go.Figure().add_annotation(text=f'Error loading trend: {str(e)}', showarrow=False)

@app.callback(
    Output('wordcloud-image', 'src'),
    Input('analysis-data', 'data'),
    prevent_initial_call=True
)
def update_wordcloud(data):
    """Update wordcloud image"""
    if not data or 'keyword' not in data:
        return ''
    
    keyword = data['keyword']
    
    try:
        response = requests.get(
            f'{FASTAPI_URL}/api/top-words/{keyword}?days=7&limit=50',
            timeout=10
        )
        
        if response.status_code == 200:
            words_data = response.json()['words']
            
            if not words_data:
                return ''
            
            # Generate wordcloud
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                colormap='viridis',
                relative_scaling=0.5,
                min_font_size=10
            ).generate_from_frequencies(words_data)
            
            # Convert to base64 image
            img = BytesIO()
            wordcloud.to_image().save(img, format='PNG')
            img.seek(0)
            img_base64 = base64.b64encode(img.getvalue()).decode()
            
            return f'data:image/png;base64,{img_base64}'
        else:
            return ''
    
    except Exception as e:
        print(f'Error generating wordcloud: {e}')
        return ''

@app.callback(
    Output('headlines-table-container', 'children'),
    Input('analysis-data', 'data'),
    prevent_initial_call=True
)
def update_headlines_table(data):
    """Update headlines table"""
    if not data or 'articles' not in data:
        return html.Div('No headlines available', className='no-data')
    
    articles = data['articles']
    
    rows = []
    for article in articles[:10]:  # Show top 10
        sentiment = article['sentiment']
        sentiment_class = f'sentiment-{sentiment.lower()}'
        
        rows.append(html.Tr([
            html.Td(article['headline'][:80] + '...', style={'maxWidth': '400px'}),
            html.Td(html.Span(article['sentiment'], className=sentiment_class)),
            html.Td(f"{article['score']:.2%}"),
            html.Td(article['source_name']),
            html.Td(html.A('Read', href=article['url'], target='_blank', 
                           style={'color': '#667eea', 'textDecoration': 'none'}))
        ]))
    
    return html.Table([
        html.Thead(html.Tr([
            html.Th('Headline'),
            html.Th('Sentiment'),
            html.Th('Score'),
            html.Th('Source'),
            html.Th('Link')
        ])),
        html.Tbody(rows)
    ])

# ========================
# Run
# ========================

if __name__ == '__main__':
    app.run_server(
        debug=True,
        host=os.getenv('DASH_HOST', '0.0.0.0'),
        port=int(os.getenv('DASH_PORT', 8050))
    )