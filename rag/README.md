# RAG Project

זהו פרויקט שמיישם זרימת RAG (Retrieval-Augmented Generation) עם Python.

## מבנה הפרויקט

- `agent.py` – לוגיקת הסוכן/העיבוד הראשית.
- `main.py` – נקודת הכניסה להרצה.
- `prepare.py` – הכנה מקדימה של הנתונים או המידע.
- `pyproject.toml` – הגדרות הפרויקט ותלויות.
- `kiro/` – מסמכי תכנון ותיעוד.

## התקנה

1. צור סביבה וירטואלית:
   ```bash
   python -m venv .venv
   ```
2. הפעל את הסביבה:
   ```bash
   .venv\Scripts\Activate.ps1
   ```
3. התקן את התלויות:
   ```bash
   pip install -r requirements.txt
   ```

## הרצה

```bash
python main.py
```

## ארכיטקטורה

הפרויקט עבר לבניית זרימת RAG מלומדת באמצעות `workflow.py`:

- `agent.py` מחבר את Gradio ל־`create_default_workflow()`.
- `workflow.py` מיישם שלבים מוגדרים של Event-Driven workflow:
  - ולידציית קלט
  - שליפת מסמכים
  - ולידציית תוצאות השליפה
  - סינתוז תשובה
- `main.py` מפעיל את ממשק ה־Gradio.

## הערות

יש לעדכן את הקובץ בהתאם לפונקציונליות המיועדת של הפרויקט.
