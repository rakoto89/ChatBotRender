from flask import Flask, request, jsonify, render_template
import os
import pdfplumber
import openai
import traceback

# Load the OpenAI API key from Render's secret file
try:
    with open("/etc/secrets/OPENAI_API_KEY", "r") as f:
        openai_api_key = f.read().strip()
except FileNotFoundError:
    openai_api_key = os.getenv("OPENAI_API_KEY")  # Fallback for local testing

# Ensure API key is available
if not openai_api_key:
    raise ValueError("Missing OpenAI API key!")

# Set OpenAI API key
openai.api_key = openai_api_key

app = Flask(__name__)

# Use a relative path for the PDF
PDF_PATH = os.path.join(os.path.dirname(__file__), "PDFs", "OpioidInfo.pdf")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip()

pdf_text = extract_text_from_pdf(PDF_PATH)

# List of key topics related to opioids (from the PDF context)
relevant_topics = [
    "opioids", "addiction", "overdose", "withdrawal", "fentanyl", "heroin", "painkillers",
    "narcotics", "opioid crisis", "naloxone", "rehab"
]

def is_question_relevant(question):
    # Check if the question contains any of the relevant opioid-related topics
    for topic in relevant_topics:
        if topic.lower() in question.lower():
            return True
    return False

def get_gpt3_response(question, context):
    opioid_context = (
        "Assume the user is always asking about opioids or related topics like overdose, addiction, withdrawal, "
        "painkillers, fentanyl, heroin, and narcotics, even if they don't explicitly mention 'opioids'."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": opioid_context},
                {"role": "user", "content": f"Here is the document content:\n{context}\n\nQuestion: {question}"}
            ],
            max_tokens=2048,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.AuthenticationError:
        return "Authentication error: Check your OpenAI API key."
    except Exception as e:
        print(f"Error occurred in get_gpt3_response: {e}")
        return f"An unexpected error occurred: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")  

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.form.get("question", "")

    if not user_question:
        return jsonify({"answer": "Please ask a valid question."})

    # Check if the question is relevant to opioids or related topics in the PDF
    if is_question_relevant(user_question):
        # If relevant, fetch the answer based on the content of the PDF
        answer = get_gpt3_response(user_question, pdf_text)
    else:
        # If not relevant, return a default message
        answer = "Sorry, I can only answer questions related to opioids, addiction, overdose, or withdrawal."

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

