import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

# ✅ Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY is not set. Please check your .env file.")

# ✅ Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")


def get_key_points(text: str) -> dict:
    try:
        prompt = f"""
You are a helpful study assistant. Based on the following academic text, do the following:

1. Return a clear and detailed **bullet-point summary** with at least 10 key points and at most covering the topics provided in pdf. Format each point starting with "*".

2. Return a **text snippet** with at least 8 meaningful and at most covering the topics provided in pdf, informative sentences extracted or paraphrased from the content.

### Output Format:
Summary:
* point 1
* point 2
...

Snippet:
Sentence 1. Sentence 2. ...

Text:
{text[:10000]}
        """

        response = model.generate_content(prompt)
        output = response.text.strip()

        summary = ""
        snippet = ""

        if "Summary:" in output and "Snippet:" in output:
            parts = output.split("Snippet:")
            summary = parts[0].replace("Summary:", "").strip()
            snippet = parts[1].strip()
        else:
            return {
                "summary": "❌ Could not parse summary.",
                "snippet": "❌ Could not parse snippet."
            }

        return {
            "summary": summary,
            "snippet": snippet
        }

    except Exception as e:
        return {
            "summary": f"❌ Error: {str(e)}",
            "snippet": f"❌ Error: {str(e)}"
        }


def get_mind_map(text: str) -> str:
    try:
        prompt = f"""
You are an educational assistant. From the following text, create a **mind map** showing the hierarchy of key topics, subtopics, and important points.

Use a clear bullet format like:
- Main Topic
  - Subtopic 1
    - Detail 1
    - Detail 2

Text:
{text[:10000]}
        """
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"❌ Error generating mind map: {str(e)}"


def get_mcqs(text: str) -> list:
    try:
        prompt = f"""
You are a tutor creating practice questions. Generate **5 multiple choice questions (MCQs)** based on this text. Each question should include:
- A question
- 4 options (A to D)
- Clearly marked correct answer
- A short explanation

Return the result in the following JSON format:

[
  {{
    "question": "...",
    "options": {{
      "A": "...",
      "B": "...",
      "C": "...",
      "D": "..."
    }},
    "answer": "A",
    "explanation": "..."
  }}
]

Text:
{text[:10000]}
"""
        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        # ✅ Clean code block formatting if present
        if raw_output.startswith("```"):
            raw_output = re.sub(r"^```(?:json)?", "", raw_output)
            raw_output = re.sub(r"```$", "", raw_output).strip()

        if not raw_output:
            return [{"error": "❌ Gemini returned an empty response for MCQs."}]

        return json.loads(raw_output)

    except Exception as e:
        return [{"error": f"❌ Error generating MCQs: {str(e)}"}]


def get_study_plan(text: str) -> str:
    try:
        prompt = f"""
You're a study planner. Based on this text, create a **7-day study plan**. Each day should include:
- A topic or theme
- Study tasks or focus points

Text:
{text[:10000]}
"""
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"❌ Error generating study plan: {str(e)}"
