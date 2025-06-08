import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class DataProcessor:
    """Process recruitment data from Excel files"""
    
    def __init__(self):
        self.required_columns = [
            'Consultant_Name', 'Job_Title', 'Candidate_Name', 'Country', 'City',
            'Job_Status', 'Interview_Status', 'Posted_Date', 'Placement_Date',
            'Billing_Value', 'Client_Type', 'Job_ID', 'Candidate_ID'
        ]
    
    def load_excel_data(self, file_path):
        """Load and process Excel data"""
        try:
            # Try to read the Excel file
            df = pd.read_excel(file_path)
            
            # Process and clean the data
            df = self._clean_and_standardize_data(df)
            
            return df
            
        except FileNotFoundError:
            raise Exception(f"Excel file '{file_path}' not found")
        except Exception as e:
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def _clean_and_standardize_data(self, df):
        """Clean and standardize the dataframe"""
        
        # Map common column variations to standard names
        column_mapping = {
            'consultant': 'Consultant_Name',
            'job_title': 'Job_Title',
            'candidate': 'Candidate_Name',
            'candidate_name': 'Candidate_Name',
            'country': 'Country',
            'city': 'City',
            'status': 'Job_Status',
            'job_status': 'Job_Status',
            'interview_status': 'Interview_Status',
            'posted_date': 'Posted_Date',
            'placement_date': 'Placement_Date',
            'billing_value': 'Billing_Value',
            'client_type': 'Client_Type',
            'job_id': 'Job_ID',
            'candidate_id': 'Candidate_ID'
        }
        
        # Rename columns to match standard names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        df = df.rename(columns=column_mapping)
        
        # Add missing columns with default values
        for col in self.required_columns:
            if col not in df.columns:
                if col in ['Posted_Date', 'Placement_Date']:
                    df[col] = pd.NaT
                elif col in ['Billing_Value']:
                    df[col] = 0.0
                elif col in ['Job_ID', 'Candidate_ID']:
                    df[col] = range(1, len(df) + 1)
                else:
                    df[col] = 'Unknown'
        
        # Clean data types
        df['Posted_Date'] = pd.to_datetime(df['Posted_Date'], errors='coerce')
        df['Placement_Date'] = pd.to_datetime(df['Placement_Date'], errors='coerce')
        df['Billing_Value'] = pd.to_numeric(df['Billing_Value'], errors='coerce').fillna(0)
        
        # Calculate additional fields
        df = self._calculate_derived_fields(df)
        
        return df
    
    def _calculate_derived_fields(self, df):
        """Calculate derived fields for analysis"""
        
        # Time to hire calculation
        df['Time_to_Hire'] = (df['Placement_Date'] - df['Posted_Date']).dt.days
        
        # Client categorization
        df['Client_Type'] = df['Client_Type'].fillna('Unknown')
        
        # Job status standardization
        status_mapping = {
            'active': 'Active',
            'won': 'Won',
            'lost': 'Lost',
            'on_hold': 'On Hold',
            'closed': 'Closed'
        }
        df['Job_Status'] = df['Job_Status'].str.lower().map(status_mapping).fillna(df['Job_Status'])
        
        # Interview status standardization
        interview_mapping = {
            'scheduled': 'Scheduled',
            'completed': 'Completed',
            'pending': 'Pending',
            'cancelled': 'Cancelled',
            'no_show': 'No Show'
        }
        df['Interview_Status'] = df['Interview_Status'].str.lower().map(interview_mapping).fillna(df['Interview_Status'])
        
        return df
