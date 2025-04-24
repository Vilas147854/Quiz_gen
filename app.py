from flask import Flask, render_template, request, jsonify, session
import os
import requests
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For session management

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyAhlfLaoMt28x4zzZiQuEyJ5V4uiuBQk-g"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    topic = request.form.get("topic")
    num_questions = int(request.form.get("num_questions", 1))
    difficulty = request.form.get("difficulty", "medium")
    
    # Call Gemini API to generate questions
    prompt = f"""
    Generate {num_questions} multiple-choice question(s) on {topic} for SSC CGL preparation with {difficulty} difficulty level.
    Each question should have 4 options and one correct answer.
    Ensure the questions cover all the various categories in the SSC CGL Syllabus and are similar to previous year SSC CGL papers in style and difficulty.
    Return the response in JSON format as an array of objects, each with fields: question, options, correct_answer.
    Example:
    [
        {{
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": "4"
        }}
    ]
    """
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generation_config": {"response_mime_type": "application/json"}
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        quiz_data = response.json()
        quiz = json.loads(quiz_data["candidates"][0]["content"]["parts"][0]["text"])
        
        # Store questions in session
        session["quiz"] = quiz
        
        # Calculate total time (30 seconds per question)
        total_time = 30 * num_questions
        
        return render_template("quiz.html", quiz=quiz, total_time=total_time)
    except Exception as e:
        return render_template("index.html", error=f"Error generating quiz: {str(e)}")

@app.route("/submit", methods=["POST"])
def submit():
    user_answers = request.form.to_dict()
    quiz = session.get("quiz", [])
    results = []
    score = 0
    
    for q in quiz:
        question_text = q["question"]
        correct_answer = q["correct_answer"]
        user_answer = user_answers.get(question_text, None)
        is_correct = user_answer == correct_answer
        if is_correct:
            score += 1
        results.append({
            "question": question_text,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })
    
    # Clear the quiz from the session
    session.pop("quiz", None)
    
    return render_template("result.html", score=score, total=len(quiz), results=results)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)