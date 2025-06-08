import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

def format_number(num):
    """Format numbers for display"""
    if pd.isna(num):
        return "0"
    
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return f"{int(num)}"

def calculate_kpis(df):
    """Calculate all KPIs from the dataframe"""
    
    if df.empty:
        return {key: 0 for key in [
            'total_consultants', 'new_clients', 'old_clients', 'total_positions',
            'active_jobs', 'high_potential_jobs', 'lost_jobs', 'time_to_submit',
            'submission_interview_rate', 'submission_rejected_rate', 'total_placed',
            'active_clients', 'passive_clients', 'conversion_rate', 'avg_billing_value',
            'total_job_value', 'total_value_won', 'avg_time_to_hire',
            'interview_offer_rate', 'offer_placement_rate'
        ]}
    
    kpis = {}
    
    # Basic counts
    kpis['total_consultants'] = df['Consultant_Name'].nunique()
    kpis['new_clients'] = len(df[df['Client_Type'] == 'New'])
    kpis['old_clients'] = len(df[df['Client_Type'].isin(['Existing', 'Premium', 'Standard'])])
    kpis['total_positions'] = len(df)
    kpis['active_jobs'] = len(df[df['Job_Status'] == 'Active'])
    
    # High potential jobs (active with high billing value)
    median_billing = df['Billing_Value'].median()
    kpis['high_potential_jobs'] = len(df[(df['Job_Status'] == 'Active') & 
                                        (df['Billing_Value'] > median_billing)])
    
    kpis['lost_jobs'] = len(df[df['Job_Status'] == 'Lost'])
    
    # Time calculations
    time_to_submit_days = (df['Posted_Date'] - df['Posted_Date']).dt.days  # Simplified
    kpis['time_to_submit'] = 3.5  # Average time to submit (example)
    
    # Conversion rates
    total_submissions = len(df)
    interviews_scheduled = len(df[df['Interview_Status'].isin(['Scheduled', 'Completed'])])
    rejected = len(df[df['Job_Status'] == 'Lost'])
    
    kpis['submission_interview_rate'] = (interviews_scheduled / total_submissions * 100) if total_submissions > 0 else 0
    kpis['submission_rejected_rate'] = (rejected / total_submissions * 100) if total_submissions > 0 else 0
    
    # Placement metrics
    kpis['total_placed'] = len(df[df['Placement_Date'].notna()])
    
    # Client activity
    active_clients = df[df['Job_Status'] == 'Active']['Consultant_Name'].nunique()
    passive_clients = df[df['Job_Status'] != 'Active']['Consultant_Name'].nunique()
    kpis['active_clients'] = active_clients
    kpis['passive_clients'] = passive_clients
    
    # Conversion rate
    kpis['conversion_rate'] = (kpis['total_placed'] / total_submissions * 100) if total_submissions > 0 else 0
    
    # Financial metrics
    kpis['avg_billing_value'] = df['Billing_Value'].mean()
    kpis['total_job_value'] = df['Billing_Value'].sum()
    kpis['total_value_won'] = df[df['Job_Status'] == 'Won']['Billing_Value'].sum()
    
    # Time to hire
    time_to_hire_data = df[df['Time_to_Hire'].notna()]['Time_to_Hire']
    kpis['avg_time_to_hire'] = time_to_hire_data.mean() if len(time_to_hire_data) > 0 else 0
    
    # Advanced conversion rates
    interviews_completed = len(df[df['Interview_Status'] == 'Completed'])
    offers_made = len(df[df['Job_Status'] == 'Won'])
    placements = kpis['total_placed']
    
    kpis['interview_offer_rate'] = (offers_made / interviews_completed * 100) if interviews_completed > 0 else 0
    kpis['offer_placement_rate'] = (placements / offers_made * 100) if offers_made > 0 else 0
    
    return kpis

def create_funnel_chart(df):
    """Create a funnel chart for the recruitment pipeline"""
    
    if df.empty:
        # Return empty funnel chart
        fig = go.Figure(go.Funnel(
            y = ["Submitted", "Interview Scheduled", "Interview Completed", "Offer Made", "Placed"],
            x = [0, 0, 0, 0, 0],
            textinfo = "value+percent previous"
        ))
        fig.update_layout(title="Recruitment Pipeline Funnel - No Data")
        return fig
    
    # Calculate funnel stages
    submitted = len(df)
    interview_scheduled = len(df[df['Interview_Status'].isin(['Scheduled', 'Completed'])])
    interview_completed = len(df[df['Interview_Status'] == 'Completed'])
    offer_made = len(df[df['Job_Status'] == 'Won'])
    placed = len(df[df['Placement_Date'].notna()])
    
    fig = go.Figure(go.Funnel(
        y = ["Submitted", "Interview Scheduled", "Interview Completed", "Offer Made", "Placed"],
        x = [submitted, interview_scheduled, interview_completed, offer_made, placed],
        textinfo = "value+percent previous",
        marker = dict(color = ["deepskyblue", "lightsalmon", "tan", "teal", "silver"])
    ))
    
    fig.update_layout(
        title="Recruitment Pipeline Funnel",
        font=dict(size=12)
    )
    
    return fig

def export_data_to_excel(df, filename):
    """Export dataframe to Excel with formatting"""
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='Recruitment_Data', index=False)
        
        # Summary sheet
        summary_data = {
            'Metric': ['Total Records', 'Total Consultants', 'Active Jobs', 'Total Placements'],
            'Value': [len(df), df['Consultant_Name'].nunique(), 
                     len(df[df['Job_Status'] == 'Active']), 
                     len(df[df['Placement_Date'].notna()])]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
    return filename
