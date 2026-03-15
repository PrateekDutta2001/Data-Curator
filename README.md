# Data Curator

**AI-Powered Synthetic Dataset Generator for Machine Learning and Data Science Applications**

## Executive Summary

Data Curator is a production-ready web application designed to generate synthetic structured datasets for artificial intelligence and machine learning model training. The application leverages Large Language Models (LLMs) through the OpenRouter API to intelligently parse natural language dataset descriptions and automatically generate corresponding data schemas. Built with modern web technologies, Data Curator addresses the critical challenge of data scarcity in AI/ML development workflows by enabling rapid generation of realistic, validated synthetic datasets.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [System Requirements](#system-requirements)
4. [Installation and Setup](#installation-and-setup)
5. [Configuration](#configuration)
6. [API Documentation](#api-documentation)
7. [Data Generation Pipeline](#data-generation-pipeline)
8. [Security Considerations](#security-considerations)
9. [Performance Optimization](#performance-optimization)
10. [Deployment Guide](#deployment-guide)
11. [Contributing](#contributing)
12. [License](#license)

## Architecture Overview

### System Architecture

Data Curator follows a three-tier architecture pattern:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  (HTML5, CSS3, JavaScript ES6+, Responsive Design)      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│                    Application Layer                     │
│  (Python Flask/FastAPI, Request Handling, Validation)   │
└────────────────────┬────────────────────────────────────┘
                     │ API Calls
┌────────────────────▼────────────────────────────────────┐
│                    Integration Layer                     │
│  (OpenRouter API, Faker Library, Data Processing)       │
└─────────────────────────────────────────────────────────┘
```

### Component Architecture

1. **Frontend (Client-Side)**
   - Single Page Application (SPA) architecture
   - Asynchronous API communication via Fetch API
   - Real-time form validation and user feedback
   - Progressive data rendering for large datasets

2. **Backend (Server-Side)**
   - RESTful API endpoints
   - Request validation and sanitization
   - Rate limiting and error handling
   - Schema generation orchestration
   - Data generation engine

3. **External Services**
   - OpenRouter API for LLM-based schema generation
   - Faker library for realistic data synthesis

## Technology Stack

### Frontend Technologies

- **HTML5**: Semantic markup, accessibility compliance
- **CSS3**: Modern styling with Flexbox/Grid, CSS Variables, animations
- **JavaScript (ES6+)**: 
  - Async/await for asynchronous operations
  - Fetch API for HTTP requests
  - DOM manipulation and event handling
  - Client-side validation

### Backend Technologies

- **Python 3.8+**: Core programming language
- **Flask/FastAPI**: Web framework for API endpoints
- **Pandas**: Data manipulation and DataFrame operations
- **Faker**: Synthetic data generation library
- **Requests**: HTTP client for external API communication
- **python-dotenv**: Environment variable management
- **openpyxl**: Excel file generation support

### External APIs

- **OpenRouter API**: LLM inference service for schema generation
  - Endpoint: `https://openrouter.ai/api/v1/chat/completions`
  - Authentication: Bearer token
  - Models: `stepfun/step-3.5-flash:free`

### Development Tools

- **Git**: Version control
- **pip**: Package management
- **Virtual Environment**: Dependency isolation

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **RAM**: 4 GB minimum (8 GB recommended for large datasets)
- **Storage**: 500 MB free space
- **Network**: Internet connection for API access

### Recommended Requirements

- **Python**: Version 3.10 or higher
- **RAM**: 8 GB or higher
- **Storage**: 2 GB free space (for generated datasets)
- **Network**: Stable broadband connection

## Installation and Setup

### Prerequisites

Ensure Python 3.8+ is installed on your system:

```bash
python --version
```

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/data-curator.git
cd data-curator
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the project root:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Step 5: Run Application

```bash
# Development server (recommended)
python server.py

# Or using Flask directly
flask run

# Production (using Gunicorn - Linux/macOS)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app

# Production (using Waitress - Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 server:app
```

The application will be available at `http://localhost:5000`

### Project Structure

```
data-curator/
├── server.py              # Flask backend server
├── index.html            # Main HTML template
├── style.css             # Stylesheet
├── app.js                # Frontend JavaScript
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create from .env.example)
├── README.md            # This file
├── LICENSE              # MIT License
└── QUICK_START.md       # Quick start guide
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API authentication key | Yes | None |
| `FLASK_ENV` | Flask environment (development/production) | No | development |
| `FLASK_DEBUG` | Enable debug mode | No | False |
| `MAX_ROWS` | Maximum allowed dataset rows | No | 100000 |
| `API_TIMEOUT` | API request timeout (seconds) | No | 60 |
| `MAX_RETRIES` | Maximum API retry attempts | No | 3 |

### Application Configuration

Configuration can be modified directly in `server.py`:

```python
# Configuration constants in server.py
MAX_ROWS = 100000
DEFAULT_MODEL = "stepfun/step-3.5-flash:free"
API_TIMEOUT = 60
MAX_RETRIES = 3
```

Supported export formats: CSV, XLSX, JSON, TXT

## API Documentation

### Endpoints

#### POST `/api/generate-schema`

Generate dataset schema from natural language description.

**Request Body:**
```json
{
  "problem_statement": "Generate a telecom customer churn dataset with columns: customer_id, age, monthly_bill, contract_type, tenure_months, internet_service, support_calls, churn"
}
```

**Response:**
```json
{
  "success": true,
  "schema": {
    "dataset_name": "telecom_customer_churn",
    "columns": [
      {
        "name": "customer_id",
        "type": "string",
        "min": null,
        "max": null,
        "values": null
      },
      {
        "name": "age",
        "type": "integer",
        "min": 18,
        "max": 80,
        "values": null
      }
    ]
  }
}
```

#### POST `/api/generate-data`

Generate synthetic dataset based on schema.

**Request Body:**
```json
{
  "schema": { ... },
  "num_rows": 1000
}
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "rows": 1000,
  "columns": 8
}
```

#### POST `/api/export`

Export dataset in specified format.

**Request Body:**
```json
{
  "format": "CSV",
  "dataset_name": "my_dataset",
  "data": [...]
}
```

**Response:** File download with appropriate MIME type

### Error Responses

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Data Generation Pipeline

### Schema Generation Process

1. **Input Validation**: Validate and sanitize user-provided problem statement
2. **LLM Prompt Construction**: Format prompt with schema requirements
3. **API Request**: Send request to OpenRouter API with retry logic
4. **Response Parsing**: Extract and validate JSON schema from LLM response
5. **Schema Validation**: Verify schema structure and data types

### Data Synthesis Process

1. **Schema Parsing**: Iterate through schema columns
2. **Type-Based Generation**:
   - **Integer**: Random integer within [min, max] range
   - **Float**: Uniform random float within [min, max] range
   - **Categorical**: Random selection from predefined values
   - **String**: Context-aware generation using Faker library
3. **DataFrame Construction**: Assemble data into Pandas DataFrame
4. **Validation**: Verify data conforms to schema constraints
5. **Export Preparation**: Format data for requested export type

### Data Validation Rules

- Column count matches schema definition
- Data types match specified types
- Numeric values within defined ranges
- Categorical values restricted to allowed set
- No null values unless explicitly allowed

## Security Considerations

### API Key Management

- API keys stored in environment variables, never in code
- `.env` file excluded from version control
- Secrets management for production deployments

### Input Validation

- All user inputs sanitized and validated
- SQL injection prevention (parameterized queries if database used)
- XSS prevention through output encoding
- Rate limiting on API endpoints

### Data Privacy

- No user data stored permanently
- Generated datasets processed in-memory
- Temporary files cleaned after export

### Best Practices

- HTTPS required for production
- CORS configuration for cross-origin requests
- Request size limits
- Timeout configurations

## Performance Optimization

### Frontend Optimization

- Lazy loading for large datasets
- Virtual scrolling for data tables
- Debounced API requests
- Client-side caching

### Backend Optimization

- Efficient DataFrame operations
- Batch processing for large datasets
- Connection pooling for API requests
- Response compression

### Scalability Considerations

- Horizontal scaling support
- Stateless API design
- Efficient memory management
- Async processing for large datasets

## Deployment Guide

### Local Development

```bash
python server.py
```

### Production Deployment

#### Using Gunicorn (Linux/macOS)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 server:app
```

#### Using Waitress (Windows)

```bash
waitress-serve --host=0.0.0.0 --port=5000 --threads=4 server:app
```

#### Using Docker

```bash
docker build -t data-curator .
docker run -p 5000:5000 -e OPENROUTER_API_KEY=your_key data-curator
```

#### Using Cloud Platforms

- **Heroku**: Deploy via Git with Procfile
- **AWS Elastic Beanstalk**: Deploy via EB CLI
- **Google Cloud Run**: Container-based deployment
- **Azure App Service**: Git-based deployment

### Environment-Specific Configuration

Production environments should:
- Set `FLASK_ENV=production`
- Set `FLASK_DEBUG=False`
- Use secure session management
- Enable HTTPS
- Configure proper logging

## Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards

- Follow PEP 8 style guide
- Write docstrings for all functions
- Include unit tests for new features
- Update documentation for API changes

### Testing

```bash
# Run tests (if test suite is available)
pytest

# With coverage
pytest --cov=server tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Prateek Dutta**

Built for data professionals who struggle to get basic data for AI experiments.

## Acknowledgments

- OpenRouter for LLM API access
- Faker library contributors
- Flask community
- Open source contributors

---

**Version**: 1.0.0  
**Last Updated**: 2026  
**Status**: Production Ready
