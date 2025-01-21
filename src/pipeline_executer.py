from config_loader  import ConfigLoader, logger
from data_cleaning import DataCleaner
import os
def execute_pipeline(data_clean_obj, config):
    """Execute the complete ETL pipeline.
        * Load data paths from configuration 
        * Clean all datasets
        * Save to SQLite
        """
    try:
        logger.info("Starting the ETL pipeline.")
        file_paths = config['file_paths']
        data_clean_obj.companies = data_clean_obj.extract_from_file(file_paths['companies_data'])
        data_clean_obj.contacts = data_clean_obj.extract_from_file(file_paths['contacts_data'])
        data_clean_obj.opportunities = data_clean_obj.extract_from_file(file_paths['opportunities_data'])
        data_clean_obj.activities = data_clean_obj.extract_from_file(file_paths['activities_data'])

        logger.info("Cleaning datasets.")
        data_clean_obj.clean_companies()
        data_clean_obj.clean_contacts()
        data_clean_obj.clean_opportunities()
        data_clean_obj.clean_activities()

        logger.info("Saving cleaned data to SQLite.")
        data_clean_obj.save_to_sqlite()
        
        logger.info("Data cleaning pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    """Main script execution
        * Load configuration
        * Initialize data cleaner object
        * Execute the pipeline
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yml')
        config = ConfigLoader.load_config(config_path)
        data_clean_obj = DataCleaner()
        execute_pipeline(data_clean_obj, config)
    except Exception as e:
        logger.critical(f"Critical error: {e}")
