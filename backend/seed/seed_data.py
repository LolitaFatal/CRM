"""
Seed script to populate the CRM database with realistic Hebrew dummy data.
Run: python -m backend.seed.seed_data
"""
import os
import random
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError('Set SUPABASE_URL and SUPABASE_KEY/SUPABASE_SERVICE_KEY in .env')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ──────────────────────────────────────────────
# Hebrew Names and Data
# ──────────────────────────────────────────────
FIRST_NAMES_M = ['דוד', 'יוסף', 'משה', 'אברהם', 'יעקב', 'שמעון', 'אליהו', 'חיים', 'דניאל', 'עמית']
FIRST_NAMES_F = ['שרה', 'מיכל', 'רחל', 'לאה', 'הדס', 'נועה', 'תמר', 'אורית', 'יעל', 'רות']
LAST_NAMES = ['כהן', 'לוי', 'מזרחי', 'פרץ', 'ביטון', 'אברהם', 'דהן', 'אזולאי', 'שלום', 'חדד',
              'ישראלי', 'גולן', 'אלון', 'בר', 'שפירא', 'רוזנברג', 'פרידמן', 'ברק', 'נחום', 'סגל']

STREETS = ['הרצל', 'בן גוריון', 'ז\'בוטינסקי', 'רוטשילד', 'אלנבי', 'דיזנגוף', 'ויצמן', 'בגין',
           'סוקולוב', 'ביאליק']
CITIES = ['תל אביב', 'ירושלים', 'חיפה', 'באר שבע', 'ראשון לציון', 'פתח תקווה', 'נתניה', 'רמת גן']

DIAGNOSES_POOL = [
    'יתר לחץ דם', 'סוכרת סוג 2', 'סוכרת סוג 1', 'אסתמה', 'כולסטרול גבוה',
    'דלקת פרקים', 'תת פעילות בלוטת התריס', 'אנמיה', 'מיגרנות', 'דום נשימה בשינה',
]
MEDICATIONS_POOL = [
    'מטפורמין (Metformin)', 'אנאלפריל (Enalapril)', 'סימבסטטין (Simvastatin)',
    'אומפרזול (Omeprazole)', 'אלטרוקסין (Eltroxin)', 'ונטולין (Ventolin)',
    'אקמול (Acamol)', 'נורופן (Nurofen)', 'קסרלטו (Xarelto)', 'רמיפריל (Ramipril)',
]
ALLERGIES_POOL = ['פניצילין', 'אספירין', 'סולפה', 'לטקס', 'יוד', 'אגוזים', 'ללא אלרגיות ידועות']
CHRONIC_POOL = [
    'אסתמה קלה - ללא התקפים בשנה האחרונה',
    'סוכרת מאוזנת תחת טיפול',
    'יתר לחץ דם מטופל',
    'כולסטרול גבוה - בטיפול תרופתי',
    'ללא מצב כרוני',
    'דלקת פרקים שגרונית',
    'תת פעילות בלוטת התריס - מאוזן',
]

SERVICES_DATA = [
    {'name': 'ייעוץ כללי', 'description': 'ייעוץ רפואי ראשוני או מעקב', 'price': 350, 'duration_minutes': 30},
    {'name': 'בדיקת דם', 'description': 'ספירת דם מלאה וכימיה', 'price': 200, 'duration_minutes': 15},
    {'name': 'א.ק.ג', 'description': 'בדיקת אלקטרוקרדיוגרמה', 'price': 300, 'duration_minutes': 20},
    {'name': 'אולטרסאונד', 'description': 'בדיקת אולטרסאונד אבחנתית', 'price': 500, 'duration_minutes': 30},
    {'name': 'חיסון שפעת', 'description': 'חיסון עונתי נגד שפעת', 'price': 100, 'duration_minutes': 10},
    {'name': 'בדיקת שמיעה', 'description': 'בדיקת שמיעה אודיומטרית', 'price': 250, 'duration_minutes': 25},
    {'name': 'ייעוץ תזונה', 'description': 'ייעוץ תזונתי מקיף', 'price': 400, 'duration_minutes': 45},
    {'name': 'מעקב כרוני', 'description': 'מעקב מחלות כרוניות', 'price': 280, 'duration_minutes': 30},
]

TASK_TITLES = [
    ('תיאום תור דחוף - ניתוח קטרקט', 'urgent', 'open'),
    ('הזמנת מלאי מחטים ומזרקים', 'medium', 'open'),
    ('עדכון פרוטוקול חיטוי', 'normal', 'open'),
    ('מעקב תוצאות בדיקות דם דחופות', 'urgent', 'in_progress'),
    ('עדכון תיקים רפואיים', 'medium', 'in_progress'),
    ('סיכום פגישת צוות שבועית', 'normal', 'done'),
    ('בדיקת מלאי תרופות חירום', 'medium', 'done'),
    ('חידוש רישיון מרפאה', 'normal', 'done'),
    ('תיאום הדרכת צוות חדש', 'medium', 'open'),
    ('שליחת תזכורת תורים שבועית', 'normal', 'done'),
]


