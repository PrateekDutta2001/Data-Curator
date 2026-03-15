import streamlit as st
import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv
from faker import Faker
import random
import time
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize Faker
fake = Faker()

# Page configuration
st.set_page_config(
    page_title="AI Synthetic Dataset Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main styling */
    .main {
        padding: 2rem 2rem;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    /* Subheader */
    h2 {
        color: #2d3748;
        font-weight: 600;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #718096;
        font-weight: 500;
    }
    
    /* Success messages */
    .stSuccess {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        border-radius: 10px;
        padding: 1rem;
        border-left: 5px solid #2f855a;
    }
    
    /* Error messages */
    .stError {
        background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
        border-radius: 10px;
        padding: 1rem;
        border-left: 5px solid #c53030;
    }
    
    /* Info boxes */
    .stInfo {
        background: linear-gradient(135deg, #90cdf4 0%, #63b3ed 100%);
        border-radius: 10px;
        padding: 1rem;
        border-left: 5px solid #3182ce;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar header */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
    }
    
    /* Text area */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(72, 187, 120, 0.6);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f7fafc;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #718096;
        font-size: 0.9rem;
        margin-top: 3rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #667eea;
        color: white;
        margin: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None
if 'schema' not in st.session_state:
    st.session_state.schema = None
if 'example_problem' not in st.session_state:
    st.session_state.example_problem = ''

def get_openrouter_api_key():
    """Get OpenRouter API key from environment variable."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        st.error("❌ OPENROUTER_API_KEY not found in .env file. Please add it.")
        st.stop()
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
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            # Handle rate limiting (429)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                wait_time = min(retry_after * (2 ** attempt), 60)  # Cap at 60 seconds
                
                if attempt < max_retries - 1:
                    st.warning(f"⏳ Rate limit reached. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    st.error("❌ Rate limit exceeded. Please wait a few minutes and try again, or check your OpenRouter API quota.")
                    return None
            
            # Handle other HTTP errors
            response.raise_for_status()
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                st.error("❌ Empty response from API. Please try again.")
                return None
            
            # Clean the content - remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                # Remove code block markers
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
                st.warning(f"⏳ Request timeout. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(2 ** attempt)
                continue
            else:
                st.error("❌ Request timeout. Please check your internet connection and try again.")
                return None
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and "429" not in str(e):
                st.warning(f"⏳ Request failed. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(2 ** attempt)
                continue
            else:
                error_msg = str(e)
                if "429" in error_msg:
                    st.error("❌ Rate limit exceeded. Please wait a few minutes and try again, or check your OpenRouter API quota.")
                else:
                    st.error(f"❌ API Request failed: {error_msg}")
                return None
        
        except json.JSONDecodeError as e:
            st.error(f"❌ Failed to parse JSON schema from LLM response: {str(e)}")
            st.error(f"Raw response preview: {content[:500] if 'content' in locals() else 'No content'}")
            return None
        
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return None
    
    return None

def generate_synthetic_data(schema, num_rows):
    """
    Generate synthetic data based on the schema.
    """
    if not schema or 'columns' not in schema:
        return None
    
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
                # Fallback to Yes/No if no values provided
                data[col_name] = [random.choice(['Yes', 'No']) for _ in range(num_rows)]
        
        elif col_type == 'string':
            # Use Faker for common field names
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
            # Default to string
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
        
        # Check integer type
        if col_type == 'integer':
            if not pd.api.types.is_integer_dtype(df[col_name]):
                return False, f"Column {col_name} should be integer"
            if col_min is not None and (df[col_name] < int(col_min)).any():
                return False, f"Column {col_name} has values below minimum {col_min}"
            if col_max is not None and (df[col_name] > int(col_max)).any():
                return False, f"Column {col_name} has values above maximum {col_max}"
        
        # Check float type
        elif col_type == 'float':
            if not pd.api.types.is_numeric_dtype(df[col_name]):
                return False, f"Column {col_name} should be float"
            if col_min is not None and (df[col_name] < float(col_min)).any():
                return False, f"Column {col_name} has values below minimum {col_min}"
            if col_max is not None and (df[col_name] > float(col_max)).any():
                return False, f"Column {col_name} has values above maximum {col_max}"
        
        # Check categorical type
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
        return df.to_csv(index=False).encode('utf-8')
    
    elif format_type == "XLSX":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return output.getvalue()
    
    elif format_type == "JSON":
        return df.to_json(orient='records', indent=2).encode('utf-8')
    
    elif format_type == "TXT":
        return df.to_string(index=False).encode('utf-8')
    
    return None

# Main UI Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<h1>Data Curator</h1>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-size: 1.1rem; color: #4a5568; margin-top: -1rem;'>
        Generate synthetic structured datasets for AI/ML training using AI-powered schema generation
    </p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: right;'>
        <span class='badge'>AI-Powered</span><br>
        <span class='badge' style='background: #48bb78;'>LLM Integrated</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.5rem;'>⚙️ Configuration</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
            Configure your dataset generation settings
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Problem Statement
    st.markdown("### 📝 Problem Statement")
    
    # Show example problem statement
    example_text = """Generate a telecom customer churn dataset.

Columns:
customer_id, age, monthly_bill, contract_type, tenure_months, internet_service, support_calls, churn

Customers with higher support_calls and lower tenure are more likely to churn."""
    
    with st.expander("📋 Example Format (Click to expand)", expanded=True):
        st.code(example_text, language=None)
        if st.button("📋 Use This Example", key="use_example", use_container_width=True):
            st.session_state.example_problem = example_text
            st.rerun()
    
    # Get example from session state if user clicked "Use Example"
    default_value = st.session_state.get('example_problem', '')
    
    problem_statement = st.text_area(
        "Describe your dataset",
        height=180,
        value=default_value,
        placeholder="Generate a telecom customer churn dataset.\n\nColumns:\ncustomer_id, age, monthly_bill, contract_type, tenure_months, internet_service, support_calls, churn\n\nCustomers with higher support_calls and lower tenure are more likely to churn.",
        help="Describe the dataset you want to generate, including column names and types. See example above for format.",
        label_visibility="collapsed"
    )
    
    # Clear example after it's been populated
    if default_value:
        st.session_state.example_problem = ''
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Model Selection - Hidden from UI, using default model
    # st.markdown("### 🤖 AI Model")
    # model = st.selectbox(
    #     "Select Model",
    #     # ["qwen/qwen3-coder:free", 
    #     ["stepfun/step-3.5-flash:free"],
    #     help="Select the OpenRouter model to use for schema generation.",
    #     label_visibility="collapsed"
    # )
    model = "stepfun/step-3.5-flash:free"  # Default model
    
    # st.markdown("<br>", unsafe_allow_html=True)
    
    # Number of Rows
    st.markdown("### 📊 Dataset Size")
    
    # Quick select options
    quick_options = st.radio(
        "Quick Select",
        ["100", "500", "1000", "5000", "10000", "Custom"],
        horizontal=True,
        help="Choose a preset or select Custom to enter your own number (max 100,000)",
        label_visibility="collapsed"
    )
    
    if quick_options == "Custom":
        num_rows = st.number_input(
            "Enter number of rows",
            min_value=1,
            max_value=100000,
            value=1000,
            step=100,
            help="Enter a custom number of rows (maximum 100,000)",
            label_visibility="collapsed"
        )
    else:
        num_rows = int(quick_options)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Output Format
    st.markdown("### 💾 Export Format")
    output_format = st.selectbox(
        "Output Format",
        ["CSV", "XLSX", "JSON", "TXT"],
        help="Select the download format.",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate Button
    generate_button = st.button("🚀 Generate Dataset", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #718096; font-size: 0.85rem; padding: 1rem;'>
        <p>💡 <strong>Tip:</strong> Be specific about column names and data types for best results</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area
if generate_button:
    # Validate input
    if not problem_statement or problem_statement.strip() == "":
        st.error("❌ Please enter a problem statement.")
    else:
        # Get API key
        api_key = get_openrouter_api_key()
        
        # Show loading spinner
        with st.spinner("🔄 Generating schema using AI..."):
            schema = get_schema_from_llm(problem_statement, model, api_key)
        
        if schema:
            st.session_state.schema = schema
            st.success("✅ **Schema generated successfully!**")
            
            # Display schema in a nice container
            with st.expander("📋 View Generated Schema", expanded=False):
                st.json(schema)
            
            # Generate data
            with st.spinner(f"🔄 Generating {num_rows:,} rows of synthetic data... This may take a moment."):
                df = generate_synthetic_data(schema, num_rows)
            
            if df is not None:
                # Validate dataset
                is_valid, message = validate_dataset(df, schema)
                
                if is_valid:
                    st.session_state.generated_data = df
                    st.success(f"✅ **Dataset generated successfully!** {message}")
                    
                    # Dataset info cards
                    st.markdown("### 📈 Dataset Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Rows", f"{len(df):,}")
                    with col2:
                        st.metric("Total Columns", len(df.columns))
                    with col3:
                        st.metric("Dataset Name", schema.get('dataset_name', 'N/A')[:15])
                    with col4:
                        st.metric("Memory Size", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Display preview
                    st.markdown("### 📊 Data Preview (First 20 Rows)")
                    st.dataframe(
                        df.head(20), 
                        use_container_width=True,
                        height=400
                    )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Export section
                    st.markdown("### 💾 Download Dataset")
                    dataset_name = schema.get('dataset_name', 'synthetic_dataset')
                    file_extension = output_format.lower()
                    
                    file_data = export_dataset(df, output_format, dataset_name)
                    
                    if file_data:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.download_button(
                                label=f"⬇️ Download as {output_format}",
                                data=file_data,
                                file_name=f"{dataset_name}.{file_extension}",
                                mime={
                                    "CSV": "text/csv",
                                    "XLSX": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    "JSON": "application/json",
                                    "TXT": "text/plain"
                                }.get(output_format, "application/octet-stream"),
                                use_container_width=True
                            )
                        with col2:
                            st.markdown(f"""
                            <div style='text-align: center; padding: 1rem; background: #f7fafc; 
                                        border-radius: 10px; margin-top: 0.5rem;'>
                                <p style='margin: 0; color: #4a5568; font-size: 0.9rem;'>
                                    <strong>Format:</strong> {output_format}<br>
                                    <strong>Size:</strong> {len(file_data) / 1024:.2f} KB
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ **Validation failed:** {message}")
            else:
                st.error("❌ **Failed to generate dataset.** Please check your schema and try again.")
        else:
            st.error("❌ **Failed to generate schema.** Please check your API key, try a different model, or wait a few minutes if you hit rate limits.")

# Show previous dataset if available
elif st.session_state.generated_data is not None:
    st.info("💡 **Tip:** Click 'Generate Dataset' in the sidebar to create a new dataset or regenerate with different parameters.")
    
    st.markdown("### 📊 Previous Dataset Preview")
    
    # Dataset info
    df = st.session_state.generated_data
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        if st.session_state.schema:
            st.metric("Dataset Name", st.session_state.schema.get('dataset_name', 'N/A')[:20])
    
    st.dataframe(df.head(20), use_container_width=True, height=400)
    
    # Export previous dataset
    if st.session_state.schema:
        dataset_name = st.session_state.schema.get('dataset_name', 'synthetic_dataset')
        file_data = export_dataset(st.session_state.generated_data, output_format, dataset_name)
        
        if file_data:
            st.markdown("### 💾 Download Previous Dataset")
            st.download_button(
                label=f"⬇️ Download as {output_format}",
                data=file_data,
                file_name=f"{dataset_name}.{output_format.lower()}",
                mime={
                    "CSV": "text/csv",
                    "XLSX": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "JSON": "application/json",
                    "TXT": "text/plain"
                }.get(output_format, "application/octet-stream"),
                use_container_width=True
            )

# Welcome message when no dataset generated yet
else:
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); 
                border-radius: 15px; margin: 2rem 0;'>
        <h2 style='color: #2d3748; margin-bottom: 1rem;'>🚀 Get Started</h2>
        <p style='color: #4a5568; font-size: 1.1rem; line-height: 1.8; max-width: 600px; margin: 0 auto;'>
            Configure your dataset settings in the sidebar and click <strong>"Generate Dataset"</strong> to create 
            synthetic data for your AI/ML projects. The AI will automatically generate a schema based on your description.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Example Problem Statement Section
    st.markdown("### 📝 Example Problem Statement Format")
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 1rem 0;'>
    """, unsafe_allow_html=True)
    
    example_problem = """Generate a telecom customer churn dataset.

Columns:
customer_id, age, monthly_bill, contract_type, tenure_months, internet_service, support_calls, churn

Customers with higher support_calls and lower tenure are more likely to churn."""
    
    st.code(example_problem, language=None)
    
    st.markdown("""
    <p style='color: #4a5568; font-size: 0.95rem; margin-top: 1rem;'>
        <strong>💡 Tips:</strong><br>
        • Start with a clear description of what the dataset is for<br>
        • List all column names separated by commas<br>
        • Add any business rules or relationships between columns<br>
        • Be specific about data types if needed (e.g., "age as integer", "price as float")
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("### ✨ Features")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style='padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h3 style='color: #667eea; margin-top: 0;'>🤖 AI-Powered</h3>
            <p style='color: #4a5568;'>Automatic schema generation from natural language descriptions</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h3 style='color: #667eea; margin-top: 0;'>📊 Multiple Formats</h3>
            <p style='color: #4a5568;'>Export to CSV, XLSX, JSON, or TXT formats</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style='padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h3 style='color: #667eea; margin-top: 0;'>⚡ Scalable</h3>
            <p style='color: #4a5568;'>Generate up to 10,000 rows efficiently</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p><strong>AI Synthetic Dataset Generator</strong> - Developed by Prateek dutta</p>
    <p style='font-size: 0.8rem;'>Built for data professional who struggles to get basic data for AI experiments</p>
</div>
""", unsafe_allow_html=True)
