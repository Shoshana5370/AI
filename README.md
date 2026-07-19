# AI Learning Repository

מאגר ללימוד בינה מלאכותית עם דוגמאות ופרויקטים מעשיים בתחומים של prompt engineering, RAG, ממשקי API ו־MCP.

## מה נמצא כאן?

- `text_to_commands/` — פרויקט שמתרגם טקסט חופשי לפקודות מובנות באמצעות Prompt Engineering ו־LLMs.
- `rag/` — ניסויים עם Retrieval-Augmented Generation, מבנה נתונים מובנים ו־workflow ל־Agent.
- `mcp/weather-chat_mcp/` — דוגמת MCP ל־weather assistant עם כלים ל־USA ולישראל, כולל דפדפן אוטומציה דרך Playwright.

## מטרת המאגר

המטרה היא להוות בסיס ללמידה, ניסויים ופיתוח בקוד פתוח של פרויקטי AI, עם דגש על:

- Prompt Engineering
- עבודה עם מודלים של שפה
- שילוב של שליפה סמנטית וחיבור לנתונים חיצוניים
- אינטגרציה עם שירותי API ו־browser automation
- עיצוב תוכנה מודולרי של פרויקטים קטנים

## מבנה הפרויקט

```text
mcp/weather-chat_mcp/   # דוגמה ל־MCP-based weather assistant עם API ו־Playwright
rag/                     # פרויקט RAG עם אינדקס מסמכים ושכבת נתונים מובנים
text_to_commands/        # פרויקט Text-to-Commands לפרומפט אינג'ינירינג ויצירת פקודות
```

## איך להתחיל

1. בחר את התיקיה המבוקשת (`mcp/weather-chat_mcp`, `rag`, או `text_to_commands`).
2. צור והפעל סביבה וירטואלית עבור הפרויקט:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. התקן את התלויות של הפרויקט:
   ```powershell
   pip install -r requirements.txt
   ```
4. עיין ב־README המקומי של כל פרויקט להמשך ההפעלה והדגמות.

## הערות כלליות

- חלק מהפרויקטים דורשים Python 3.13+.
- כל פרויקט כולל README מקומי עם הוראות התקנה והרצה ספציפיות.
- זהו מאגר לימודי, ולכן מומלץ לקרוא את הקוד ולהריץ דוגמאות כדי להבין את הארכיטקטורה והטכניקות.
