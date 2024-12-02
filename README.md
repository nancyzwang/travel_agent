# PRFAQ Generator

This application generates Amazon-style PRFAQ (Press Release / FAQ) documents based on product descriptions and requirements. It uses OpenAI's GPT model to create comprehensive, well-structured PRFAQs that follow Amazon's six-pager format.

## Features
- Generates complete PRFAQ documents including:
  - Press Release
  - FAQ section
  - Working Backwards section
  - Technical Architecture
  - Success Metrics
  - Go-to-Market Strategy
- Exports to Word document format
- User-friendly Streamlit interface

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage
1. Enter your product description and requirements in the web interface
2. Click "Generate PRFAQ"
3. Review the generated content
4. Download the PRFAQ as a Word document

## Note
Make sure you have a valid OpenAI API key and sufficient credits for API usage.
