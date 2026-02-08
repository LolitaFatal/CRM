import re
import json
from openai import OpenAI
from flask import current_app
from backend.extensions import get_supabase

SCHEMA_CONTEXT = """
PostgreSQL Database Schema:
- patients (id, first_name, last_name, id_number, date_of_birth, gender, phone, email, address, created_at)
- services (id, name, description, price, duration_minutes, is_active)
- appointments (id, patient_id, service_id, doctor_id, appointment_date, status, notes, created_at)
  - status values: 'scheduled', 'completed', 'cancelled', 'no_show'
- invoices (id, invoice_number, patient_id, appointment_id, amount, status, issued_date, paid_date, created_at)
  - status values: 'paid', 'pending', 'overdue'
- tasks (id, title, description, status, priority, assigned_to, due_date, position, created_at)
  - status values: 'open', 'in_progress', 'done'
  - priority values: 'urgent', 'medium', 'normal'
- users (id, email, full_name, role, created_at)
  - role values: 'doctor', 'secretary'

Relationships:
- appointments.patient_id → patients.id
- appointments.service_id → services.id
- appointments.doctor_id → users.id
- invoices.patient_id → patients.id
- invoices.appointment_id → appointments.id
- tasks.assigned_to → users.id
"""

SQL_SYSTEM_PROMPT = f"""You are a SQL assistant for a medical clinic CRM system.
Given the following PostgreSQL schema, convert the user's Hebrew question into a single SELECT query.
Output ONLY the raw SQL query, nothing else. No markdown, no explanation.

{SCHEMA_CONTEXT}

Rules:
- Only SELECT queries are allowed
- Use proper JOINs when relating tables
- LIMIT results to 100 rows maximum
- Use Hebrew column aliases for readability (e.g., AS "שם מטופל")
- For patient full name, concatenate: first_name || ' ' || last_name
- Current date function: CURRENT_DATE
- For date comparisons use proper PostgreSQL date functions
- Never access password_hash column
- Never access medical_history table
"""

ANSWER_SYSTEM_PROMPT = """You are a medical clinic CRM assistant. Answer the user's question in Hebrew based ONLY on the data provided.
Rules:
- Answer ONLY based on the query results provided
- If no results were returned, say: "לא נמצאו תוצאות"
- Never fabricate or guess patient names, numbers, or medical data
- Format numbers with commas for readability
- Format currency as ₪ (Israeli Shekel)
- Keep answers concise and professional
- If you're unsure about the query interpretation, say so"""

BLOCKED_PATTERNS = [
    r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b',
    r'\b(INTO|SET)\b.*\b(VALUES|WHERE)\b',
    r'--',
    r';.*\S',  # Multiple statements
    r'\bmedical_history\b',
    r'\bpassword_hash\b',
]

ALLOWED_TABLES = ['patients', 'services', 'appointments', 'invoices', 'tasks', 'users']


def validate_sql(sql: str) -> tuple[bool, str]:
    sql_upper = sql.strip().upper()

    if not sql_upper.startswith('SELECT'):
        return False, 'רק שאילתות SELECT מותרות'

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            return False, 'השאילתה מכילה פעולות אסורות'

    return True, ''


def generate_sql(question: str) -> str:
    api_key = current_app.config['OPENAI_API_KEY']
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not configured')

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': SQL_SYSTEM_PROMPT},
            {'role': 'user', 'content': question},
        ],
        temperature=0,
        max_tokens=500,
    )

    sql = response.choices[0].message.content.strip()
    sql = sql.replace('```sql', '').replace('```', '').strip()
    return sql


def execute_sql(sql: str) -> list[dict]:
    supabase = get_supabase()
    result = supabase.rpc('execute_readonly_query', {'query_text': sql}).execute()
    return result.data if result.data else []


def generate_answer(question: str, sql: str, results: list) -> str:
    api_key = current_app.config['OPENAI_API_KEY']
    client = OpenAI(api_key=api_key)

    results_text = json.dumps(results[:50], ensure_ascii=False, indent=2) if results else "אין תוצאות"

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': ANSWER_SYSTEM_PROMPT},
            {'role': 'user', 'content': f'שאלה: {question}\n\nשאילתת SQL: {sql}\n\nתוצאות:\n{results_text}'},
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    return response.choices[0].message.content.strip()


def chat(question: str) -> dict:
    question = question.strip()
    if not question:
        return {'answer': 'אנא הזן שאלה', 'error': None}

    clinic_keywords = ['מטופל', 'תור', 'חשבונ', 'שירות', 'משימ', 'הכנס', 'תשלום',
                       'ביקור', 'רופא', 'מרפאה', 'פגיש', 'חודש', 'שבוע', 'היום',
                       'כמה', 'מי', 'אילו', 'מה', 'רשימ', 'סיכום', 'דוח']
    is_relevant = any(kw in question for kw in clinic_keywords)

    if not is_relevant and len(question) > 5:
        return {
            'answer': 'אני יכול לענות רק על שאלות הקשורות לנתוני המרפאה',
            'error': None,
            'sql': None,
        }

    try:
        sql = generate_sql(question)

        is_valid, error_msg = validate_sql(sql)
        if not is_valid:
            return {'answer': f'לא ניתן לבצע שאילתה זו: {error_msg}', 'error': error_msg, 'sql': sql}

        results = execute_sql(sql)
        answer = generate_answer(question, sql, results)

        return {
            'answer': answer,
            'sql': sql,
            'row_count': len(results),
            'error': None,
        }

    except Exception as e:
        return {
            'answer': 'אירעה שגיאה בעיבוד השאלה. נסה לנסח את השאלה אחרת.',
            'error': str(e),
            'sql': None,
        }