def seed():
    print('🌱 Starting seed...')

    # ── 1. Users ──────────────────────────────
    print('  Creating users...')
    users_data = [
        {
            'email': 'doctor@demo.com',
            'password_hash': generate_password_hash('demo1234', method='pbkdf2:sha256'),
            'full_name': 'ד"ר אבי כהן',
            'role': 'doctor',
        },
        {
            'email': 'secretary@demo.com',
            'password_hash': generate_password_hash('demo1234', method='pbkdf2:sha256'),
            'full_name': 'מירב לוי',
            'role': 'secretary',
        },
    ]
    supabase.table('users').upsert(users_data, on_conflict='email').execute()
    users = supabase.table('users').select('id, role').execute().data
    doctor_id = next(u['id'] for u in users if u['role'] == 'doctor')
    secretary_id = next(u['id'] for u in users if u['role'] == 'secretary')
    print(f'  ✓ 2 users created')

    # ── 2. Patients ───────────────────────────
    print('  Creating patients...')
    patients_data = []
    for i in range(20):
        if i < 10:
            first = FIRST_NAMES_M[i]
            gender = 'male'
        else:
            first = FIRST_NAMES_F[i - 10]
            gender = 'female'
        last = LAST_NAMES[i]

        year = random.randint(1950, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)

        patients_data.append({
            'first_name': first,
            'last_name': last,
            'id_number': f'{random.randint(100000000, 999999999)}',
            'date_of_birth': f'{year}-{month:02d}-{day:02d}',
            'gender': gender,
            'phone': f'05{random.randint(0,9)}-{random.randint(1000000,9999999)}',
            'email': f'{first.replace("\"", "")}.{last}@example.com'.lower(),
            'address': f'רחוב {random.choice(STREETS)} {random.randint(1, 120)}, {random.choice(CITIES)}',
        })

    supabase.table('patients').insert(patients_data).execute()
    patients = supabase.table('patients').select('id, first_name, last_name').execute().data
    patient_ids = [p['id'] for p in patients]
    print(f'  ✓ {len(patients)} patients created')

    # ── 3. Services ───────────────────────────
    print('  Creating services...')
    supabase.table('services').insert(SERVICES_DATA).execute()
    services = supabase.table('services').select('id, price, name').execute().data
    service_ids = [s['id'] for s in services]
    print(f'  ✓ {len(services)} services created')

    # ── 4. Medical History ────────────────────
    print('  Creating medical histories...')
    med_histories = []
    for pid in patient_ids:
        num_diagnoses = random.randint(0, 3)
        num_meds = random.randint(0, 3)
        num_allergies = random.randint(0, 2)

        diagnoses = random.sample(DIAGNOSES_POOL, num_diagnoses) if num_diagnoses > 0 else []
        medications = random.sample(MEDICATIONS_POOL, num_meds) if num_meds > 0 else []

        if num_allergies > 0:
            allergies = random.sample(ALLERGIES_POOL[:6], num_allergies)
        else:
            allergies = ['ללא אלרגיות ידועות']

        med_histories.append({
            'patient_id': pid,
            'diagnoses': diagnoses,
            'medications': medications,
            'allergies': allergies,
            'chronic_conditions': random.choice(CHRONIC_POOL),
            'notes': 'מטופל במעקב שוטף',
        })

    supabase.table('medical_history').insert(med_histories).execute()
    print(f'  ✓ {len(med_histories)} medical histories created')

    # ── 5. Appointments ───────────────────────
    print('  Creating appointments...')
    now = datetime.now()
    statuses = ['completed', 'completed', 'completed', 'completed', 'scheduled', 'cancelled', 'no_show']
    appointments_data = []

    for _ in range(60):
        days_ago = random.randint(-14, 180)  # -14 = future
        apt_date = now - timedelta(days=days_ago)
        apt_date = apt_date.replace(
            hour=random.randint(8, 17),
            minute=random.choice([0, 15, 30, 45]),
            second=0, microsecond=0
        )

        status = random.choice(statuses)
        if days_ago < 0:
            status = 'scheduled'

        appointments_data.append({
            'patient_id': random.choice(patient_ids),
            'service_id': random.choice(service_ids),
            'doctor_id': doctor_id,
            'appointment_date': apt_date.isoformat(),
            'status': status,
            'notes': '',
        })

    supabase.table('appointments').insert(appointments_data).execute()
    appointments = supabase.table('appointments').select('id, patient_id, service_id, status, appointment_date').execute().data
    print(f'  ✓ {len(appointments)} appointments created')

    # ── 6. Invoices ───────────────────────────
    print('  Creating invoices...')
    service_price_map = {s['id']: float(s['price']) for s in services}
    payment_statuses = ['paid', 'paid', 'paid', 'pending', 'overdue']
    invoices_data = []
    invoice_counter = 1000

    completed_appts = [a for a in appointments if a['status'] == 'completed']
    for apt in completed_appts[:50]:
        invoice_counter += 1
        price = service_price_map.get(apt['service_id'], 300)
        pay_status = random.choice(payment_statuses)

        apt_date_str = apt['appointment_date'][:10]
        paid_date = apt_date_str if pay_status == 'paid' else None

        invoices_data.append({
            'invoice_number': f'INV-{invoice_counter}',
            'patient_id': apt['patient_id'],
            'appointment_id': apt['id'],
            'amount': price,
            'status': pay_status,
            'issued_date': apt_date_str,
            'paid_date': paid_date,
        })

    if invoices_data:
        supabase.table('invoices').insert(invoices_data).execute()
    print(f'  ✓ {len(invoices_data)} invoices created')

    # ── 7. Tasks ──────────────────────────────
    print('  Creating tasks...')
    assignees = [doctor_id, secretary_id]
    tasks_data = []

    for i, (title, priority, status) in enumerate(TASK_TITLES):
        due_offset = random.randint(-5, 30)
        tasks_data.append({
            'title': title,
            'description': f'תיאור המשימה: {title}',
            'status': status,
            'priority': priority,
            'assigned_to': random.choice(assignees),
            'due_date': (date.today() + timedelta(days=due_offset)).isoformat(),
            'position': i,
        })

    supabase.table('tasks').insert(tasks_data).execute()
    print(f'  ✓ {len(tasks_data)} tasks created')

    print('\n✅ Seed complete!')


if __name__ == '__main__':
    seed()
