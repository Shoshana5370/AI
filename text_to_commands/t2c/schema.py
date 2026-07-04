"""
schema.py — הגדרת מבנה הפלט (Output Structuring).

זו הסכמה שהמודל *חייב* למלא. בזכותה אי אפשר ש"ישכח" שדה —
למשל את רמת הסיכון, כפי שקרה בשלב 1 עם טקסט חופשי.

שימי לב לסדר השדות: reasoning ראשון (Chain of Thought) —
המודל מנמק *לפני* שהוא קובע approved.
"""

from . import config

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string",
            "description": "חשיבה קצרה: אילו פעולות זוהו, מה הסיכון, והאם בטוח לאשר",
        },
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "risk": {"type": "string", "enum": config.RISK_LEVELS},
                },
                "required": ["action", "risk"],
            },
        },
        "approved": {
            "type": "boolean",
            "description": "האם הבקשה מאושרת לביצוע",
        },
        "message": {
            "type": "string",
            "description": "הסבר קצר בעברית למשתמש",
        },
    },
    "required": ["reasoning", "actions", "approved", "message"],
    # מבטיח ש-reasoning ייווצר ראשון — בלי זה ה-CoT לא באמת עובד
    "propertyOrdering": ["reasoning", "actions", "approved", "message"],
}
