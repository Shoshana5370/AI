"""
client.py — עטיפה דקה סביב ה-API של Gemini.

המקום *היחיד* בפרויקט שמכיר את ספריית google-genai. אם נחליף ספק
(נניח חזרה ל-Anthropic כמו בקורס) — נשנה רק את הקובץ הזה, ושום דבר אחר.
"""

import os
from dotenv import load_dotenv

load_dotenv()
from google import genai
from google.genai import types

from . import config

# קוראים את המפתח מהסביבה. אם הגדרת אותו ישירות בקוד — אפשר להחליף כאן.
_API_KEY = os.environ.get("API","")

_client = genai.Client(api_key=_API_KEY)


def generate_json(system_prompt: str, user_text: str, response_schema: dict,
                  temperature: float = 0.0) -> str:
    """
    שולח בקשה למודל ומחזיר את הטקסט הגולמי (JSON כמחרוזת).
    הפרסור עצמו נעשה בשכבה שמעל — הקובץ הזה רק "מדבר" עם ה-API.

    temperature=0.0 כברירת מחדל = תשובות עקביות (חשוב לבטיחות).
    בשלב 4 (Self-Consistency) נעלה אותו בכוונה כדי לקבל מגוון.
    """
    response = _client.models.generate_content(
        model=config.MODEL,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=temperature,
            max_output_tokens=1024,
        ),
        contents=user_text,
    )
    return response.text
