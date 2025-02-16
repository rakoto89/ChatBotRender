from flask import Flask, request, jsonify, render_template
import os
import pdfplumber
from dotenv import load_dotenv
from openai import OpenAI  # Updated OpenAI import

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Load OpenAI API key from Render's secret file
try:
    with open("/etc/secrets/OPENAI_API_KEY", "r") as f:
        openai_api_key = f.read().strip()
except FileNotFoundError:
    openai_api_key = os.getenv("OPENAI_API_KEY")  # Fallback for local testing

# Ensure API key is available
if not openai_api_key:
    raise ValueError("Missing OpenAI API key!")

# OpenAI API client
openai.api_key = openai_api_key

@app.route("/")
def home():
    return "Chatbot API is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    mode = data.get("mode", "text")  # "text" or "speech"

    if not user_input:
        return jsonify({"error": "Message is required!"}), 400

    try:
        # OpenAI API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5", 
            messages=[{"role": "user", "content": user_input}]
        )
        bot_reply = response["choices"][0]["message"]["content"]

        return jsonify({
            "reply": bot_reply,
            "mode": mode  # Indicate whether to use speech or text output
        })

    except openai.OpenAIError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

