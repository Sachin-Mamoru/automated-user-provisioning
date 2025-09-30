#!/usr/bin/env python3
"""
Test script for the User Provisioning Manager

This script contains unit tests to validate the functionality of the
user provisioning system.
"""

import unittest
import tempfile
import os
import csv
import json
from unittest.mock import Mock, patch, MagicMock
from user_provisioning import UserProvisioningManager


class TestUserProvisioningManager(unittest.TestCase):
    """Test cases for UserProvisioningManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.manager = UserProvisioningManager(
            api_endpoint="https://test-api.com/users",
            log_file="test_log.txt"
        )
    
    def tearDown(self):
        """Clean up after each test method."""
        self.manager.cleanup()
        # Clean up test log files
        if os.path.exists("logs/test_log.txt"):
            os.remove("logs/test_log.txt")
    
    def test_email_validation_valid_emails(self):
        """Test email validation with valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "admin+tag@company.org",
            "123@numbers.net"
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(self.manager.validate_email(email))
    
    def test_email_validation_invalid_emails(self):
        """Test email validation with invalid email addresses."""
        invalid_emails = [
            "",
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user.domain.com",
            None,
            123
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(self.manager.validate_email(email))
    
    def test_validate_user_data_valid(self):
        """Test user data validation with valid data."""
        valid_user = {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "admin"
        }
        
        is_valid, errors = self.manager.validate_user_data(valid_user)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_user_data_missing_fields(self):
        """Test user data validation with missing required fields."""
        invalid_users = [
            {"name": "", "email": "john@example.com", "role": "admin"},
            {"name": "John Doe", "email": "", "role": "admin"},
            {"name": "John Doe", "email": "john@example.com", "role": ""},
            {}
        ]
        
        for user_data in invalid_users:
            with self.subTest(user_data=user_data):
                is_valid, errors = self.manager.validate_user_data(user_data)
                self.assertFalse(is_valid)
                self.assertGreater(len(errors), 0)
    
    def test_validate_user_data_invalid_email(self):
        """Test user data validation with invalid email."""
        invalid_user = {
            "name": "John Doe",
            "email": "invalid-email",
            "role": "admin"
        }
        
        is_valid, errors = self.manager.validate_user_data(invalid_user)
        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid email format" in error for error in errors))
    
    def test_validate_user_data_invalid_role(self):
        """Test user data validation with invalid role."""
        invalid_user = {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "invalid_role"
        }
        
        is_valid, errors = self.manager.validate_user_data(invalid_user)
        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid role" in error for error in errors))
    
    def test_validate_user_data_invalid_name_length(self):
        """Test user data validation with invalid name length."""
        invalid_users = [
            {"name": "A", "email": "john@example.com", "role": "admin"},  # Too short
            {"name": "A" * 51, "email": "john@example.com", "role": "admin"}  # Too long
        ]
        
        for user_data in invalid_users:
            with self.subTest(user_data=user_data):
                is_valid, errors = self.manager.validate_user_data(user_data)
                self.assertFalse(is_valid)
                self.assertTrue(any("Name length" in error for error in errors))
    
    @patch('requests.Session.post')
    def test_create_single_user_success(self, mock_post):
        """Test successful user creation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "admin"
        }
        
        result = self.manager.create_single_user(user_data, 1)
        self.assertTrue(result)
    
    @patch('requests.Session.post')
    def test_create_single_user_api_error(self, mock_post):
        """Test user creation with API error."""
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Bad request"}
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response
        
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "admin"
        }
        
        result = self.manager.create_single_user(user_data, 1)
        self.assertFalse(result)
    
    def test_process_csv_file_nonexistent(self):
        """Test processing a non-existent CSV file."""
        result = self.manager.process_csv_file("nonexistent.csv")
        self.assertEqual(result['total_processed'], 0)
    
    def test_process_csv_file_empty(self):
        """Test processing an empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
        
        try:
            result = self.manager.process_csv_file(csv_path)
            self.assertEqual(result['total_processed'], 0)
        finally:
            os.unlink(csv_path)
    
    def test_process_csv_file_missing_headers(self):
        """Test processing CSV file with missing required headers."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'email'])  # Missing 'role' header
            writer.writerow(['John Doe', 'john@example.com'])
            csv_path = f.name
        
        try:
            result = self.manager.process_csv_file(csv_path)
            self.assertEqual(result['total_processed'], 0)
        finally:
            os.unlink(csv_path)
    
    @patch('requests.Session.post')
    def test_process_csv_file_valid_data(self, mock_post):
        """Test processing CSV file with valid data."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'email', 'role'])
            writer.writeheader()
            writer.writerow({'name': 'John Doe', 'email': 'john@example.com', 'role': 'admin'})
            writer.writerow({'name': 'Jane Smith', 'email': 'jane@example.com', 'role': 'user'})
            csv_path = f.name
        
        try:
            result = self.manager.process_csv_file(csv_path)
            self.assertEqual(result['total_processed'], 2)
            self.assertEqual(result['successful_creations'], 2)
            self.assertEqual(result['failed_creations'], 0)
        finally:
            os.unlink(csv_path)
    
    def test_process_csv_file_with_invalid_data(self):
        """Test processing CSV file with mix of valid and invalid data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'email', 'role'])
            writer.writeheader()
            writer.writerow({'name': 'John Doe', 'email': 'john@example.com', 'role': 'admin'})
            writer.writerow({'name': '', 'email': 'jane@example.com', 'role': 'user'})  # Missing name
            writer.writerow({'name': 'Bob', 'email': 'invalid-email', 'role': 'user'})  # Invalid email
            csv_path = f.name
        
        try:
            result = self.manager.process_csv_file(csv_path)
            self.assertEqual(result['total_processed'], 3)
            self.assertEqual(result['validation_failures'], 2)
            self.assertEqual(result['skipped_rows'], 2)
        finally:
            os.unlink(csv_path)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    @patch('requests.Session.post')
    def test_end_to_end_workflow(self, mock_post):
        """Test the complete end-to-end workflow."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        # Create test CSV file
        test_data = [
            {'name': 'Alice Johnson', 'email': 'alice@example.com', 'role': 'admin'},
            {'name': 'Bob Smith', 'email': 'bob@example.com', 'role': 'user'},
            {'name': '', 'email': 'invalid@example.com', 'role': 'user'},  # Invalid: missing name
            {'name': 'Charlie Brown', 'email': 'invalid-email', 'role': 'user'},  # Invalid: bad email
            {'name': 'David Wilson', 'email': 'david@example.com', 'role': 'moderator'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'email', 'role'])
            writer.writeheader()
            for row in test_data:
                writer.writerow(row)
            csv_path = f.name
        
        try:
            manager = UserProvisioningManager(log_file="integration_test_log.txt")
            result = manager.process_csv_file(csv_path)
            
            # Verify results
            self.assertEqual(result['total_processed'], 5)
            self.assertEqual(result['successful_creations'], 3)  # Alice, Bob, David
            self.assertEqual(result['validation_failures'], 2)  # Missing name, invalid email
            self.assertEqual(result['skipped_rows'], 2)
            
            manager.cleanup()
            
        finally:
            os.unlink(csv_path)
            # Clean up test log
            if os.path.exists("logs/integration_test_log.txt"):
                os.remove("logs/integration_test_log.txt")


def run_tests():
    """Run all tests and print results."""
    print("🧪 Running User Provisioning Manager Tests...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUserProvisioningManager))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
