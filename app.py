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
from utils import format_number, calculate_kpis, create_funnel_chart

# Page configuration
st.set_page_config(
    page_title="Recruitment Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional styling
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .dashboard-header {
        background: linear-gradient(90deg, #1B365D 0%, #4A90E2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .section-header {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4A90E2;
        margin: 1rem 0;
    }
    
    .filter-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    .sample-question {
        background: #f0f8ff;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        cursor: pointer;
        border: 1px solid #4A90E2;
        color: #1B365D;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    
    .sample-question:hover {
        background: #4A90E2;
        color: white;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .bot-message {
        background: #f1f8e9;
        border-left: 4px solid #4caf50;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .alert-warning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }
    
    .alert-success {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
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
            job_status_dist = context_data['Job_Status'].value_counts()
            client_type_dist = context_data['Client_Type'].value_counts()
            
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
    "What are the conversion rate trends across different cities?",
    "Which client types generate the highest billing values?",
    "Identify bottlenecks in our recruitment pipeline",
    "Compare interview completion rates by consultant",
    "What's the correlation between job status and billing values?",
    "Analyze seasonal trends in job placements",
    "Which consultants need performance improvement support?",
    "What are the most profitable job categories?",
    "Predict which active jobs are likely to convert based on patterns",
    "Analyze time-to-hire patterns across different regions",
    "What factors contribute to job losses and how to prevent them?"
]

# Load data
df, is_sample_data = load_data()

# Main dashboard
def main():
    # Professional Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🎯 Recruitment Analytics Dashboard</h1>
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
    # Sidebar filters with professional styling
    with st.sidebar:
        st.markdown("""
        <div class="filter-container">
            <h3>🔍 Analytics Filters</h3>
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
    
    # Display KPIs in cards
    st.header("📈 Key Performance Indicators")
    
    # Row 1 - Basic metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Consultants", format_number(kpis['total_consultants']))
    with col2:
        st.metric("New Clients", format_number(kpis['new_clients']))
    with col3:
        st.metric("Old Clients", format_number(kpis['old_clients']))
    with col4:
        st.metric("Total Positions", format_number(kpis['total_positions']))
    with col5:
        st.metric("Active Jobs", format_number(kpis['active_jobs']))
    
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
    
    st.divider()
    
    # Charts section
    st.header("📊 Analytics & Visualizations")
    
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
    
    st.divider()
    
    # Tables section
    st.header("📋 Detailed Views")
    
    tab1, tab2 = st.tabs(["Consultant Pipeline Details", "Raw Data Export"])
    
    with tab1:
        st.subheader("Consultant-wise Pipeline Details")
        if not filtered_df.empty:
            pipeline_details = filtered_df[['Consultant_Name', 'Job_Title', 'Candidate_Name', 
                                          'Interview_Status', 'Job_Status', 'City', 'Billing_Value']].copy()
            pipeline_details['Billing_Value'] = pipeline_details['Billing_Value'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
            st.dataframe(pipeline_details, use_container_width=True)
        else:
            st.info("No pipeline data available for selected filters")
    
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
                
                # Get AI response
                with st.spinner("Thinking..."):
                    response = chatbot.generate_response(question, df)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
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
