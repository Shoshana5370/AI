# Text to Commands

הופך טקסט חופשי ("מחק לוגים ישנים ושלח לי מייל") לפקודות מובנות ובטוחות,
תוך שימוש בטכניקות Prompt Engineering.

## מבנה הפרויקט

```
text_to_commands/
├── main.py              ← נקודת כניסה (CLI). מריץ ומציג. בלי לוגיקה.
├── requirements.txt
└── t2c/                 ← חבילת הליבה
    ├── config.py        ← נתונים בלבד: פעולות מותרות, סיכונים, שם מודל
    ├── schema.py        ← Output Structuring: מבנה הפלט שהמודל חייב למלא
    ├── prompts.py       ← הנדסת הפרומפטים: Role + Guardrails + Few-Shot
    ├── client.py        ← העטיפה היחידה סביב Gemini API
    └── parser.py        ← הליבה: מחבר הכל ומחזיר dict נקי
```

## עקרון המבנה

כל שכבה אחראית לדבר אחד, והתלות זורמת בכיוון אחד בלבד:

```
main.py  →  parser.py  →  client.py   →  Gemini API
                       →  prompts.py
                       →  schema.py
            (כולם)     →  config.py
```

היתרון: כשנוסיף שלב חדש בקורס, הוא מתיישב במקום מוגדר —
Self-Consistency ייכנס כקובץ ב-t2c, Gradio ייכנס כ-app.py ליד main.py,
ושום דבר קיים לא נשבר.

## הרצה

```bash
pip install -r requirements.txt
set GEMINI_API_KEY=המפתח-שלך        # Windows
py main.py                          # מריץ את סוללת הבדיקות
py main.py "מחק לוגים ישנים"          # בקשה בודדת
```

## טכניקות לפי שלבים

- שלב 1 — Role, Guardrails, Hard-coded context
- שלב 2 — Few-Shot, Output Structuring, Chain of Thought  ← אנחנו כאן
- שלב 3 — Prompt Chaining עם gates
- שלב 4 — Self-Consistency
- שלב 5 — Test suite + Prompt Optimization
- שלב 6 — UI עם Gradio
