import numpy as np
from datetime import datetime
from backend.extensions import get_supabase

try:
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def _get_patient_features():
    supabase = get_supabase()

    patients = supabase.table('patients').select('id, first_name, last_name').execute().data or []

    appointments = supabase.table('appointments').select(
        'patient_id, appointment_date, status'
    ).execute().data or []

    invoices = supabase.table('invoices').select(
        'patient_id, amount, status'
    ).eq('status', 'paid').execute().data or []

    now = datetime.now()
    features = []

    for patient in patients:
        pid = patient['id']

        patient_appts = [a for a in appointments if a['patient_id'] == pid]
        patient_invs = [i for i in invoices if i['patient_id'] == pid]

        total_appointments = len(patient_appts)
        cancelled = sum(1 for a in patient_appts if a['status'] in ('cancelled', 'no_show'))
        cancelled_ratio = cancelled / max(total_appointments, 1)
        total_revenue = sum(float(i['amount']) for i in patient_invs)

        if patient_appts:
            dates = sorted(
                [datetime.fromisoformat(a['appointment_date'].replace('Z', '+00:00').replace('+00:00', ''))
                 for a in patient_appts if a['appointment_date']],
                reverse=True
            )
            if dates:
                last_visit = dates[0]
                days_since_last = (now - last_visit.replace(tzinfo=None)).days

                if len(dates) > 1:
                    intervals = [(dates[i] - dates[i + 1]).days for i in range(len(dates) - 1)]
                    avg_interval = sum(intervals) / len(intervals)
                else:
                    avg_interval = days_since_last
            else:
                days_since_last = 365
                avg_interval = 365
                last_visit = None
        else:
            days_since_last = 365
            avg_interval = 365
            last_visit = None

        features.append({
            'patient_id': pid,
            'patient_name': f"{patient['first_name']} {patient['last_name']}",
            'last_visit': last_visit.strftime('%Y-%m-%d') if last_visit else None,
            'days_since_last_visit': days_since_last,
            'total_appointments': total_appointments,
            'cancelled_ratio': cancelled_ratio,
            'total_revenue': total_revenue,
            'avg_interval': avg_interval,
        })

    return features


def get_all_churn_scores():
    features = _get_patient_features()

    if not features or not SKLEARN_AVAILABLE:
        return _simple_heuristic(features)

    X = np.array([
        [
            f['days_since_last_visit'],
            f['total_appointments'],
            f['cancelled_ratio'],
            f['total_revenue'],
            f['avg_interval'],
        ]
        for f in features
    ])

    if len(X) < 5:
        return _simple_heuristic(features)

    y = np.array([1 if f['days_since_last_visit'] > 90 else 0 for f in features])

    if len(set(y)) < 2:
        return _simple_heuristic(features)

    try:
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X, y)

        probabilities = model.predict_proba(X)[:, 1]

        results = []
        for i, f in enumerate(features):
            prob = round(float(probabilities[i]) * 100, 1)
            risk_level = 'high' if prob > 70 else ('medium' if prob > 40 else 'low')
            results.append({
                'patient_id': f['patient_id'],
                'patient_name': f['patient_name'],
                'last_visit': f['last_visit'],
                'days_since_last_visit': f['days_since_last_visit'],
                'churn_probability': prob,
                'risk_level': risk_level,
            })

        return sorted(results, key=lambda x: x['churn_probability'], reverse=True)

    except Exception:
        return _simple_heuristic(features)


def _simple_heuristic(features):
    results = []
    for f in features:
        days = f['days_since_last_visit']
        cancel_rate = f['cancelled_ratio']

        score = min(100, (days / 180) * 60 + cancel_rate * 40)
        risk_level = 'high' if score > 70 else ('medium' if score > 40 else 'low')

        results.append({
            'patient_id': f['patient_id'],
            'patient_name': f['patient_name'],
            'last_visit': f['last_visit'],
            'days_since_last_visit': f['days_since_last_visit'],
            'churn_probability': round(score, 1),
            'risk_level': risk_level,
        })

    return sorted(results, key=lambda x: x['churn_probability'], reverse=True)
