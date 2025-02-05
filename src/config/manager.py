import os
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv, set_key
from getpass import getpass
import re
from src.utils.logger import logger
import argparse

# TODO: Encrypted secrets, use keyring or other secure storage
class ConfigManager:
    """Manages application configuration and settings."""
    
    CONFIG_SCHEMA = {
        'EMAIL_HOST': {
            'prompt': 'Enter your email IMAP server (e.g., imap.gmail.com):',
            'default': 'imap.gmail.com',
            'validator': lambda x: bool(x.strip()),
            'is_secret': False
        },
        'EMAIL_USERNAME': {
            'prompt': 'Enter your email address:',
            'validator': lambda x: re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', x),
            'is_secret': False
        },
        'EMAIL_PASSWORD': {
            'prompt': 'Enter your email app-specific password:',
            # 'validator': lambda x: len(x) >= 8,
            'is_secret': True
        },
        'TODOIST_API_KEY': {
            'prompt': 'Enter your Todoist API key:',
            # 'validator': lambda x: len(x) >= 8,
            'is_secret': True
        },
        'SCAN_TIME': {
            'prompt': 'Enter the daily scan time (24-hour format, e.g., 09:00):',
            'default': '09:00',
            'validator': lambda x: re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', x),
            'is_secret': False
        }
    }

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent
        self.env_file = self.root_dir / '.env'
        self.config_file = self.root_dir / 'config.json'
        self.load_env()

    def load_env(self):
        """Load environment variables from .env file"""
        load_dotenv()

    def save_to_env(self, key: str, value: str):
        """Save a key-value pair to .env file"""
        set_key(self.env_file, key, value)
        os.environ[key] = value

    def save_to_config(self, settings: Dict[str, Any]):
        """Save non-sensitive settings to config file"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(settings, f, indent=4)

    def load_config(self) -> Dict[str, Any]:
        """Load settings from config file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def is_configured(self) -> bool:
        """Check if all required configuration is present"""
        return all(os.getenv(key) for key in self.CONFIG_SCHEMA.keys())

    def validate_setting(self, key: str, value: str) -> bool:
        """Validate a single setting"""
        if key not in self.CONFIG_SCHEMA:
            return False
        return self.CONFIG_SCHEMA[key]['validator'](value)

    def update_setting(self, key: str, value: str) -> bool:
        """Update a single setting"""
        if not self.validate_setting(key, value):
            return False
        
        if self.CONFIG_SCHEMA[key]['is_secret']:
            self.save_to_env(key, value)
        else:
            config = self.load_config()
            config[key] = value
            self.save_to_config(config)
            self.save_to_env(key, value)
        return True

    def initial_setup(self):
        """Run initial configuration setup"""
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
        """Print current configuration (hiding secrets)"""
        print("\nCurrent Configuration:")
        print("----------------------")
        for key in self.CONFIG_SCHEMA.keys():
            value = os.getenv(key, '')
            if self.CONFIG_SCHEMA[key]['is_secret']:
                value = '*' * 8 if value else 'Not set'
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