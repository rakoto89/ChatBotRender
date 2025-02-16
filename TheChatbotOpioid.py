from flask import Flask, request, jsonify, render_template
import openai
import os
import pdfplumber
from dotenv import load_dotenv

# Load environment variables
env_path = ".env.txt"
load_dotenv(env_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Debugging: Check if API key is loaded
print(f"OpenAI API Key: {openai.api_key}")  # Remove this after confirming it works

app = Flask(__name__)

PDF_PATH = "OpioidInfo.pdf"

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        print(f"Extracted PDF Text (first 500 chars): {text[:500]}")  # Debugging
    except Exception as e:
        print(f"Error loading PDF: {str(e)}")  # Debugging
    return text.strip()

pdf_text = extract_text_from_pdf(PDF_PATH)

def is_question_relevant(question):
    relevance_prompt = (
        "Determine if the following question is related to opioids OR related topics such as overdose, withdrawal, "
        "prescription painkillers, fentanyl, narcotics, analgesics, opiates, opioid crisis, addiction, naloxone, or rehab. "
        "Respond with 'yes' if it is related and 'no' if it is not.\n\n"
        f"Question: {question}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": relevance_prompt}],
            max_tokens=10,
            temperature=0,
        )
        answer = response['choices'][0]['message']['content'].strip().lower()
        print(f"Relevance Check Response: {answer}")  # Debugging
        return answer == "yes"
    except Exception as e:
        print(f"Error in relevance check: {str(e)}")  # Debugging
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
        answer = response['choices'][0]['message']['content'].strip()
        print(f"GPT-3 Response: {answer}")  # Debugging
        return answer
    except openai.error.AuthenticationError:
        return "Authentication error: Check your OpenAI API key."
    except Exception as e:
        print(f"Error in GPT-3 response: {str(e)}")  # Debugging
        return f"An error occurred: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")  

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.form.get("question", "")

    if not user_question:
        return jsonify({"answer": "Please ask a valid question."})

    if is_question_relevant(user_question):
        answer = get_gpt3_response(user_question, pdf_text)
    else:
        answer = "Sorry, I can only answer questions related to opioids, addiction, overdose, or withdrawal."

    return jsonify({"answer": answer})

application = app

if __name__ == "__main__":
    app.run()

