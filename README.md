# Automated User Provisioning Script

## Overview

This project is a solution to the Support Engineer Coding Challenge, focusing on debugging and enhancing a Python script that automates user account creation from CSV files via HTTP API calls.

## Problem Statement

The original script had several critical issues:
1. **No error logging**: Failed user creations weren't logged to files
2. **Poor error handling**: Limited exception handling and recovery mechanisms
3. **No data validation**: Missing validation for required fields and data formats
4. **No retry logic**: API failures weren't retried
5. **Limited feedback**: Minimal user feedback about processing status

## Solution Features

### 🔧 **Debugging & Fixes**
- ✅ **Comprehensive Error Logging**: All errors are logged to `logs/error_log.txt` with timestamps
- ✅ **Enhanced Error Handling**: Proper exception handling for network, API, and data errors
- ✅ **Data Validation**: Validates required fields, email formats, and business rules
- ✅ **File Handling**: Robust CSV parsing with encoding and format error handling

### 🚀 **New Features**
- ✅ **Retry Logic**: Automatic retry for failed API requests with exponential backoff
- ✅ **Statistics Tracking**: Comprehensive tracking of success/failure rates
- ✅ **Email Validation**: Regex-based email format validation
- ✅ **Role Validation**: Ensures only valid roles are processed
- ✅ **Skip Invalid Rows**: Automatically skips rows with missing required data
- ✅ **Progress Monitoring**: Real-time feedback on processing status

### 🏗️ **Code Quality Improvements**
- ✅ **Object-Oriented Design**: Clean class-based architecture
- ✅ **Type Hints**: Full type annotations for better code clarity
- ✅ **Comprehensive Documentation**: Detailed docstrings and comments
- ✅ **Modular Functions**: Single-responsibility functions for maintainability
- ✅ **Configuration Management**: Easily configurable parameters
- ✅ **Resource Cleanup**: Proper cleanup of HTTP sessions and resources

## Project Structure

```
automated-user-provisioning/
├── user_provisioning.py      # Enhanced main script
├── original_script.py         # Original buggy script for reference
├── users.csv                 # Sample CSV file with test data
├── requirements.txt          # Python dependencies
├── README.md                 # This documentation
├── logs/                     # Generated log files directory
│   └── error_log.txt        # Error and processing logs
├── test_script.py           # Unit tests for the script
└── config.json              # Configuration file
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd automated-user-provisioning
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python user_provisioning.py
```

### Configuration
The script can be configured by modifying the following variables in the `main()` function:

```python
CSV_FILE_PATH = "users.csv"                                    # Path to CSV file
API_ENDPOINT = "https://jsonplaceholder.typicode.com/users"   # API endpoint
```

### CSV File Format
The CSV file must contain the following headers:
- `name`: User's full name (required, 2-50 characters)
- `email`: Valid email address (required)
- `role`: User role (required, must be: admin, user, moderator, or guest)

**Example CSV:**
```csv
name,email,role
Alice,alice@example.com,admin
Bob,bob@example.com,user
Charlie,charlie@example.com,moderator
```

## Validation Rules

The script enforces the following validation rules:

### Required Fields
- **name**: Must be present and 2-50 characters long
- **email**: Must be present and valid email format
- **role**: Must be present and one of: admin, user, moderator, guest

### Data Quality Checks
- **Email Format**: Uses regex pattern for RFC-compliant email validation
- **Empty Rows**: Automatically skips completely empty rows
- **Whitespace Handling**: Trims whitespace from all fields
- **Missing Values**: Skips rows with any missing required fields

## Error Handling & Logging

### Log Files
All activities are logged to `logs/error_log.txt` with:
- Timestamps for all events
- Detailed error messages
- Row numbers for tracking issues
- API response details
- Processing statistics

### Error Types Handled
1. **Network Errors**: Connection timeouts, DNS failures
2. **API Errors**: HTTP error codes, invalid responses
3. **File Errors**: Missing files, encoding issues, CSV format errors
4. **Data Validation Errors**: Invalid emails, missing fields, invalid roles
5. **Unexpected Errors**: General exception handling with detailed logging

### Retry Logic
- **Automatic Retries**: Up to 3 attempts for failed API calls
- **Backoff Strategy**: Exponential backoff between retry attempts
- **Status Code Handling**: Retries on 429, 500, 502, 503, 504 errors

## Output & Reports

### Console Output
Real-time processing feedback including:
- File processing status
- Individual user creation results
- Validation warnings
- Error notifications
- Final statistics summary

### Log File Output
Comprehensive logging including:
- Session start/end timestamps
- Detailed error descriptions
- API request/response information
- Processing statistics
- Debugging information

### Processing Summary
```
============================================================
PROCESSING SUMMARY
============================================================
📊 Total rows processed: 8
✅ Successful creations: 5
❌ Failed creations: 0
⚠️  Skipped rows: 3
🔍 Validation failures: 3
📈 Success rate: 62.5%
============================================================
```

## Testing

Run the included test script to validate functionality:
```bash
python test_script.py
```

## Performance Considerations

- **Rate Limiting**: Small delay (0.1s) between API calls to avoid overwhelming servers
- **Connection Pooling**: HTTP session reuse for improved performance
- **Memory Efficiency**: Streaming CSV processing for large files
- **Timeout Handling**: Reasonable timeouts to prevent hanging

## Security Features

- **Input Validation**: Comprehensive validation prevents injection attacks
- **Error Sanitization**: Sensitive information is not logged
- **Safe File Handling**: Proper file encoding and error handling
- **HTTP Security**: Secure headers and timeout configurations

## Troubleshooting

### Common Issues

1. **CSV File Not Found**
   - Ensure `users.csv` exists in the same directory
   - Check file permissions

2. **API Connection Errors**
   - Verify internet connection
   - Check if the API endpoint is accessible
   - Review firewall settings

3. **Permission Errors**
   - Ensure write permissions for the `logs/` directory
   - Check file system permissions

4. **Validation Failures**
   - Review CSV data format
   - Ensure all required fields are present
   - Validate email addresses format

### Debug Mode
To enable more detailed logging, modify the logging level:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Future Enhancements

### Potential Improvements
1. **Configuration File**: External JSON/YAML configuration
2. **Command Line Interface**: argparse for flexible parameters
3. **Database Integration**: Support for database output
4. **Batch Processing**: Improved handling of large CSV files
5. **Monitoring Integration**: Metrics export for monitoring systems
6. **Email Notifications**: Alert notifications for processing completion
7. **API Authentication**: Support for authenticated API endpoints
8. **Data Transformation**: Field mapping and data transformation capabilities

### Scalability Considerations
1. **Async Processing**: asyncio for improved concurrent processing
2. **Queue Integration**: Message queue support for enterprise environments
3. **Distributed Processing**: Support for processing across multiple workers
4. **Caching**: Response caching for improved performance

## Contributing

When contributing to this project:
1. Follow PEP 8 style guidelines
2. Add comprehensive docstrings
3. Include type hints
4. Write unit tests for new features
5. Update documentation

## License

This project is created as part of a coding challenge assessment.

---

**Author**: Support Engineering Team  
**Version**: 2.0  
**Last Updated**: September 2025
