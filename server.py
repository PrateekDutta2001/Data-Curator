"""
Data Curator - Flask Backend Server
AI-Powered Synthetic Dataset Generator
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv
from faker import Faker
import random
import time
from io import BytesIO
import base64

# Load environment variables
load_dotenv()

# Initialize Flask app - serve templates and static files from root
app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)  # Enable CORS for API requests

# Initialize Faker
fake = Faker()

# Configuration
MAX_ROWS = 100000
DEFAULT_MODEL = "stepfun/step-3.5-flash:free"
API_TIMEOUT = 60
MAX_RETRIES = 3


def get_openrouter_api_key():
    """Get OpenRouter API key from environment variable."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    return api_key


def get_schema_from_llm(problem_statement, model, api_key, max_retries=3):
    """
    Use OpenRouter API to generate a JSON schema from the problem statement.
    Includes retry logic for rate limiting (429 errors).
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    prompt = f"""Convert the following dataset request into a JSON schema.

Problem Statement: {problem_statement}

Return ONLY a valid JSON object in this exact format (no markdown, no code blocks, just the JSON):
{{
    "dataset_name": "descriptive_name",
    "columns": [
        {{
            "name": "column_name",
            "type": "integer|float|categorical|string",
            "min": minimum_value_or_null,
            "max": maximum_value_or_null,
            "values": [array_of_values_for_categorical_or_null]
        }}
    ]
}}

For types:
- integer: provide min and max (numbers)
- float: provide min and max (numbers)
- categorical: provide values array (list of strings)
- string: use null for min, max, and values

Example for "age, income, credit_score, loan_amount, default":
{{
    "dataset_name": "loan_default_prediction",
    "columns": [
        {{"name": "age", "type": "integer", "min": 18, "max": 80, "values": null}},
        {{"name": "income", "type": "float", "min": 20000, "max": 200000, "values": null}},
        {{"name": "credit_score", "type": "integer", "min": 300, "max": 850, "values": null}},
        {{"name": "loan_amount", "type": "float", "min": 1000, "max": 500000, "values": null}},
        {{"name": "default", "type": "categorical", "min": null, "max": null, "values": ["Yes", "No"]}}
    ]
}}"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
            
            # Handle rate limiting (429)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                wait_time = min(retry_after * (2 ** attempt), 60)
                
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Rate limit exceeded. Please wait a few minutes and try again.")
            
            # Handle other HTTP errors
            response.raise_for_status()
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                raise Exception("Empty response from API")
            
            # Clean the content - remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            if content.startswith("```json"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            
            # Parse JSON
            schema = json.loads(content)
            return schema
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception("Request timeout. Please check your internet connection.")
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and "429" not in str(e):
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"API Request failed: {str(e)}")
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON schema: {str(e)}")
        
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise
    
    return None


def generate_synthetic_data(schema, num_rows):
    """
    Generate synthetic data based on the schema.
    """
    if not schema or 'columns' not in schema:
        raise ValueError("Invalid schema provided")
    
    data = {}
    
    for column in schema['columns']:
        col_name = column.get('name', '')
        col_type = column.get('type', 'string')
        col_min = column.get('min')
        col_max = column.get('max')
        col_values = column.get('values')
        
        if col_type == 'integer':
            min_val = int(col_min) if col_min is not None else 0
            max_val = int(col_max) if col_max is not None else 100
            data[col_name] = [random.randint(min_val, max_val) for _ in range(num_rows)]
        
        elif col_type == 'float':
            min_val = float(col_min) if col_min is not None else 0.0
            max_val = float(col_max) if col_max is not None else 100.0
            data[col_name] = [random.uniform(min_val, max_val) for _ in range(num_rows)]
        
        elif col_type == 'categorical':
            if col_values and len(col_values) > 0:
                data[col_name] = [random.choice(col_values) for _ in range(num_rows)]
            else:
                data[col_name] = [random.choice(['Yes', 'No']) for _ in range(num_rows)]
        
        elif col_type == 'string':
            col_lower = col_name.lower()
            if 'name' in col_lower:
                data[col_name] = [fake.name() for _ in range(num_rows)]
            elif 'email' in col_lower:
                data[col_name] = [fake.email() for _ in range(num_rows)]
            elif 'phone' in col_lower:
                data[col_name] = [fake.phone_number() for _ in range(num_rows)]
            elif 'city' in col_lower:
                data[col_name] = [fake.city() for _ in range(num_rows)]
            elif 'address' in col_lower:
                data[col_name] = [fake.address() for _ in range(num_rows)]
            elif 'company' in col_lower:
                data[col_name] = [fake.company() for _ in range(num_rows)]
            else:
                data[col_name] = [fake.word() for _ in range(num_rows)]
        
        else:
            data[col_name] = [fake.word() for _ in range(num_rows)]
    
    df = pd.DataFrame(data)
    return df


