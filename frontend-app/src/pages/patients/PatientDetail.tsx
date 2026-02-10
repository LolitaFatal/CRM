import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { apiFetch } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import Header from '../../components/Header'
import type { Patient, MedicalHistory, Appointment, Invoice, ApiResponse } from '../../types'

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('he-IL')
}

function formatCurrency(n: number) {
  return new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' }).format(n)
}

interface PatientData {
  patient: Patient
  medical_history: MedicalHistory | null
  appointments: Appointment[]
  invoices: Invoice[]
}

export default function PatientDetail() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<PatientData | null>(null)
  const { isDoctor } = useAuth()

  useEffect(() => {
    if (id) {
      apiFetch<ApiResponse<PatientData>>(`/api/patients/${id}`).then((res) => {
        if (res.data) setData(res.data)
      })
    }
  }, [id])

  if (!data) return <div className="p-8 text-gray-400">טוען...</div>

  const { patient, medical_history, appointments, invoices } = data

  return (
    <>
      <Header
        title={patient.full_name}
        subtitle={`${patient.phone} • ${patient.email || ''}`}
        actions={
          <Link to="/patients" className="text-sm text-gray-500 hover:text-primary flex items-center gap-1">
            <span className="material-symbols-outlined text-lg">arrow_forward</span>
            חזרה לרשימה
          </Link>
        }
      />
      <div className="p-8 space-y-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4">פרטים אישיים</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><span className="text-gray-500">מגדר:</span> <span className="text-gray-800 mr-2">{patient.gender === 'male' ? 'זכר' : 'נקבה'}</span></div>
            <div><span className="text-gray-500">תאריך לידה:</span> <span className="text-gray-800 mr-2">{patient.date_of_birth ? formatDate(patient.date_of_birth) : '-'}</span></div>
            <div><span className="text-gray-500">כתובת:</span> <span className="text-gray-800 mr-2">{patient.address || '-'}</span></div>
            <div><span className="text-gray-500">ת.ז:</span> <span className="text-gray-800 mr-2">{patient.id_number || '-'}</span></div>
          </div>
        </div>

        {isDoctor && medical_history && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-lg font-bold text-gray-800 mb-4">היסטוריה רפואית</h3>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-gray-500 font-medium">אבחנות:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {(medical_history.diagnoses || []).map((d, i) => (
                    <span key={i} className="bg-blue-50 text-blue-700 px-2 py-1 rounded-md text-xs">{d}</span>
                  ))}
                </div>
              </div>
              <div>
                <span className="text-gray-500 font-medium">תרופות:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {(medical_history.medications || []).map((m, i) => (
                    <span key={i} className="bg-green-50 text-green-700 px-2 py-1 rounded-md text-xs">{m}</span>
                  ))}
                </div>
              </div>
              <div>
                <span className="text-gray-500 font-medium">אלרגיות:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {(medical_history.allergies || []).map((a, i) => (
                    <span key={i} className="bg-red-50 text-red-700 px-2 py-1 rounded-md text-xs">{a}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4">תורים ({appointments.length})</h3>
          {appointments.length === 0 ? (
            <p className="text-sm text-gray-400">אין תורים</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="border-b">
                <tr>
                  <th className="text-right py-2 text-gray-500">תאריך</th>
                  <th className="text-right py-2 text-gray-500">שירות</th>
                  <th className="text-right py-2 text-gray-500">סטטוס</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map((a) => (
                  <tr key={a.id} className="border-b last:border-0">
                    <td className="py-2">{formatDate(a.appointment_date)}</td>
                    <td className="py-2">{a.service_name || '-'}</td>
                    <td className="py-2">{a.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4">חשבוניות ({invoices.length})</h3>
          {invoices.length === 0 ? (
            <p className="text-sm text-gray-400">אין חשבוניות</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="border-b">
                <tr>
                  <th className="text-right py-2 text-gray-500">תאריך</th>
                  <th className="text-right py-2 text-gray-500">סכום</th>
                  <th className="text-right py-2 text-gray-500">סטטוס</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id} className="border-b last:border-0">
                    <td className="py-2">{formatDate(inv.issued_date)}</td>
                    <td className="py-2">{formatCurrency(inv.amount)}</td>
                    <td className="py-2">{inv.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  )
}
