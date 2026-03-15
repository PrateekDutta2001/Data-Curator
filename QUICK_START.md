# Quick Start Guide - Data Curator

## Running the Application

### Option 1: Using Python Script
```bash
python server.py
```

### Option 2: Using Flask Directly
```bash
flask run
```

### Option 3: Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

## Access the Application

Once the server is running, open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
data-curator/
├── server.py              # Flask backend server
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── app.js        # Frontend JavaScript
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
└── README.md            # Documentation
```

## Environment Setup

1. Create a `.env` file in the project root
2. Add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## API Endpoints

- `GET /` - Main application page
- `POST /api/generate-schema` - Generate dataset schema
- `POST /api/generate-data` - Generate synthetic data
- `POST /api/export` - Export dataset in specified format

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, change it in `server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Module Not Found
Install dependencies:
```bash
pip install -r requirements.txt
```

### API Key Error
Make sure your `.env` file exists and contains:
```
OPENROUTER_API_KEY=your_actual_key
```
