import yaml
import logging
import os

class ConfigLoader:
    """A class to handle configuration loading and logging setup."""

    @staticmethod
    def load_config(file_path):
        """Load a YAML configuration file."""
        try:
            with open(file_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Failed to load config file: {e}")
            raise

# Set the path to the config.yml file
config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yml')

# Load configuration
config = ConfigLoader.load_config(config_path)

# Get log file path from the configuration
log_path = config.get('log_paths', {}).get('log_file', 'default.log')  # Fallback to 'default.log'

# Global logger setup
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
