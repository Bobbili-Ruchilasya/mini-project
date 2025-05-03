import os
import re
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY is not set. Please check your .env file.")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Fallback text
FALLBACK_TEXT = """
Introduction to Ecosystems
Ecosystems are communities of living organisms interacting with their environment. They include both biotic factors, like plants and animals, and abiotic factors, such as sunlight and water. Energy flows through ecosystems via food chains, starting from producers like plants to consumers like herbivores and predators. Nutrient cycles, such as the carbon and nitrogen cycles, sustain ecosystem balance. Human activities, like deforestation, can disrupt ecosystems, leading to biodiversity loss.
"""

# Clean the text
def clean_text(text):
    text = re.sub(r'[^\w\s\-\.\,\!\?\(\)]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ✅ Summary + Snippet
def get_key_points(text: str) -> dict:
    try:
        if not text or not text.strip():
            text = FALLBACK_TEXT
        text = clean_text(text)

        prompt = f"""
You are a helpful study assistant. Based on the following academic text, do the following:

1. Return a clear and detailed **bullet-point summary** with exactly 10 key points. Each point should start with "*".
2. Return a **text snippet** with exactly 10 meaningful, informative sentences.

Format:
Summary:
* point 1
* point 2
...
Snippet:
Sentence 1. Sentence 2. ...

Text: {text[:10000]}
        """

        response = model.generate_content(prompt)
        output = response.text.strip()
        logger.debug("Raw Response (Key Points): %s", output)

        if "Summary:" in output and "Snippet:" in output:
            parts = output.split("Snippet:")
            summary = parts[0].replace("Summary:", "").strip()
            snippet = parts[1].strip()
            return {"summary": summary, "snippet": snippet}
        else:
            return {
                "summary": "❌ Could not parse summary.",
                "snippet": "❌ Could not parse snippet."
            }

    except Exception as e:
        logger.error("Error in get_key_points: %s", str(e))
        return {
            "summary": f"❌ Error: {str(e)}",
            "snippet": f"❌ Error: {str(e)}"
        }

# ✅ Mind Map
def get_mind_map(text: str) -> str:
    try:
        if not text or not text.strip():
            text = FALLBACK_TEXT
        text = clean_text(text)

        prompt = f"""
You are an educational assistant. From the following text, create a **mind map** showing the hierarchy of key topics, subtopics, and important points.

Use bullet format like:
- Main Topic
  - Subtopic 1
    - Detail 1
    - Detail 2

Text: {text[:10000]}
        """

        response = model.generate_content(prompt)
        mind_map = response.text.strip()

        # Normalize bullet symbols
        lines = mind_map.split("\n")
        converted_lines = []
        for line in lines:
            if line.strip().startswith("*"):
                indent = line[:line.index("*")]
                content = line.strip()[1:].strip()
                converted_lines.append(f"{indent}- {content}")
            else:
                converted_lines.append(line)

        return "\n".join(converted_lines)

    except Exception as e:
        logger.error("Error in get_mind_map: %s", str(e))
        return "❌ Error generating mind map."

# ✅ MCQs
def get_mcqs(text: str) -> list:
    try:
        if not text or not text.strip():
            text = FALLBACK_TEXT
        text = clean_text(text)

        prompt = f"""
You are a tutor creating practice questions. Generate 5 **multiple choice questions (MCQs)** based on this text. Each should include:
- A clear question
- 4 options (A–D)
- The correct answer
- A short explanation

Format as JSON array:
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

Text: {text[:10000]}
        """

        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        # Clean triple backticks
        if raw_output.startswith("```"):
            raw_output = re.sub(r"^```(?:json)?", "", raw_output)
            raw_output = re.sub(r"```$", "", raw_output).strip()

        return json.loads(raw_output)

    except Exception as e:
        logger.error("Error in get_mcqs: %s", str(e))
        return [{
            "question": "Error generating question.",
            "options": {"A": "N/A", "B": "N/A", "C": "N/A", "D": "N/A"},
            "answer": "N/A",
            "explanation": "Could not generate due to API error."
        }]

# ✅ Study Plan
def get_study_plan(text: str) -> str:
    try:
        if not text or not text.strip():
            text = FALLBACK_TEXT
        text = clean_text(text)

        prompt = f"""
Create a detailed **7-day study plan** based on the following academic content. Include:
- Daily focus topics
- Learning objectives
- Suggested activities
- Review points

Format as:
Day 1: ...
Day 2: ...

Text: {text[:10000]}
        """

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.error("Error in get_study_plan: %s", str(e))
        return "❌ Error generating study plan."
