from flask import Flask, request, jsonify, render_template
import os
import pdfplumber
from dotenv import load_dotenv
from openai import OpenAI  # Updated OpenAI import

# Load environment variables
load_dotenv()

# Initialize OpenAI client with the API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Use a relative path for the PDF
PDF_PATH = os.path.join(os.path.dirname(__file__), "PDFs", "OpioidInfo.pdf")

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip()

# Extract text from the PDF
pdf_text = extract_text_from_pdf(PDF_PATH)

def get_gpt3_response(question, context):
    """Gets a response from OpenAI based on the provided document."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Answer the user's question based on the provided document."},
                {"role": "user", "content": f"Here is the document content:\n{context}\n\nQuestion: {question}"}
            ],
            max_tokens=2048,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route("/")
def index():
    """Renders the chatbot UI."""
    return render_template("index.html")  

@app.route("/ask", methods=["POST"])
def ask():
    """Handles user questions and returns a chatbot response."""
    user_question = request.form.get("question", "")

    if not user_question:
        return jsonify({"answer": "Please ask a valid question."})

    answer = get_gpt3_response(user_question, pdf_text)
    
    return jsonify({"answer": answer})

# Gunicorn expects 'application' as the entry point
application = app  

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))




