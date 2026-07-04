"""
parser.py — לב הפרויקט: הופך טקסט חופשי לתוצאה מובנת.

זה ה"מנוע". הוא מחבר יחד את הפרומפט, הסכמה והקריאה למודל,
ומחזיר dict נקי שאפשר לעבוד איתו. לא יודע כלום על UI או על תצוגה.
"""

import json

from . import client, prompts, schema


def analyze(user_text: str) -> dict:
    """
    מקבל בקשה בשפה חופשית, מחזיר ניתוח מובנה:
        {
          "reasoning": str,   # ה-CoT — חשיבה לפני החלטה
          "actions": [{"action": str, "risk": "low|medium|high"}],
          "approved": bool,
          "message": str
        }
    """
    raw = client.generate_json(
        system_prompt=prompts.build_system_prompt(),
        user_text=user_text,
        response_schema=schema.RESPONSE_SCHEMA,
    )

    # בזכות response_schema הפלט אמור להיות JSON תקין תמיד,
    # אבל עוטפים בכל זאת ליתר ביטחון (Guardrail בצד הקוד).
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "reasoning": "המודל החזיר פלט לא תקין.",
            "actions": [],
            "approved": False,
            "message": "אירעה שגיאה בניתוח הבקשה. נסי שוב.",
        }