def validate_dataset(df, schema):
    """
    Validate the generated dataset against the schema.
    """
    if df is None or df.empty:
        return False, "Dataset is empty"
    
    if not schema or 'columns' not in schema:
        return False, "Invalid schema"
    
    # Check all columns exist
    schema_columns = {col.get('name') for col in schema['columns']}
    df_columns = set(df.columns)
    
    if schema_columns != df_columns:
        missing = schema_columns - df_columns
        extra = df_columns - schema_columns
        return False, f"Column mismatch. Missing: {missing}, Extra: {extra}"
    
    # Validate column types and ranges
    for column in schema['columns']:
        col_name = column.get('name')
        col_type = column.get('type')
        col_min = column.get('min')
        col_max = column.get('max')
        col_values = column.get('values')
        
        if col_name not in df.columns:
            continue
        
        if col_type == 'integer':
            if not pd.api.types.is_integer_dtype(df[col_name]):
                return False, f"Column {col_name} should be integer"
            if col_min is not None and (df[col_name] < int(col_min)).any():
                return False, f"Column {col_name} has values below minimum {col_min}"
            if col_max is not None and (df[col_name] > int(col_max)).any():
                return False, f"Column {col_name} has values above maximum {col_max}"
        
        elif col_type == 'float':
            if not pd.api.types.is_numeric_dtype(df[col_name]):
                return False, f"Column {col_name} should be float"
            if col_min is not None and (df[col_name] < float(col_min)).any():
                return False, f"Column {col_name} has values below minimum {col_min}"
            if col_max is not None and (df[col_name] > float(col_max)).any():
                return False, f"Column {col_name} has values above maximum {col_max}"
        
        elif col_type == 'categorical':
            if col_values:
                invalid_values = set(df[col_name].unique()) - set(col_values)
                if invalid_values:
                    return False, f"Column {col_name} has invalid values: {invalid_values}"
    
    return True, "Dataset is valid"


def export_dataset(df, format_type, dataset_name="synthetic_dataset"):
    """
    Export dataset in the specified format.
    """
    if df is None or df.empty:
        return None
    
    if format_type == "CSV":
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return output
    
    elif format_type == "XLSX":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return output
    
    elif format_type == "JSON":
        output = BytesIO()
        output.write(df.to_json(orient='records', indent=2).encode('utf-8'))
        output.seek(0)
        return output
    
    elif format_type == "TXT":
        output = BytesIO()
        output.write(df.to_string(index=False).encode('utf-8'))
        output.seek(0)
        return output
    
    return None


# Routes
@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    """Serve the CSS file."""
    return send_from_directory('.', 'style.css', mimetype='text/css')

@app.route('/app.js')
def serve_js():
    """Serve the JavaScript file."""
    return send_from_directory('.', 'app.js', mimetype='application/javascript')


@app.route('/api/generate-schema', methods=['POST'])
def generate_schema():
    """API endpoint to generate schema from problem statement."""
    try:
        data = request.get_json()
        problem_statement = data.get('problem_statement', '').strip()
        
        if not problem_statement:
            return jsonify({
                'success': False,
                'error': 'Problem statement is required'
            }), 400
        
        api_key = get_openrouter_api_key()
        schema = get_schema_from_llm(problem_statement, DEFAULT_MODEL, api_key)
        
        if schema:
            return jsonify({
                'success': True,
                'schema': schema
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate schema'
            }), 500
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-data', methods=['POST'])
def generate_data():
    """API endpoint to generate synthetic data."""
    try:
        data = request.get_json()
        schema = data.get('schema')
        num_rows = int(data.get('num_rows', 100))
        
        if num_rows > MAX_ROWS:
            return jsonify({
                'success': False,
                'error': f'Maximum {MAX_ROWS} rows allowed'
            }), 400
        
        if not schema:
            return jsonify({
                'success': False,
                'error': 'Schema is required'
            }), 400
        
        df = generate_synthetic_data(schema, num_rows)
        is_valid, message = validate_dataset(df, schema)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Convert DataFrame to JSON
        data_json = df.to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'data': data_json,
            'rows': len(df),
            'columns': len(df.columns),
            'dataset_name': schema.get('dataset_name', 'synthetic_dataset')
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export', methods=['POST'])
def export_data():
    """API endpoint to export dataset."""
    try:
        data = request.get_json()
        format_type = data.get('format', 'CSV')
        dataset_name = data.get('dataset_name', 'synthetic_dataset')
        data_rows = data.get('data', [])
        
        if not data_rows:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Convert JSON back to DataFrame
        df = pd.DataFrame(data_rows)
        
        file_data = export_dataset(df, format_type, dataset_name)
        
        if not file_data:
            return jsonify({
                'success': False,
                'error': 'Failed to export dataset'
            }), 500
        
        file_extension = format_type.lower()
        mime_types = {
            'CSV': 'text/csv',
            'XLSX': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'JSON': 'application/json',
            'TXT': 'text/plain'
        }
        
        return send_file(
            file_data,
            mimetype=mime_types.get(format_type, 'application/octet-stream'),
            as_attachment=True,
            download_name=f"{dataset_name}.{file_extension}"
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Check if API key is set
    try:
        get_openrouter_api_key()
        print("✓ OpenRouter API key found")
    except ValueError:
        print("⚠ Warning: OPENROUTER_API_KEY not found in environment variables")
        print("  The app will run but API calls will fail.")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
