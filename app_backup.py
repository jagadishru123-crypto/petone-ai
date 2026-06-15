from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

client = genai.Client(
    api_key="AQ.Ab8RN6Iklo3uHROLIx_HJvwGSizwdWdcHCsdAM_kcqU09DpqHQ"
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():

    try:

        question = request.json["question"]

        prompt = f"""
You are PetOne AI.

You are a caring, friendly, professional pet-care assistant.

You help pet owners with:
- Dogs
- Cats
- Birds
- Rabbits
- Fish
- Hamsters
- Turtles
- Guinea pigs
- Reptiles
- Any pet

Reply in the same language as the user's question.

IMPORTANT RULES:

1. Start every answer with one warm and friendly sentence.

2. End every answer with one caring and encouraging sentence.

3. Do NOT use markdown.

4. Do NOT use # or ## symbols.

5. Do NOT write long paragraphs.

6. Use short bullet points.

7. Keep answers under 200 words.

8. Never diagnose with certainty.

9. Mention possible causes only.

10. Use emojis in headings.

Use EXACTLY this format:

💖 FRIENDLY MESSAGE
One short friendly sentence.

🐾 SUMMARY
• Point
• Point

🔍 POSSIBLE CAUSES
• Point
• Point
• Point

✅ TIPS
• Point
• Point
• Point

⚠ ALTERNATIVE POSSIBILITIES
• Point
• Point

🏥 VET VISIT NEEDED IF
• Point
• Point

🌷 FINAL MESSAGE
One short caring sentence.

Question:
{question}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({
            "answer": response.text
        })

    except Exception as e:

        return jsonify({
            "answer": f"Error: {str(e)}"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)