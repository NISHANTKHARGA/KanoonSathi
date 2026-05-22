from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv
from nepal_law import NEPAL_LAW_CONTEXT
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    history = data.get("history", [])

    if not question:
        return jsonify({"error": "No question provided"}), 400

    conversation = ""
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        text = msg.get("text", "") or ""
        conversation += f"{role}: {text}\n"

    prompt = f"""
    {NEPAL_LAW_CONTEXT}

    This is an ongoing conversation. Use the previous messages as context to answer the follow-up question.

    Previous conversation:
    {conversation}

    New question from user: {question}

    If the user says "tell me more", "explain further", "what about", or similar — continue from the previous topic.
    Give a helpful, clear legal answer based on Nepali law.
    Rules for your response:
    - Keep it brief and to the point
    - Only cite the ONE most relevant Act and section for this specific problem
    - Do NOT use ** or * for formatting — plain text only
    - Cite the relevant Act and section in plain text
    - End with one simple next step the user should take
    - If recommending a lawyer, specify the type e.g. "consult a Property Lawyer" or "consult a Criminal Lawyer" or "consult a Family Lawyer" based on the issue
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={"max_output_tokens": 200, "temperature": 0.3}
        )
        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "KanoonSathi AI is running"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)