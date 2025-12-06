# AI Invoice Extractor 📄

**Automated invoice data extraction using AI Vision models** - Built with Test-Driven Development

Extract structured data from invoice files (PDF, JPG, PNG) using Grok Vision AI, with human-in-the-loop editing and Excel export.

## ✨ Features

- **AI-Powered Extraction:** Grok Vision API automatically reads invoice data
- **Multiple Formats:** Support for PDF, JPG, and PNG files
- **Smart Processing:** Intelligent image optimization and preprocessing
- **Human-in-the-Loop:** Review and edit extracted data before export
- **Excel Export:** Professional formatted `.xlsx` files with Polish headers
- **Privacy-First:** Files processed in-memory only (no storage)
- **Data Validation:** Pydantic models ensure data integrity
- **Comprehensive Tests:** 105 unit tests with 92% coverage

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Key

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your xAI Grok API key:

```env
XAI_API_KEY=your_actual_api_key_here
```

**Get your API key:** https://console.x.ai/

### 3. Run Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Upload Invoice:** Click "Browse files" and select an invoice (PDF/JPG/PNG)
2. **Analyze:** Click "Analyze Invoice" button
3. **Review:** AI extracts data automatically - review for accuracy
4. **Edit:** Modify any incorrect fields, add/remove items
5. **Export:** Download formatted Excel file

## 🧪 Testing

```bash
# Run all tests (105 tests, 92% coverage)
pytest

# Run with detailed coverage report
pytest --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit -v

# Run specific test file
pytest tests/unit/test_invoice_data.py -v

# Run excluding slow tests (API calls)
pytest -m "not slow"
```

View coverage report: `open htmlcov/index.html`

## Project Structure

```
fv extractor/
├── src/
│   ├── models/           # Pydantic data models
│   ├── processors/       # Image preprocessing
│   ├── ai/              # AI client (Grok/Claude)
│   ├── exporters/       # Excel export
│   └── utils/           # Validators
├── tests/
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Sample invoices
├── app.py               # Streamlit UI
└── specs/               # Technical specifications
```

## Tech Stack

- **Language:** Python 3.10+
- **UI:** Streamlit
- **AI:** xAI Grok Vision (MVP) / Anthropic Claude (future)
- **Validation:** Pydantic
- **Image Processing:** pdf2image, Pillow
- **Testing:** pytest

## License

MIT
