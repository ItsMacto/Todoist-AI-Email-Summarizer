import os
import json
from pathlib import Path
from typing import Dict, Any
from getpass import getpass
import re
import argparse
from src.utils.logger import logger

class ConfigManager:
    """Manages application configuration and settings using a JSON config file."""
    
    # Only include keys that the application actually needs.
    CONFIG_SCHEMA = {
        'TODOIST_API_KEY': {
            'prompt': 'Enter your Todoist API key:',
            'validator': lambda x: len(x.strip()) > 0,
            'is_secret': True
        },
        'SCAN_TIME': {
            'prompt': 'Enter the daily scan time (24-hour format, e.g., 09:00):',
            'default': '09:00',
            'validator': lambda x: re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', x),
            'is_secret': False
        },
        'GMAIL_CREDENTIALS_PATH': {
            'prompt': 'Enter the path to your Gmail API credentials file:',
            'default': 'credentials.json',
            'validator': lambda x: len(x.strip()) > 0,
            'is_secret': False
        },
        'GMAIL_TOKEN_PATH': {
            'prompt': 'Enter the path for storing your Gmail OAuth token:',
            'default': 'token.json',
            'validator': lambda x: len(x.strip()) > 0,
            'is_secret': False
        },
        'EXCLUDE_READ': {
            'prompt': 'Exclude read emails? (yes/no):',
            'default': 'yes',
            'validator': lambda x: x.strip().lower() in ['yes', 'no'],
            'is_secret': False
        },
        'EXCLUDE_SPAM': {
            'prompt': 'Exclude spam emails? (yes/no):',
            'default': 'yes',
            'validator': lambda x: x.strip().lower() in ['yes', 'no'],
            'is_secret': False
        },
        'EXCLUDE_PROMOTIONAL': {
            'prompt': 'Exclude promotional emails? (yes/no):',
            'default': 'yes',
            'validator': lambda x: x.strip().lower() in ['yes', 'no'],
            'is_secret': False
        }
    }
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent
        self.config_file = self.root_dir / 'config.json'
    
    def save_to_config(self, settings: Dict[str, Any]):
        """Save settings to the config file."""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(settings, f, indent=4)
    
    def load_config(self) -> Dict[str, Any]:
        """Load settings from the config file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def is_configured(self) -> bool:
        """Check if all required configuration keys are present in the config file."""
        config = self.load_config()
        for key in self.CONFIG_SCHEMA.keys():
            if key not in config or not config[key]:
                return False
        return True
    
    def validate_setting(self, key: str, value: str) -> bool:
        """Validate a single setting."""
        if key not in self.CONFIG_SCHEMA:
            return False
        return self.CONFIG_SCHEMA[key]['validator'](value)
    
    def update_setting(self, key: str, value: str) -> bool:
        """Update a single setting in the config file."""
        if not self.validate_setting(key, value):
            return False
        config = self.load_config()
        config[key] = value
        self.save_to_config(config)
        return True
    
    def initial_setup(self):
        """Run the initial configuration setup interactively."""
        print("Welcome to Email Summary Manager initial setup!")
        print("Please provide the following information:")
        print("----------------------------------------")
    
        for key, settings in self.CONFIG_SCHEMA.items():
            while True:
                if settings.get('is_secret', False):
                    value = getpass(f"{settings['prompt']} ")
                else:
                    default = settings.get('default', '')
                    default_prompt = f" [{default}]" if default else ""
                    value = input(f"{settings['prompt']}{default_prompt} ").strip()
                    if not value and default:
                        value = default
    
                if self.validate_setting(key, value):
                    self.update_setting(key, value)
                    break
                else:
                    print(f"Invalid input for {key}. Please try again.")
    
        print("\nConfiguration completed successfully!")
    
    def print_current_config(self):
        """Print current configuration."""
        print("\nCurrent Configuration:")
        print("----------------------")
        config = self.load_config()
        for key in self.CONFIG_SCHEMA.keys():
            value = config.get(key, '')
            print(f"{key}: {value}")
    
    def setup_cli(self):
        """Handle CLI configuration commands."""
        parser = argparse.ArgumentParser(description='Email Summary Manager Configuration')
        parser.add_argument('--init', action='store_true', help='Run initial setup')
        parser.add_argument('--update', nargs=2, metavar=('KEY', 'VALUE'), help='Update a specific setting')
        parser.add_argument('--show', action='store_true', help='Show current configuration')
    
        args = parser.parse_args()
    
        if args.init:
            self.initial_setup()
        elif args.update:
            key, value = args.update
            if self.update_setting(key, value):
                logger.info(f"Successfully updated {key}")
            else:
                logger.error(f"Failed to update {key}")
        elif args.show:
            self.print_current_config()
        else:
            parser.print_help()