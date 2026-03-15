/**
 * Data Curator - Frontend JavaScript
 * Handles UI interactions and API communication
 */

// Global state
const appState = {
    currentSchema: null,
    currentData: null,
    currentDatasetName: null
};

// DOM Elements
const elements = {
    problemStatement: document.getElementById('problemStatementMain'),
    useExampleBtn: document.getElementById('useExampleBtn'),
    rowSizeGroup: document.getElementById('rowSizeGroup'),
    customRows: document.getElementById('customRows'),
    outputFormat: document.getElementById('outputFormat'),
    generateBtn: document.getElementById('generateBtn'),
    loadingSpinner: document.getElementById('loadingSpinner'),
    loadingText: document.getElementById('loadingText'),
    errorMessage: document.getElementById('errorMessage'),
    successMessage: document.getElementById('successMessage'),
    welcomeSection: document.getElementById('welcomeSection'),
    problemStatementSection: document.getElementById('problemStatementSection'),
    schemaSection: document.getElementById('schemaSection'),
    schemaDisplay: document.getElementById('schemaDisplay'),
    statsSection: document.getElementById('statsSection'),
    previewSection: document.getElementById('previewSection'),
    downloadSection: document.getElementById('downloadSection'),
    dataTable: document.getElementById('dataTable'),
    tableHead: document.getElementById('tableHead'),
    tableBody: document.getElementById('tableBody'),
    statRows: document.getElementById('statRows'),
    statColumns: document.getElementById('statColumns'),
    statName: document.getElementById('statName'),
    downloadBtn: document.getElementById('downloadBtn'),
    downloadFormat: document.getElementById('downloadFormat'),
    downloadSize: document.getElementById('downloadSize')
};

// Example problem statement
const exampleProblem = `Generate a telecom customer churn dataset.

Columns:
customer_id, age, monthly_bill, contract_type, tenure_months, internet_service, support_calls, churn

Customers with higher support_calls and lower tenure are more likely to churn.`;

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
});

function initializeEventListeners() {
    // Use example button
    elements.useExampleBtn.addEventListener('click', () => {
        if (elements.problemStatement) {
            elements.problemStatement.value = exampleProblem;
            // Scroll to the problem statement section
            elements.problemStatementSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });

    // Row size radio buttons
    elements.rowSizeGroup.addEventListener('change', (e) => {
        if (e.target.value === 'custom') {
            elements.customRows.style.display = 'block';
            elements.customRows.focus();
        } else {
            elements.customRows.style.display = 'none';
        }
    });

    // Generate button
    elements.generateBtn.addEventListener('click', handleGenerate);

    // Download button
    elements.downloadBtn.addEventListener('click', handleDownload);
}

/**
 * Get the selected number of rows
 */
function getNumRows() {
    const selected = document.querySelector('input[name="rowSize"]:checked');
    if (selected && selected.value === 'custom') {
        const customValue = parseInt(elements.customRows.value);
        if (isNaN(customValue) || customValue < 1) {
            throw new Error('Please enter a valid number of rows (minimum 1)');
        }
        if (customValue > 100000) {
            throw new Error('Maximum 100,000 rows allowed');
        }
        return customValue;
    }
    return parseInt(selected ? selected.value : 100);
}

/**
 * Show loading spinner
 */
function showLoading(message = 'Processing...') {
    elements.loadingSpinner.style.display = 'block';
    elements.loadingText.textContent = message;
    hideMessages();
    hideResults();
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    elements.loadingSpinner.style.display = 'none';
}

/**
 * Show error message
 */
function showError(message) {
    elements.errorMessage.textContent = `❌ ${message}`;
    elements.errorMessage.style.display = 'block';
    elements.successMessage.style.display = 'none';
}

/**
 * Show success message
 */
function showSuccess(message) {
    elements.successMessage.textContent = `✅ ${message}`;
    elements.successMessage.style.display = 'block';
    elements.errorMessage.style.display = 'none';
}

/**
 * Hide all messages
 */
function hideMessages() {
    elements.errorMessage.style.display = 'none';
    elements.successMessage.style.display = 'none';
}

/**
 * Hide all result sections
 */
function hideResults() {
    elements.welcomeSection.style.display = 'none';
    if (elements.problemStatementSection) {
        elements.problemStatementSection.style.display = 'none';
    }
    elements.schemaSection.style.display = 'none';
    elements.statsSection.style.display = 'none';
    elements.previewSection.style.display = 'none';
    elements.downloadSection.style.display = 'none';
}

/**
 * Show results
 */
function showResults() {
    elements.welcomeSection.style.display = 'none';
    if (elements.problemStatementSection) {
        elements.problemStatementSection.style.display = 'block';
    }
}

/**
 * Handle generate button click
 */
async function handleGenerate() {
    try {
        // Validate input
        const problemStatement = elements.problemStatement.value.trim();
        if (!problemStatement) {
            showError('Please enter a problem statement');
            return;
        }

        // Get number of rows
        let numRows;
        try {
            numRows = getNumRows();
        } catch (error) {
            showError(error.message);
            return;
        }

        // Disable generate button
        elements.generateBtn.disabled = true;
        elements.generateBtn.textContent = '🔄 Generating...';

        // Step 1: Generate schema
        showLoading('Please Hold-on for a while we prepare data for you!');
        const schema = await generateSchema(problemStatement);
        
        if (!schema) {
            throw new Error('Failed to generate schema');
        }

        appState.currentSchema = schema;
        showSuccess('Schema generated successfully!');
        displaySchema(schema);

        // Step 2: Generate data
        showLoading('Please Hold-on for a while we prepare data for you!');
        const data = await generateData(schema, numRows);
        
        if (!data || !data.success) {
            throw new Error(data?.error || 'Failed to generate data');
        }

        appState.currentData = data.data;
        appState.currentDatasetName = data.dataset_name;
        
        showSuccess(`Dataset generated successfully! ${data.rows} rows, ${data.columns} columns`);
        displayStats(data);
        displayPreview(data.data);
        displayDownload(data);

        // Show results
        showResults();

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An unexpected error occurred');
    } finally {
        hideLoading();
        elements.generateBtn.disabled = false;
        elements.generateBtn.textContent = '🚀 Generate Dataset';
    }
}

/**
 * Generate schema from problem statement
 */
async function generateSchema(problemStatement) {
    try {
        const response = await fetch('/api/generate-schema', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ problem_statement: problemStatement })
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to generate schema');
        }

        return result.schema;
    } catch (error) {
        console.error('Schema generation error:', error);
        throw error;
    }
}

