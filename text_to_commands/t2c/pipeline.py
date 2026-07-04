"""

pipeline.py — שרשרת השערים (Prompt Chaining with Gates).
 
כל בקשה עוברת דרך שלושה שערים לפי הסדר. שער שנכשל עוצר את השרשרת

ומדווח בדיוק היכן ומדוע — לצורך למידה ו-debugging.
 
  Gate 1: Parse     — האם המודל הצליח לנתח, ויש פעולות?

  Gate 2: Validate  — בדיקת קוד: כל פעולה באמת ברשימה המותרת?

  Gate 3: Safety    — האם המודל אישר (approved)?

"""
 
from . import parser, config
 
 
def run(user_text: str) -> dict:

    """

    מריץ את הבקשה דרך השערים ומחזיר דוח מלא:

        {

          "passed": bool,            # האם עברה את כל השערים

          "stopped_at": str | None,  # שם השער שעצר (None אם הצליח)

          "reason": str,             # למה נעצר / "הכל תקין"

          "trace": [ ... ],          # מה קרה בכל שער (ל-debugging)

          "analysis": dict           # הפלט המלא של ה-parser

        }

    """

    trace = []  # נתעד כאן כל שער שעברנו
 
    # ----- Gate 1: Parse -------------------------------------------------

    analysis = parser.analyze(user_text)
 
    if not analysis.get("actions"):

        # אין פעולות — או שלא זוהה כלום, או שהמודל דחה כבר בשלב הניתוח

        trace.append({"gate": "1-Parse", "status": "FAIL",

                      "detail": "לא זוהו פעולות תקינות בבקשה"})

        return _stop("1-Parse", analysis.get("message", "לא זוהו פעולות"),

                     trace, analysis)
 
    trace.append({"gate": "1-Parse", "status": "PASS",

                  "detail": f"זוהו {len(analysis['actions'])} פעולות"})
 
    # ----- Gate 2: Validate (בדיקת קוד, לא מודל!) ------------------------

    # שכבת הגנה שנייה: גם אם המודל המציא פעולה, הקוד שלנו תופס.

    for a in analysis["actions"]:

        if a["action"] not in config.ALLOWED_ACTIONS:

            trace.append({"gate": "2-Validate", "status": "FAIL",

                          "detail": f"הפעולה '{a['action']}' אינה ברשימה המותרת"})

            return _stop("2-Validate",

                         f"הפעולה '{a['action']}' אינה מוכרת למערכת",

                         trace, analysis)
 
    trace.append({"gate": "2-Validate", "status": "PASS",

                  "detail": "כל הפעולות קיימות ברשימה המותרת"})
 
    # ----- Gate 3: Safety ------------------------------------------------

    if not analysis.get("approved"):

        trace.append({"gate": "3-Safety", "status": "FAIL",

                      "detail": "המודל לא אישר את הבקשה"})

        return _stop("3-Safety", analysis.get("message", "הבקשה לא אושרה"),

                     trace, analysis)
 
    trace.append({"gate": "3-Safety", "status": "PASS",

                  "detail": "הבקשה אושרה על ידי המודל"})
 
    # ----- עברה את כל השערים --------------------------------------------

    return {

        "passed": True,

        "stopped_at": None,

        "reason": "הכל תקין — כל השערים עברו",

        "trace": trace,

        "analysis": analysis,

    }
 
 
def _stop(gate: str, reason: str, trace: list, analysis: dict) -> dict:

    """עוזר: בונה דוח עצירה אחיד כשנכשל שער."""

    return {

        "passed": False,

        "stopped_at": gate,

        "reason": reason,

        "trace": trace,

        "analysis": analysis,

    }
 