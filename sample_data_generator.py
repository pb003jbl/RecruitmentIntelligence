import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class SampleDataGenerator:
    """Generate realistic sample recruitment data for demonstration"""
    
    def __init__(self):
        self.consultants = ['Sarah Johnson', 'Michael Chen', 'Emily Rodriguez', 'David Kim', 'Lisa Thompson', 
                           'James Wilson', 'Maria Garcia', 'Robert Taylor', 'Jennifer Lee', 'Andrew Davis']
        
        self.countries = ['USA', 'Canada', 'UK', 'Germany', 'Australia', 'Singapore', 'UAE']
        
        self.cities = {
            'USA': ['New York', 'San Francisco', 'Chicago', 'Austin', 'Seattle'],
            'Canada': ['Toronto', 'Vancouver', 'Montreal'],
            'UK': ['London', 'Manchester', 'Edinburgh'],
            'Germany': ['Berlin', 'Munich', 'Frankfurt'],
            'Australia': ['Sydney', 'Melbourne', 'Brisbane'],
            'Singapore': ['Singapore'],
            'UAE': ['Dubai', 'Abu Dhabi']
        }
        
        self.job_titles = [
            'Software Engineer', 'Senior Developer', 'Product Manager', 'Data Scientist',
            'DevOps Engineer', 'UX Designer', 'Sales Manager', 'Marketing Director',
            'Business Analyst', 'Project Manager', 'Quality Assurance Engineer',
            'Full Stack Developer', 'Machine Learning Engineer', 'Cloud Architect',
            'Cybersecurity Specialist', 'Technical Lead', 'Scrum Master', 'HR Manager'
        ]
        
        self.job_statuses = ['Active', 'Won', 'Lost', 'On Hold', 'Closed']
        self.interview_statuses = ['Scheduled', 'Completed', 'Pending', 'Cancelled', 'No Show']
        self.client_types = ['New', 'Existing', 'Premium', 'Standard']
        
        self.first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa',
                           'James', 'Maria', 'William', 'Jennifer', 'Richard', 'Linda', 'Thomas',
                           'Elizabeth', 'Christopher', 'Patricia', 'Daniel', 'Barbara']
        
        self.last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
                          'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
                          'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
    
    def generate_comprehensive_data(self, num_records=500):
        """Generate comprehensive recruitment data"""
        
        data = []
        
        for i in range(num_records):
            # Basic information
            consultant = random.choice(self.consultants)
            country = random.choice(self.countries)
            city = random.choice(self.cities[country])
            job_title = random.choice(self.job_titles)
            job_status = random.choice(self.job_statuses)
            interview_status = random.choice(self.interview_statuses)
            client_type = random.choice(self.client_types)
            
            # Generate candidate name
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            candidate_name = f"{first_name} {last_name}"
            
            # Generate dates
            posted_date = self._generate_random_date(days_back=365)
            
            # Placement date logic - only some candidates get placed
            placement_date = None
            if job_status == 'Won' and random.random() < 0.7:  # 70% of won jobs have placements
                placement_date = posted_date + timedelta(days=random.randint(15, 90))
            elif random.random() < 0.3:  # 30% chance of placement for other statuses
                placement_date = posted_date + timedelta(days=random.randint(20, 120))
            
            # Billing value - varies by job level and location
            base_billing = self._calculate_billing_value(job_title, country, city)
            billing_value = base_billing * random.uniform(0.8, 1.3)  # Add some variation
            
            # Time to hire calculation
            time_to_hire = None
            if placement_date:
                time_to_hire = (placement_date - posted_date).days
            
            record = {
                'Job_ID': f"JOB-{1000 + i}",
                'Candidate_ID': f"CAND-{2000 + i}",
                'Consultant_Name': consultant,
                'Job_Title': job_title,
                'Candidate_Name': candidate_name,
                'Country': country,
                'City': city,
                'Job_Status': job_status,
                'Interview_Status': interview_status,
                'Posted_Date': posted_date,
                'Placement_Date': placement_date,
                'Billing_Value': billing_value,
                'Client_Type': client_type,
                'Time_to_Hire': time_to_hire
            }
            
            data.append(record)
        
        df = pd.DataFrame(data)
        
        # Add some additional calculated fields
        df = self._add_calculated_fields(df)
        
        return df
    
    def _generate_random_date(self, days_back=365):
        """Generate a random date within the specified range"""
        start_date = datetime.now() - timedelta(days=days_back)
        random_days = random.randint(0, days_back)
        return start_date + timedelta(days=random_days)
    
    def _calculate_billing_value(self, job_title, country, city):
        """Calculate realistic billing values based on role and location"""
        
        # Base values by job title
        title_values = {
            'Software Engineer': 80000,
            'Senior Developer': 120000,
            'Product Manager': 130000,
            'Data Scientist': 110000,
            'DevOps Engineer': 105000,
            'UX Designer': 85000,
            'Sales Manager': 95000,
            'Marketing Director': 140000,
            'Business Analyst': 75000,
            'Project Manager': 90000,
            'Quality Assurance Engineer': 70000,
            'Full Stack Developer': 100000,
            'Machine Learning Engineer': 125000,
            'Cloud Architect': 135000,
            'Cybersecurity Specialist': 115000,
            'Technical Lead': 130000,
            'Scrum Master': 95000,
            'HR Manager': 85000
        }
        
        # Location multipliers
        country_multipliers = {
            'USA': 1.2,
            'Canada': 1.0,
            'UK': 1.1,
            'Germany': 1.05,
            'Australia': 1.15,
            'Singapore': 1.3,
            'UAE': 1.25
        }
        
        base_value = title_values.get(job_title, 80000)
        country_multiplier = country_multipliers.get(country, 1.0)
        
        return base_value * country_multiplier
    
    def _add_calculated_fields(self, df):
        """Add additional calculated fields"""
        
        # Add submission and offer stages for funnel analysis
        df['Submitted'] = True  # All records are submitted
        df['Interview_Scheduled'] = df['Interview_Status'].isin(['Scheduled', 'Completed'])
        df['Offer_Made'] = (df['Job_Status'] == 'Won') | (df['Placement_Date'].notna())
        df['Placed'] = df['Placement_Date'].notna()
        
        # Add quarterly information
        df['Posted_Quarter'] = df['Posted_Date'].dt.to_period('Q').astype(str)
        df['Posted_Year'] = df['Posted_Date'].dt.year
        
        return df