/**
 * Generate data from schema
 */
async function generateData(schema, numRows) {
    try {
        const response = await fetch('/api/generate-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                schema: schema,
                num_rows: numRows
            })
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to generate data');
        }

        return result;
    } catch (error) {
        console.error('Data generation error:', error);
        throw error;
    }
}

/**
 * Display schema
 */
function displaySchema(schema) {
    elements.schemaSection.style.display = 'block';
    elements.schemaDisplay.textContent = JSON.stringify(schema, null, 2);
}

/**
 * Display statistics
 */
function displayStats(data) {
    elements.statRows.textContent = data.rows.toLocaleString();
    elements.statColumns.textContent = data.columns;
    elements.statName.textContent = data.dataset_name || '-';
    
    elements.statsSection.style.display = 'block';
}

/**
 * Display data preview table
 */
function displayPreview(data) {
    if (!data || data.length === 0) {
        return;
    }

    // Clear existing table
    elements.tableHead.innerHTML = '';
    elements.tableBody.innerHTML = '';

    // Get column names from first row
    const columns = Object.keys(data[0]);
    
    // Create header
    const headerRow = document.createElement('tr');
    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    elements.tableHead.appendChild(headerRow);

    // Create rows (first 20)
    const previewRows = data.slice(0, 20);
    previewRows.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = row[col] !== null && row[col] !== undefined ? row[col] : '';
            tr.appendChild(td);
        });
        elements.tableBody.appendChild(tr);
    });

    elements.previewSection.style.display = 'block';
}

/**
 * Display download section
 */
function displayDownload(data) {
    elements.downloadFormat.textContent = elements.outputFormat.value;
    
    // Calculate size
    const sizeInKB = (JSON.stringify(data.data).length / 1024).toFixed(2);
    elements.downloadSize.textContent = `${sizeInKB} KB`;
    
    elements.downloadSection.style.display = 'block';
}

/**
 * Handle download button click
 */
async function handleDownload() {
    try {
        if (!appState.currentData) {
            showError('No data to download');
            return;
        }

        elements.downloadBtn.disabled = true;
        elements.downloadBtn.textContent = '⬇️ Downloading...';

        const format = elements.outputFormat.value;
        const datasetName = appState.currentDatasetName || 'synthetic_dataset';

        const response = await fetch('/api/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                format: format,
                dataset_name: datasetName,
                data: appState.currentData
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Download failed');
        }

        // Get filename from response headers or create one
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `${datasetName}.${format.toLowerCase()}`;
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showSuccess('Dataset downloaded successfully!');

    } catch (error) {
        console.error('Download error:', error);
        showError(error.message || 'Download failed');
    } finally {
        elements.downloadBtn.disabled = false;
        elements.downloadBtn.textContent = '⬇️ Download Dataset';
    }
}

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getNumRows,
        generateSchema,
        generateData
    };
}
