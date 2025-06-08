import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io
import warnings
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

# Load data
df, is_sample_data = load_data()

# Main dashboard
def main():
    # Header
    st.title("🎯 Recruitment Analytics Dashboard")
    if is_sample_data:
        st.caption("*Currently displaying sample data for demonstration*")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
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

if __name__ == "__main__":
    main()
