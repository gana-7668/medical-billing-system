from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Dict, List

from django.db.models import Prefetch

from ..models import Bill, Patient


def build_patient_brief(patient: Patient) -> Dict:
    bills_data: List[Dict] = []
    for bill in getattr(patient, 'prefetched_bills', [])[:5]:
        try:
            total_amount = sum((item.total_price() for item in bill.items.all()), Decimal(0))
        except InvalidOperation:
            total_amount = None
        bills_data.append({
            'id': bill.id,
            'created_at': bill.created_at,
            'total_amount': total_amount,
        })
    return {
        'id': patient.id,
        'name': patient.name,
        'age': patient.age,
        'phone': patient.phone,
        'bills': bills_data,
    }


def list_all_patients_with_recent_bills() -> List[Dict]:
    patients = Patient.objects.all().order_by('name').prefetch_related(
        Prefetch('bill_set', queryset=Bill.objects.order_by('-created_at'), to_attr='prefetched_bills')
    )
    return [build_patient_brief(p) for p in patients]


def delete_patient_by_id(patient_id: int) -> tuple[bool, str | None]:
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return False, 'Patient not found.'
    try:
        # Cascade will remove related bills and items
        patient.delete()
        return True, None
    except Exception as exc:
        return False, 'Could not delete patient.'


