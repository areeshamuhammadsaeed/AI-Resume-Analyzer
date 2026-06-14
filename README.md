# AI-Resume-Analyzer
An AI-powered web application that checks a resume PDF against a job description using the Gemini API. It calculates a match score and highlights missing keywords.

## How to Setup and Run

1. **Install required packages:**
   ```bash
   pip install -r requirements.txt
 2.  Add your API Key:
Create a folder named .streamlit and put a file named secrets.toml inside it. Add your key like this:
GEMINI_API_KEY = "YOUR_API_KEY_HERE"

3. Run the app:
Bash
streamlit run analyzer.py

## Built With
Python (Backend language)
Streamlit (Web interface layout)
pdfplumber (Extracting text from PDFs)
Google GenAI (Gemini AI API processing)
