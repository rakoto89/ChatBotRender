from flask import Flask, request, jsonify, render_template
import openai
import os
import pdfplumber
from dotenv import load_dotenv

# Load the environment variables
env_path = ".env.txt"
load_dotenv(env_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Path to the PDF file
PDF_PATH = "OpioidInfo.pdf"

# Function to extract text from the PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip()

# Extract the text from the PDF file
pdf_text = extract_text_from_pdf(PDF_PATH)

# Debugging: Check the first 1000 characters of extracted PDF text
print(f"Extracted PDF text (first 1000 chars): {pdf_text[:1000]}")

# Function to get a response from GPT-3 with the context
def get_gpt3_response(question, context):
    opioid_context = (
        "Assume the user is always asking about opioids or related topics like overdose, addiction, withdrawal, "
        "painkillers, fentanyl, heroin, and narcotics, even if they don't explicitly mention 'opioids.'"
    )

    try:
        # Dynamically trimming the context if it's too long
        context_to_send = context[:1000]  # Truncate to the first 1000 characters
        
        # Log the context we are sending to GPT-3
        print(f"Context being sent to GPT-3:\n{context_to_send}")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": opioid_context},
                {"role": "user", "content": f"Here is the document content:\n{context_to_send}\n\nQuestion: {question}"}
            ],
            max_tokens=2048,
            temperature=0.7,
        )
        print(f"GPT-3 response: {response}")  # Debugging
        return response['choices'][0]['message']['content'].strip()
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

    # Debugging the user's question
    print(f"User question: {user_question}")

    # Provide a response from GPT-3 based on the extracted PDF context
    answer = get_gpt3_response(user_question, pdf_text)

    return jsonify({"answer": answer})

# Debugging the PDF extraction (Check the first 1000 characters)
print(f"Extracted PDF text (first 1000 chars): {pdf_text[:1000]}")

application = app
if __name__ == "__main__":
    app.run()
