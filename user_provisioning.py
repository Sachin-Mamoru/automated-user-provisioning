#!/usr/bin/env python3
"""
User Account Creation Script - Enhanced Version

This script automates the creation of user accounts from a CSV file by sending
HTTP POST requests to an API endpoint. It includes comprehensive error handling,
logging, validation, and retry mechanisms.

Author: Support Engineering Team
Version: 2.0
"""

import csv
import requests
import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class UserProvisioningManager:
    """
    A class to manage user provisioning from CSV files with enhanced error handling,
    validation, and logging capabilities.
    """
    
    def __init__(self, api_endpoint: str = "https://jsonplaceholder.typicode.com/users", 
                 log_file: str = "error_log.txt", max_retries: int = 3):
        """
        Initialize the UserProvisioningManager.
        
        Args:
            api_endpoint (str): The API endpoint for user creation
            log_file (str): Path to the error log file
            max_retries (int): Maximum number of retry attempts for failed requests
        """
        self.api_endpoint = api_endpoint
        self.log_file = log_file
        self.max_retries = max_retries
        self.required_fields = ['name', 'email', 'role']
        self.valid_roles = ['admin', 'user', 'moderator', 'guest']
        
        # Setup logging
        self._setup_logging()
        
        # Setup HTTP session with retry strategy
        self.session = self._setup_session()
        
        # Statistics tracking
        self.stats = {
            'total_processed': 0,
            'successful_creations': 0,
            'failed_creations': 0,
            'skipped_rows': 0,
            'validation_failures': 0
        }
    
    def _setup_logging(self) -> None:
        """Setup logging configuration for both file and console output."""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/{self.log_file}'),
                logging.StreamHandler()  # Console output
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Log session start
        self.logger.info("=" * 60)
        self.logger.info("User Provisioning Session Started")
        self.logger.info("=" * 60)
    
    def _setup_session(self) -> requests.Session:
        """Setup HTTP session with retry strategy and timeouts."""
        session = requests.Session()
        
        # Define retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=1
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default timeout and headers
        session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'UserProvisioningScript/2.0'
        })
        
        return session
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format using regex.
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if email is valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email.strip()) is not None
    
    def validate_user_data(self, user_data: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate user data against business rules.
        
        Args:
            user_data (Dict[str, str]): User data dictionary
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for required fields
        for field in self.required_fields:
            if not user_data.get(field, '').strip():
                errors.append(f"Missing required field: {field}")
        
        # Validate email format
        email = user_data.get('email', '').strip()
        if email and not self.validate_email(email):
            errors.append(f"Invalid email format: {email}")
        
        # Validate role
        role = user_data.get('role', '').strip().lower()
        if role and role not in self.valid_roles:
            errors.append(f"Invalid role: {role}. Valid roles are: {', '.join(self.valid_roles)}")
        
        # Check name length
        name = user_data.get('name', '').strip()
        if name and (len(name) < 2 or len(name) > 50):
            errors.append(f"Name length must be between 2 and 50 characters: {name}")
        
        return len(errors) == 0, errors
    
    def create_single_user(self, user_data: Dict[str, str], row_number: int) -> bool:
        """
        Create a single user via API call with comprehensive error handling.
        
        Args:
            user_data (Dict[str, str]): User data dictionary
            row_number (int): Row number in CSV for tracking
            
        Returns:
            bool: True if user creation was successful, False otherwise
        """
        try:
            # Clean and prepare user data
            cleaned_data = {k: v.strip() if isinstance(v, str) else v for k, v in user_data.items()}
            
            # Make API request
            response = self.session.post(
                self.api_endpoint,
                json=cleaned_data,
                timeout=(10, 30)  # (connection_timeout, read_timeout)
            )
            
            # Check response status
            if response.status_code in [200, 201]:
                self.logger.info(f"✅ User created successfully: {cleaned_data.get('email')} (Row {row_number})")
                return True
            else:
                error_msg = f"API returned status {response.status_code}"
                try:
                    error_detail = response.json().get('message', 'No error details provided')
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - Response: {response.text[:200]}"
                
                self.logger.error(f"❌ Failed to create user {cleaned_data.get('email')} (Row {row_number}): {error_msg}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error(f"❌ Timeout creating user {user_data.get('email')} (Row {row_number})")
            return False
        except requests.exceptions.ConnectionError:
            self.logger.error(f"❌ Connection error creating user {user_data.get('email')} (Row {row_number})")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Request failed for user {user_data.get('email')} (Row {row_number}): {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error creating user {user_data.get('email')} (Row {row_number}): {str(e)}")
            return False
    
    def process_csv_file(self, file_path: str) -> Dict[str, int]:
        """
        Process CSV file and create users with comprehensive error handling.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            Dict[str, int]: Statistics about the processing
        """
        if not os.path.exists(file_path):
            self.logger.error(f"❌ CSV file not found: {file_path}")
            return self.stats
        
        self.logger.info(f"📂 Processing CSV file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect if file is empty
                if os.path.getsize(file_path) == 0:
                    self.logger.error("❌ CSV file is empty")
                    return self.stats
                
                reader = csv.DictReader(file)
                
                # Validate CSV headers
                if not reader.fieldnames:
                    self.logger.error("❌ CSV file has no headers")
                    return self.stats
                
                missing_headers = [field for field in self.required_fields if field not in reader.fieldnames]
                if missing_headers:
                    self.logger.error(f"❌ Missing required headers in CSV: {missing_headers}")
                    return self.stats
                
                self.logger.info(f"📋 CSV headers found: {list(reader.fieldnames)}")
                
                # Process each row
                for row_number, row in enumerate(reader, start=2):  # Start at 2 because row 1 is headers
                    self.stats['total_processed'] += 1
                    
                    # Skip empty rows
                    if all(not str(value).strip() for value in row.values()):
                        self.logger.warning(f"⚠️  Skipping empty row {row_number}")
                        self.stats['skipped_rows'] += 1
                        continue
                    
                    # Validate user data
                    is_valid, validation_errors = self.validate_user_data(row)
                    
                    if not is_valid:
                        self.logger.warning(f"⚠️  Validation failed for row {row_number}: {'; '.join(validation_errors)}")
                        self.logger.warning(f"    Row data: {dict(row)}")
                        self.stats['validation_failures'] += 1
                        self.stats['skipped_rows'] += 1
                        continue
                    
                    # Attempt to create user
                    if self.create_single_user(row, row_number):
                        self.stats['successful_creations'] += 1
                    else:
                        self.stats['failed_creations'] += 1
                    
                    # Add small delay to avoid overwhelming the API
                    time.sleep(0.1)
        
        except FileNotFoundError:
            self.logger.error(f"❌ File not found: {file_path}")
        except csv.Error as e:
            self.logger.error(f"❌ CSV parsing error: {str(e)}")
        except UnicodeDecodeError as e:
            self.logger.error(f"❌ File encoding error: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error processing file: {str(e)}")
        
        return self.stats
    
    def print_summary(self) -> None:
        """Print a comprehensive summary of the processing results."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PROCESSING SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"📊 Total rows processed: {self.stats['total_processed']}")
        self.logger.info(f"✅ Successful creations: {self.stats['successful_creations']}")
        self.logger.info(f"❌ Failed creations: {self.stats['failed_creations']}")
        self.logger.info(f"⚠️  Skipped rows: {self.stats['skipped_rows']}")
        self.logger.info(f"🔍 Validation failures: {self.stats['validation_failures']}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['successful_creations'] / self.stats['total_processed']) * 100
            self.logger.info(f"📈 Success rate: {success_rate:.1f}%")
        
        self.logger.info("=" * 60)
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        if hasattr(self, 'session'):
            self.session.close()


def main():
    """
    Main function to run the user provisioning script.
    
    This function can be easily modified to accept command-line arguments
    or configuration files in the future.
    """
    # Configuration - can be moved to a config file or command-line args
    CSV_FILE_PATH = "users.csv"
    API_ENDPOINT = "https://jsonplaceholder.typicode.com/users"  # Using a mock API for testing
    
    # Create and run the provisioning manager
    provisioner = UserProvisioningManager(
        api_endpoint=API_ENDPOINT,
        log_file="error_log.txt"
    )
    
    try:
        # Process the CSV file
        stats = provisioner.process_csv_file(CSV_FILE_PATH)
        
        # Print summary
        provisioner.print_summary()
        
        # Exit with appropriate code
        if stats['failed_creations'] > 0:
            exit(1)  # Non-zero exit code for failures
        else:
            exit(0)  # Success
            
    except KeyboardInterrupt:
        provisioner.logger.info("❌ Script interrupted by user")
        exit(130)
    except Exception as e:
        provisioner.logger.error(f"❌ Fatal error: {str(e)}")
        exit(1)
    finally:
        provisioner.cleanup()


if __name__ == "__main__":
    main()
