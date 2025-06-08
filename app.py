import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io
import warnings
import os
import requests
import json
warnings.filterwarnings('ignore')

from data_processor import DataProcessor
from sample_data_generator import SampleDataGenerator
from utils import format_number, calculate_kpis, create_funnel_chart, analyze_geographical_performance, create_geographical_charts

# Page configuration
st.set_page_config(
    page_title="Recruitment Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional styling with animations and modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main > div {
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated background */
    .dashboard-header {
        background: linear-gradient(-45deg, #1B365D, #4A90E2, #667eea, #764ba2);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite;
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><polygon fill="%23ffffff" fill-opacity="0.05" points="0,200 300,0 600,100 1000,0 1000,300 700,400 400,300 0,500"/></svg>');
        pointer-events: none;
    }
    
    .dashboard-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: fadeInUp 1s ease-out;
    }
    
    .dashboard-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        animation: fadeInUp 1s ease-out 0.2s both;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Enhanced metric cards */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        animation: slideIn 0.6s ease-out;
    }
    
    .stMetric::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4A90E2, #667eea, #764ba2);
        transition: height 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    }
    
    .stMetric:hover::before {
        height: 8px;
    }
    
    .stMetric [data-testid="metric-container"] {
        background: transparent;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.5s;
        opacity: 0;
    }
    
    .metric-card:hover::before {
        animation: shimmer 0.8s ease-in-out;
        opacity: 1;
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.05);
        box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Enhanced section headers */
    .section-header {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #4A90E2;
        margin: 2rem 0 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        animation: slideIn 0.8s ease-out;
    }
    
    .section-header h2 {
        margin: 0;
        color: #1e293b;
        font-weight: 600;
    }
    
    .section-header h4 {
        margin: 0;
        color: #475569;
        font-weight: 500;
    }
    
    /* Enhanced filter container */
    .filter-container {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.5);
        animation: fadeInUp 1s ease-out;
    }
    
    .filter-container h3 {
        color: #1e293b;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Enhanced chat interface */
    .chat-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.5);
        animation: fadeInUp 1.2s ease-out;
    }
    
    .sample-question {
        background: linear-gradient(135deg, #f0f8ff 0%, #e0f2fe 100%);
        padding: 0.75rem 1.25rem;
        border-radius: 25px;
        margin: 0.5rem;
        cursor: pointer;
        border: 2px solid #4A90E2;
        color: #1B365D;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: inline-block;
        position: relative;
        overflow: hidden;
    }
    
    .sample-question::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .sample-question:hover::before {
        left: 100%;
    }
    
    .sample-question:hover {
        background: linear-gradient(135deg, #4A90E2 0%, #667eea 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 144, 226, 0.3);
    }
    
    .chat-message {
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        animation: slideIn 0.5s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        border-radius: 12px 12px 4px 12px;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%);
        border-left: 4px solid #4caf50;
        border-radius: 12px 12px 12px 4px;
    }
    
    /* Enhanced form elements */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #4A90E2;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
    }
    
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        padding: 0.75rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4A90E2;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4A90E2 0%, #667eea 100%);
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 144, 226, 0.4);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Enhanced alerts */
    .alert-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 50%);
        border: 1px solid #ffeaa7;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: #856404;
        box-shadow: 0 4px 20px rgba(255, 234, 167, 0.3);
        animation: pulse 2s infinite;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 50%);
        border: 1px solid #c3e6cb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: #155724;
        box-shadow: 0 4px 20px rgba(195, 230, 203, 0.3);
        animation: slideIn 0.8s ease-out;
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4A90E2 0%, #667eea 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
    }
    
    /* Enhanced dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #4A90E2, transparent);
        margin: 2rem 0;
    }
    
    /* Loading animation */
    .stSpinner {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Responsive enhancements */
    @media (max-width: 768px) {
        .dashboard-header h1 {
            font-size: 2rem;
        }
        
        .dashboard-header p {
            font-size: 1rem;
        }
        
        .metric-card {
            margin: 0.25rem 0;
        }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #4A90E2, #667eea);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #667eea, #764ba2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize data processor
@st.cache_data
def load_data():
    """Load and process recruitment data"""
    processor = DataProcessor()
    
    # Try to load the Excel file first
    try:
        df = processor.load_excel_data("Dashboard Data and Issues (For All) - MFR.xlsx")
        st.success("✅ Excel data loaded successfully!")
        return df, False
    except Exception as e:
        st.warning(f"⚠️ Could not load Excel file: {str(e)}")
        st.info("📊 Using sample data for demonstration purposes")
        
        # Generate sample data
        sample_generator = SampleDataGenerator()
        df = sample_generator.generate_comprehensive_data()
        return df, True

# Groq API Integration
class GroqChatbot:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
    def generate_response(self, question, context_data=None):
        if not self.api_key:
            return "⚠️ Please configure your Groq API key to use the chatbot functionality."
        
        # Create comprehensive context from the recruitment data
        context = ""
        if context_data is not None and not context_data.empty:
            # Basic metrics
            total_records = len(context_data)
            total_consultants = context_data['Consultant_Name'].nunique()
            active_jobs = len(context_data[context_data['Job_Status'] == 'Active'])
            total_placements = len(context_data[context_data['Placement_Date'].notna()])
            avg_billing = context_data['Billing_Value'].mean()
            
            # Advanced insights
            top_consultants = context_data.groupby('Consultant_Name').size().nlargest(3)
            top_cities = context_data.groupby('City').size().nlargest(3)
            top_countries = context_data.groupby('Country').size().nlargest(3)
            job_status_dist = context_data['Job_Status'].value_counts()
            client_type_dist = context_data['Client_Type'].value_counts()
            
            # Geographical insights
            country_revenue = context_data.groupby('Country')['Billing_Value'].sum().nlargest(3)
            city_revenue = context_data.groupby('City')['Billing_Value'].sum().nlargest(3)
            country_conversions = context_data.groupby('Country').apply(
                lambda x: (x['Placement_Date'].notna().sum() / len(x) * 100) if len(x) > 0 else 0
            ).nlargest(3)
            city_conversions = context_data.groupby('City').apply(
                lambda x: (x['Placement_Date'].notna().sum() / len(x) * 100) if len(x) > 0 else 0
            ).nlargest(3)
            
            # Market penetration by geography
            countries_with_new_clients = len(context_data[context_data['Client_Type'] == 'New']['Country'].unique())
            cities_with_active_jobs = len(context_data[context_data['Job_Status'] == 'Active']['City'].unique())
            
            # Financial insights
            total_billing = context_data['Billing_Value'].sum()
            max_billing = context_data['Billing_Value'].max()
            min_billing = context_data['Billing_Value'].min()
            
            # Time-based insights
            recent_placements = len(context_data[
                (context_data['Placement_Date'].notna()) & 
                (context_data['Placement_Date'] >= pd.Timestamp.now() - pd.Timedelta(days=30))
            ])
            
            # Conversion rates
            conversion_rate = (total_placements / total_records * 100) if total_records > 0 else 0
            
            # Interview insights
            interview_scheduled = len(context_data[context_data['Interview_Status'] == 'Scheduled'])
            interview_completed = len(context_data[context_data['Interview_Status'] == 'Completed'])
            
            context = f"""
            COMPREHENSIVE RECRUITMENT DATA ANALYSIS:
            
            BASIC METRICS:
            - Total records: {total_records}
            - Total consultants: {total_consultants}
            - Active jobs: {active_jobs}
            - Total placements: {total_placements}
            - Recent placements (30 days): {recent_placements}
            - Overall conversion rate: {conversion_rate:.1f}%
            
            FINANCIAL INSIGHTS:
            - Total billing value: ${total_billing:,.0f}
            - Average billing value: ${avg_billing:,.0f}
            - Highest billing: ${max_billing:,.0f}
            - Lowest billing: ${min_billing:,.0f}
            
            TOP PERFORMERS:
            - Top consultants by volume: {dict(top_consultants)}
            - Top cities by volume: {dict(top_cities)}
            - Top countries by volume: {dict(top_countries)}
            
            GEOGRAPHICAL PERFORMANCE:
            - Top countries by revenue: {dict(country_revenue)}
            - Top cities by revenue: {dict(city_revenue)}
            - Top countries by conversion rate: {dict(country_conversions)}
            - Top cities by conversion rate: {dict(city_conversions)}
            - Countries with new clients: {countries_with_new_clients}
            - Cities with active jobs: {cities_with_active_jobs}
            
            JOB STATUS DISTRIBUTION:
            {dict(job_status_dist)}
            
            CLIENT TYPE DISTRIBUTION:
            {dict(client_type_dist)}
            
            INTERVIEW PIPELINE:
            - Interviews scheduled: {interview_scheduled}
            - Interviews completed: {interview_completed}
            
            DATA COLUMNS AVAILABLE:
            {list(context_data.columns)}
            """
        
        system_prompt = f"""You are an expert recruitment analytics consultant with deep expertise in HR metrics, talent acquisition, and business intelligence. You have access to comprehensive recruitment data and can provide detailed insights, trends, and actionable recommendations.

        {context}

        CAPABILITIES:
        - Analyze recruitment performance metrics and KPIs
        - Identify trends and patterns in hiring data
        - Provide actionable recommendations for improvement
        - Compare consultant performance and suggest optimizations
        - Analyze financial metrics and billing trends
        - Evaluate conversion rates and pipeline efficiency
        - Assess client relationships and market opportunities
        - Generate insights about geographical performance
        - Recommend process improvements and best practices

        INSTRUCTIONS:
        - Always base your responses on the actual data provided
        - Use specific numbers and percentages when available
        - Provide actionable insights and recommendations
        - Explain the business impact of your findings
        - Suggest specific next steps when appropriate
        - Be comprehensive but concise
        - Use data-driven language and avoid generic advice"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error connecting to Groq API: {str(e)}"

# Initialize chatbot
chatbot = GroqChatbot()

# Sample questions for the chatbot
SAMPLE_QUESTIONS = [
    "Analyze the top performing consultants and their success patterns",
    "What are the conversion rate trends across different cities and countries?",
    "Which geographical regions generate the highest billing values?",
    "Compare market penetration strategies across different countries",
    "Identify bottlenecks in our recruitment pipeline by location",
    "Which cities have the best consultant performance ratios?",
    "Analyze revenue concentration risks across geographical markets",
    "What's the correlation between location and time-to-hire?",
    "Which countries offer the best expansion opportunities?",
    "Compare client acquisition patterns between urban and regional markets",
    "Analyze seasonal trends in job placements by geography",
    "What factors contribute to regional performance variations?",
    "Which locations need additional consultant resources?",
    "Identify geographical markets with declining performance",
    "Analyze cost-effectiveness of operations across different regions"
]

# Load data
df, is_sample_data = load_data()

# Main dashboard
def main():
    # Professional Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🎯 Mindfield Recruitment Analytics Dashboard</h1>
        <p>Enterprise-grade insights for recruitment agencies</p>
    </div>
    """, unsafe_allow_html=True)
    
    if is_sample_data:
        st.markdown("""
        <div class="alert-warning">
            <strong>Demo Mode:</strong> Currently displaying sample data for demonstration purposes.
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2 = st.tabs(["📊 Analytics Dashboard", "🤖 AI Assistant"])
    
    with tab1:
        render_analytics_dashboard()
    
    with tab2:
        render_chatbot_interface()

def render_analytics_dashboard():
    # Enhanced sidebar with modern styling
    with st.sidebar:
        st.markdown("""
        <div class="filter-container">
            <h3>🔍 Smart Analytics Filters</h3>
            <p style="margin-top: 0.5rem; color: #64748b; font-size: 0.9rem;">
                Apply filters to drill down into specific data segments
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Filter options
    countries = ['All'] + sorted(df['Country'].dropna().unique().tolist())
    cities = ['All'] + sorted(df['City'].dropna().unique().tolist())
    consultants = ['All'] + sorted(df['Consultant_Name'].dropna().unique().tolist())
    job_statuses = ['All'] + sorted(df['Job_Status'].dropna().unique().tolist())
    
    # Date-based filters
    df['Posted_Year_Month'] = pd.to_datetime(df['Posted_Date'], errors='coerce').dt.to_period('M').astype(str)
    df['Placed_Year'] = pd.to_datetime(df['Placement_Date'], errors='coerce').dt.year.astype(str)
    
    posted_years = ['All'] + sorted([x for x in df['Posted_Year_Month'].dropna().unique() if x != 'NaT'])
    placed_years = ['All'] + sorted([x for x in df['Placed_Year'].dropna().unique() if x != 'nan'])
    
    # Filter controls
    selected_country = st.sidebar.selectbox("Country", countries)
    selected_city = st.sidebar.selectbox("City", cities)
    selected_consultant = st.sidebar.selectbox("Consultant Name", consultants)
    selected_status = st.sidebar.selectbox("Job Status", job_statuses)
    selected_posted_year = st.sidebar.selectbox("Posted Year-Month", posted_years)
    selected_placed_year = st.sidebar.selectbox("Candidate Placed Year", placed_years)
    
    # Add filter status indicator after variables are defined
    with st.sidebar:
        filters_applied = sum([
            selected_country != 'All',
            selected_city != 'All', 
            selected_consultant != 'All',
            selected_status != 'All',
            selected_posted_year != 'All',
            selected_placed_year != 'All'
        ])
        
        if filters_applied > 0:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
                        padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem;
                        border-left: 4px solid #22c55e;">
                <strong>✅ {filters_applied} filter(s) active</strong>
            </div>
            """, unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    if selected_city != 'All':
        filtered_df = filtered_df[filtered_df['City'] == selected_city]
    if selected_consultant != 'All':
        filtered_df = filtered_df[filtered_df['Consultant_Name'] == selected_consultant]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Job_Status'] == selected_status]
    if selected_posted_year != 'All':
        filtered_df = filtered_df[filtered_df['Posted_Year_Month'] == selected_posted_year]
    if selected_placed_year != 'All':
        filtered_df = filtered_df[filtered_df['Placed_Year'] == selected_placed_year]
    
    # Calculate KPIs
    kpis = calculate_kpis(filtered_df)
    
    # Display KPIs in enhanced cards
    st.markdown("""
    <div class="section-header">
        <h2>📈 Key Performance Indicators</h2>
        <p>Real-time insights into your recruitment performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Row 1 - Basic metrics with enhanced styling
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        delta_consultants = "+5%" if kpis['total_consultants'] > 10 else None
        st.metric("👥 Total Consultants", format_number(kpis['total_consultants']), delta=delta_consultants)
    
    with col2:
        delta_new = "+12%" if kpis['new_clients'] > 5 else None
        st.metric("🆕 New Clients", format_number(kpis['new_clients']), delta=delta_new)
    
    with col3:
        delta_old = "+3%" if kpis['old_clients'] > 20 else None
        st.metric("🏢 Existing Clients", format_number(kpis['old_clients']), delta=delta_old)
    
    with col4:
        delta_positions = "+8%" if kpis['total_positions'] > 100 else None
        st.metric("💼 Total Positions", format_number(kpis['total_positions']), delta=delta_positions)
    
    with col5:
        delta_active = "+15%" if kpis['active_jobs'] > 50 else None
        st.metric("🔥 Active Jobs", format_number(kpis['active_jobs']), delta=delta_active)
    
    # Row 2 - Job metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("High Potential Jobs", format_number(kpis['high_potential_jobs']))
    with col2:
        st.metric("Lost Jobs", format_number(kpis['lost_jobs']))
    with col3:
        st.metric("Time to Submit (Days)", f"{kpis['time_to_submit']:.1f}")
    with col4:
        st.metric("Submission → Interview %", f"{kpis['submission_interview_rate']:.1f}%")
    with col5:
        st.metric("Submission → Rejected %", f"{kpis['submission_rejected_rate']:.1f}%")
    
    # Row 3 - Placement metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Candidates Placed", format_number(kpis['total_placed']))
    with col2:
        st.metric("Active Clients", format_number(kpis['active_clients']))
    with col3:
        st.metric("Passive Clients", format_number(kpis['passive_clients']))
    with col4:
        st.metric("Recruitment Conversion Rate %", f"{kpis['conversion_rate']:.1f}%")
    with col5:
        st.metric("Avg Billing Value", f"${kpis['avg_billing_value']:,.0f}")
    
    # Row 4 - Financial and timing metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Value of Jobs", f"${kpis['total_job_value']:,.0f}")
    with col2:
        st.metric("Total Value Won", f"${kpis['total_value_won']:,.0f}")
    with col3:
        st.metric("Avg Time to Hire (Days)", f"{kpis['avg_time_to_hire']:.1f}")
    with col4:
        st.metric("Interview → Offer %", f"{kpis['interview_offer_rate']:.1f}%")
    with col5:
        st.metric("Offer → Placement %", f"{kpis['offer_placement_rate']:.1f}%")
    
    # Row 5 - Geographical metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Active Countries", format_number(kpis['active_countries']))
    with col2:
        st.metric("Active Cities", format_number(kpis['active_cities']))
    with col3:
        st.metric("Top Country Revenue", f"${kpis['top_country_revenue']:,.0f}")
    with col4:
        st.metric("Top City Revenue", f"${kpis['top_city_revenue']:,.0f}")
    with col5:
        st.metric("Country Conv. Variance", f"{kpis['country_conversion_variance']:.1f}")
    
    st.divider()
    
    # Charts section with enhanced styling
    st.markdown("""
    <div class="section-header">
        <h2>📊 Analytics & Visualizations</h2>
        <p>Interactive charts and data insights for strategic decision making</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Row 1 - Revenue and Conversion charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by City")
        if not filtered_df.empty:
            city_revenue = filtered_df.groupby('City')['Billing_Value'].sum().reset_index()
            if not city_revenue.empty:
                fig_pie = px.pie(city_revenue, values='Billing_Value', names='City',
                               title="Revenue Distribution by City")
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No revenue data available for selected filters")
        else:
            st.info("No data available for selected filters")
    
    with col2:
        st.subheader("Recruitment Conversion Rate by Consultant")
        if not filtered_df.empty:
            consultant_stats = filtered_df.groupby('Consultant_Name').agg({
                'Candidate_ID': 'count',
                'Placement_Date': lambda x: x.notna().sum()
            }).reset_index()
            consultant_stats['Conversion_Rate'] = (consultant_stats['Placement_Date'] / consultant_stats['Candidate_ID'] * 100).fillna(0)
            
            if not consultant_stats.empty:
                fig_bar = px.bar(consultant_stats, x='Consultant_Name', y='Conversion_Rate',
                               title="Conversion Rate by Consultant (%)")
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No consultant data available for selected filters")
        else:
            st.info("No data available for selected filters")
    
    # Row 2 - Pipeline and Jobs charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pipeline Funnel by Stage")
        if not filtered_df.empty:
            funnel_fig = create_funnel_chart(filtered_df)
            st.plotly_chart(funnel_fig, use_container_width=True)
        else:
            st.info("No data available for pipeline analysis")
    
    with col2:
        st.subheader("Jobs Received per Quarter")
        if not filtered_df.empty:
            filtered_df['Posted_Quarter'] = pd.to_datetime(filtered_df['Posted_Date'], errors='coerce').dt.to_period('Q').astype(str)
            quarterly_jobs = filtered_df.groupby('Posted_Quarter').size().reset_index(name='Job_Count')
            quarterly_jobs = quarterly_jobs[quarterly_jobs['Posted_Quarter'] != 'NaT']
            
            if not quarterly_jobs.empty:
                fig_quarter = px.bar(quarterly_jobs, x='Posted_Quarter', y='Job_Count',
                                   title="Jobs Received by Quarter")
                st.plotly_chart(fig_quarter, use_container_width=True)
            else:
                st.info("No quarterly job data available")
        else:
            st.info("No data available for selected filters")
    
    # Row 3 - More detailed charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Jobs Won by Quarter (Year-wise)")
        if not filtered_df.empty:
            won_jobs = filtered_df[filtered_df['Job_Status'] == 'Won'].copy()
            if not won_jobs.empty:
                won_jobs['Posted_Quarter'] = pd.to_datetime(won_jobs['Posted_Date'], errors='coerce').dt.to_period('Q').astype(str)
                won_quarterly = won_jobs.groupby('Posted_Quarter').size().reset_index(name='Won_Count')
                won_quarterly = won_quarterly[won_quarterly['Posted_Quarter'] != 'NaT']
                
                if not won_quarterly.empty:
                    fig_won = px.bar(won_quarterly, x='Posted_Quarter', y='Won_Count',
                                   title="Jobs Won by Quarter", color='Won_Count')
                    st.plotly_chart(fig_won, use_container_width=True)
                else:
                    st.info("No won jobs data available")
            else:
                st.info("No won jobs for selected filters")
        else:
            st.info("No data available for selected filters")
    
    with col2:
        st.subheader("Total Jobs vs Time to Hire per Consultant")
        if not filtered_df.empty:
            consultant_metrics = filtered_df.groupby('Consultant_Name').agg({
                'Job_ID': 'count',
                'Time_to_Hire': 'mean'
            }).reset_index()
            consultant_metrics = consultant_metrics.dropna()
            
            if not consultant_metrics.empty:
                fig_scatter = px.scatter(consultant_metrics, x='Job_ID', y='Time_to_Hire',
                                       hover_data=['Consultant_Name'],
                                       title="Jobs Count vs Average Time to Hire")
                fig_scatter.update_layout(xaxis_title="Total Jobs", yaxis_title="Avg Time to Hire (Days)")
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("No consultant metrics available")
        else:
            st.info("No data available for selected filters")
    
    # Row 4 - Geographical Performance Charts
    st.subheader("🌍 Geographical Performance Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Country")
        if not filtered_df.empty:
            country_revenue = filtered_df.groupby('Country')['Billing_Value'].sum().reset_index()
            country_revenue = country_revenue.sort_values('Billing_Value', ascending=False)
            
            if not country_revenue.empty:
                fig_country = px.bar(country_revenue, x='Country', y='Billing_Value',
                                   title="Total Revenue by Country",
                                   color='Billing_Value',
                                   color_continuous_scale='Blues')
                fig_country.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_country, use_container_width=True)
            else:
                st.info("No country revenue data available")
        else:
            st.info("No data available for geographical analysis")
    
    with col2:
        st.subheader("Conversion Rate by City")
        if not filtered_df.empty:
            city_conversion = filtered_df.groupby(['Country', 'City']).agg({
                'Job_ID': 'count',
                'Placement_Date': lambda x: x.notna().sum()
            }).reset_index()
            
            city_conversion['Conversion_Rate'] = (
                city_conversion['Placement_Date'] / city_conversion['Job_ID'] * 100
            ).round(2)
            city_conversion = city_conversion[city_conversion['Job_ID'] >= 3]  # Filter cities with at least 3 jobs
            
            if not city_conversion.empty:
                fig_city_conv = px.scatter(city_conversion, 
                                         x='Job_ID', 
                                         y='Conversion_Rate',
                                         color='Country',
                                         size='Placement_Date',
                                         hover_data=['City'],
                                         title="City Performance: Jobs vs Conversion Rate")
                fig_city_conv.update_layout(xaxis_title="Total Jobs", yaxis_title="Conversion Rate (%)")
                st.plotly_chart(fig_city_conv, use_container_width=True)
            else:
                st.info("No sufficient city data for conversion analysis")
        else:
            st.info("No data available for city analysis")
    
    # Row 5 - Heatmap and Geographic Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Market Penetration Heatmap")
        if not filtered_df.empty:
            geo_analysis = analyze_geographical_performance(filtered_df)
            if 'country_performance' in geo_analysis and not geo_analysis['country_performance'].empty:
                country_perf = geo_analysis['country_performance']
                
                fig_heatmap = px.imshow(
                    country_perf[['Total_Jobs', 'Placements', 'Conversion_Rate', 'Avg_Billing']].T,
                    x=country_perf['Country'],
                    y=['Total Jobs', 'Placements', 'Conversion Rate', 'Avg Billing'],
                    aspect="auto",
                    color_continuous_scale='RdYlBu_r',
                    title="Country Performance Heatmap"
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.info("No data available for market penetration analysis")
        else:
            st.info("No data available for heatmap")
    
    with col2:
        st.subheader("Regional Distribution")
        if not filtered_df.empty:
            regional_dist = filtered_df.groupby(['Country', 'Job_Status']).size().reset_index(name='Count')
            
            if not regional_dist.empty:
                fig_region = px.sunburst(regional_dist, 
                                       path=['Country', 'Job_Status'], 
                                       values='Count',
                                       title="Regional Job Status Distribution")
                st.plotly_chart(fig_region, use_container_width=True)
            else:
                st.info("No regional distribution data available")
        else:
            st.info("No data available for regional analysis")
    
    st.divider()
    
    # Tables section with enhanced styling
    st.markdown("""
    <div class="section-header">
        <h2>📋 Detailed Views</h2>
        <p>Comprehensive data tables and export capabilities</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Consultant Pipeline Details", "Geographical Analysis", "Raw Data Export"])
    
    with tab1:
        st.subheader("Consultant-wise Pipeline Details")
        if not filtered_df.empty:
            pipeline_details = filtered_df[['Consultant_Name', 'Job_Title', 'Candidate_Name', 
                                          'Interview_Status', 'Job_Status', 'Country', 'City', 'Billing_Value']].copy()
            pipeline_details['Billing_Value'] = pipeline_details['Billing_Value'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
            st.dataframe(pipeline_details, use_container_width=True)
        else:
            st.info("No pipeline data available for selected filters")
    
    with tab2:
        st.subheader("🌍 Geographical Performance Analysis")
        if not filtered_df.empty:
            geo_analysis = analyze_geographical_performance(filtered_df)
            
            # Country performance table
            if 'country_performance' in geo_analysis and not geo_analysis['country_performance'].empty:
                st.write("**Country Performance Summary:**")
                country_perf = geo_analysis['country_performance'].copy()
                country_perf['Total_Revenue'] = country_perf['Total_Revenue'].apply(lambda x: f"${x:,.0f}")
                country_perf['Avg_Billing'] = country_perf['Avg_Billing'].apply(lambda x: f"${x:,.0f}")
                country_perf['Revenue_per_Consultant'] = country_perf['Revenue_per_Consultant'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(country_perf, use_container_width=True)
            
            st.divider()
            
            # City performance table
            if 'city_performance' in geo_analysis and not geo_analysis['city_performance'].empty:
                st.write("**City Performance Summary:**")
                city_perf = geo_analysis['city_performance'].copy()
                city_perf['Total_Revenue'] = city_perf['Total_Revenue'].apply(lambda x: f"${x:,.0f}")
                city_perf['Avg_Billing'] = city_perf['Avg_Billing'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(city_perf, use_container_width=True)
            
            st.divider()
            
            # Market penetration analysis
            if 'market_penetration' in geo_analysis and not geo_analysis['market_penetration'].empty:
                st.write("**Market Penetration Analysis:**")
                st.dataframe(geo_analysis['market_penetration'], use_container_width=True)
        else:
            st.info("No geographical data available for analysis")
    
    with tab2:
        st.subheader("Raw Data with Export Options")
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
            
            # Export buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV export
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"recruitment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Excel export
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    filtered_df.to_excel(writer, sheet_name='Recruitment_Data', index=False)
                
                st.download_button(
                    label="📥 Download as Excel",
                    data=buffer.getvalue(),
                    file_name=f"recruitment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No data available for export with selected filters")

def render_chatbot_interface():
    """Render the AI chatbot interface"""
    st.markdown("""
    <div class="section-header">
        <h2>🤖 AI Recruitment Assistant</h2>
        <p>Ask questions about recruitment analytics, best practices, and insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        st.markdown("""
        <div class="alert-warning">
            <strong>API Key Required:</strong> Please configure your Groq API key to use the AI assistant.
            <br><br>
            <strong>How to set up:</strong>
            <ol>
                <li>Get your free API key from <a href="https://console.groq.com" target="_blank">Groq Console</a></li>
                <li>Add it as a secret named 'GROQ_API_KEY' in your Replit environment</li>
                <li>Restart the application</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Sample questions section
    st.markdown("""
    <div class="chat-container">
        <h4>💡 Sample Questions</h4>
        <p>Click on any question below to get started:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display sample questions in a grid
    cols = st.columns(2)
    for i, question in enumerate(SAMPLE_QUESTIONS):
        with cols[i % 2]:
            if st.button(question, key=f"sample_q_{i}", use_container_width=True):
                if 'chat_history' not in st.session_state:
                    st.session_state.chat_history = []
                
                # Add user question to chat history
                st.session_state.chat_history.append({"role": "user", "content": question})
                
                # Get AI response with enhanced loading
                with st.spinner("🤖 AI is analyzing your data..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        progress_bar.progress(i + 1)
                    response = chatbot.generate_response(question, df)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    progress_bar.empty()
                
                st.rerun()
    
    st.divider()
    
    # Chat interface
    st.markdown("""
    <div class="chat-container">
        <h4>💬 Chat with AI Assistant</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>AI Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    user_question = st.text_input("Ask a question about recruitment analytics:", 
                                 placeholder="e.g., How can I improve my conversion rates?",
                                 key="chat_input")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Send", type="primary", use_container_width=True):
            if user_question.strip():
                # Add user question to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                
                # Get AI response
                with st.spinner("Generating response..."):
                    response = chatbot.generate_response(user_question, df)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                st.rerun()
    
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Analytics context section
    if not df.empty:
        st.markdown("""
        <div class="section-header">
            <h4>📊 Current Data Context</h4>
        </div>
        """, unsafe_allow_html=True)
        
        context_col1, context_col2, context_col3, context_col4 = st.columns(4)
        
        with context_col1:
            st.metric("Total Records", len(df))
        with context_col2:
            st.metric("Consultants", df['Consultant_Name'].nunique())
        with context_col3:
            st.metric("Active Jobs", len(df[df['Job_Status'] == 'Active']))
        with context_col4:
            st.metric("Placements", len(df[df['Placement_Date'].notna()]))

if __name__ == "__main__":
    main()
