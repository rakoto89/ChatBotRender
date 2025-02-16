from flask import Flask, request, jsonify, render_template
import openai
import os
import pdfplumber
from dotenv import load_dotenv

# Load environment variables (optional, only needed if you are running locally with a .env file)
load_dotenv()

# OpenAI API Key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

PDF_PATH = "OpioidInfo.pdf"

# Extract text from the provided PDF file
def extract_text_from_pdf(pdf_path):
text = ""
with pdfplumber.open(pdf_path) as pdf:
for page in pdf.pages:
extracted_text = page.extract_text()
if extracted_text:
text += extracted_text + "\n"
return text.strip()

pdf_text = extract_text_from_pdf(PDF_PATH)

# Generate GPT-3.5 response with optional PDF context
def get_gpt3_response(question, context):
general_context = "You are a helpful and knowledgeable assistant."

try:
response = openai.ChatCompletion.create(
model="gpt-3.5-turbo",
messages=[
{"role": "system", "content": general_context},
{"role": "user", "content": f"Here is some optional context (you may use it if helpful):\n{context}\n\nQuestion: {question}"}
],
max_tokens=2048,
temperature=0.7,
)
return response['choices'][0]['message']['content'].strip()
except openai.error.AuthenticationError:
return "Authentication error: Check your OpenAI API key."
except Exception as e:
return f"An error occurred: {str(e)}"

# Home route
@app.route("/")
def index():
return render_template("index.html")

# Ask route to handle user questions
@app.route("/ask", methods=["POST"])
def ask():
user_question = request.form.get("question", "")

if not user_question:
return jsonify({"answer": "Please ask a valid question."})

# Call GPT-3.5 to answer the user's question
answer = get_gpt3_response(user_question, pdf_text)

return jsonify({"answer": answer})

# For Render deployment compatibility
application = app

if __name__ == "__main__":
app.run(debug=True)

Sent from my iPhone
