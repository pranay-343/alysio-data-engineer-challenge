import pandas as pd
import json
import re
import numpy as np
from datetime import datetime
import sqlite3
import os
from config_loader  import ConfigLoader, logger


class DataCleaner:
    
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yml')
        config = ConfigLoader.load_config(config_path)
        file_paths = config['database_path']
        self.db_name = file_paths['database_name']
        
    def clean_companies(self):
        """Clean company data
            * Remove leading/trailing whitespace and standardize casing
            * Check for missing values in critical fields
            * Ensure annual revenue is non-negative
        """
        try:
            self.companies['name'] = self.companies['name'].str.strip().str.title()
            self.companies['industry'] = self.companies['industry'].str.strip().str.title()
            self.companies.dropna(subset=['id', 'name'], inplace=True)
            self.companies = self.companies[self.companies['annual_revenue'] >= 0]
            
        except Exception as e:
            logger.error("Error cleaning companies data: %s", e)
            raise

    @staticmethod
    def clean_email(email):
        """Clean and validate email address"""
        return email.lower().strip()

    @staticmethod
    def clean_phone(phone):
        """Clean and format phone numbers"""
        try:
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 11:
                return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            return None
        except Exception as e:
            logger.error("Error cleaning phone number: %s", e)
            return None

    def clean_contacts(self):
        """Clean contacts data and maintain relationships
            * Normalize email addresses
            * Remove duplicates based on email
            * Clean phone numbers
            * Check for missing values in critical fields
            * Ensure titles are standardized
            * Maintain relationship integrity
        """
        try:
            self.contacts['email'] = self.contacts['email'].apply(self.clean_email)
            self.contacts.drop_duplicates(subset='email', keep='first', inplace=True)
            self.contacts['phone'] = self.contacts['phone'].apply(self.clean_phone)
            self.contacts.dropna(subset=['id', 'email'], inplace=True)
            self.contacts['title'] = self.contacts['title'].str.strip().str.title()
            self.contacts.set_index('id', inplace=True)
            contact_mapping = self.contacts[['email']].reset_index().set_index('email')
            self.opportunities['contact_id'] = self.opportunities['contact_id'].map(
                contact_mapping['id']
            ).fillna(self.opportunities['contact_id'])
            self.activities['contact_id'] = self.activities['contact_id'].map(
                contact_mapping['id']
            ).fillna(self.activities['contact_id'])
            self.contacts = self.contacts.reset_index()
            
        except Exception as e:
            logger.error("Error cleaning contacts data: %s", e)
            raise

    def clean_opportunities(self):
        """Clean opportunities data
            * Check for non-negative amounts
            * Validate date formats
            * Drop rows with invalid dates
            * Ensure close_date is after created_date
        """
        try:
            self.opportunities = self.opportunities[self.opportunities['amount'] >= 0]
            self.opportunities['created_date'] = pd.to_datetime(
                self.opportunities['created_date'], 
                errors='coerce'
            )
            self.opportunities['close_date'] = pd.to_datetime(
                self.opportunities['close_date'], 
                errors='coerce'
            )
            self.opportunities.dropna(
                subset=['created_date', 'close_date'], 
                inplace=True
            )
            self.opportunities = self.opportunities[
                self.opportunities['close_date'] > self.opportunities['created_date']
            ]
            
        except Exception as e:
            logger.error("Error cleaning opportunities data: %s", e)
            raise

    def clean_activities(self):
        """Clean activities data
            * Validate timestamps 
        """
        try:
            self.activities['timestamp'] = pd.to_datetime(
                self.activities['timestamp'], 
                errors='coerce'
            )
            self.activities.dropna(subset=['timestamp'], inplace=True)
            
        except Exception as e:
            logger.error("Error cleaning activities data: %s", e)
            raise

    def extract_from_file(self, file_path):
        """Extract data from file and return as DataFrame"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            if file_extension == ".csv":
                return pd.read_csv(file_path)
            elif file_extension == ".json":
                with open(file_path, "r") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    return pd.DataFrame([data])
                else:
                    raise ValueError("Unsupported JSON structure")
            else:
                raise ValueError("Unsupported file type. Only CSV and JSON are supported.")
        except Exception as e:
            logger.error("Extract failed: %s", e)
            raise e

    def save_to_sqlite(self):
        """Save cleaned data to SQLite database
            * Save all cleaned DataFrames to SQLite
        """
        try:
            conn = sqlite3.connect(self.db_name)
            self.companies.to_sql('Companies', conn, if_exists='replace', index=False)
            self.contacts.to_sql('Contacts', conn, if_exists='replace', index=False)
            self.opportunities.to_sql('Opportunities', conn, if_exists='replace', index=False)
            self.activities.to_sql('Activities', conn, if_exists='replace', index=False)
            conn.commit()
            conn.close()
            logger.info("Successfully saved all data to SQLite database")
            
        except Exception as e:
            logger.error("Failed to save data to SQLite: %s", e)
            raise

  