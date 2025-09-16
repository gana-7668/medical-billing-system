# billing_app/views.py

import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import PatientForm
from .models import Bill, BillItem, Patient
from .services.patient_service import (delete_patient_by_id,
                                       list_all_patients_with_recent_bills)


@login_required
def create_bill(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        patient_form = PatientForm(request.POST)
        medicine_data = request.POST.get('medicine_data')

        if medicine_data and (patient_id or patient_form.is_valid()):
            if patient_id:
                patient = Patient.objects.get(id=int(patient_id))
            else:
                patient = patient_form.save()
            bill = Bill.objects.create(patient=patient)

            medicines = json.loads(medicine_data)
            for med in medicines:
                BillItem.objects.create(
                    bill=bill,
                    medicine_name=med['medicine_name'],
                    quantity=int(med['quantity']),
                    price_per_tablet=Decimal(str(med['price']))
                )

            return redirect('bill_summary', bill_id=bill.id)
    else:
        patient_id = request.GET.get('patient_id')
        if patient_id:
            try:
                existing_patient = Patient.objects.get(id=int(patient_id))
                patient_form = PatientForm(instance=existing_patient)
            except Patient.DoesNotExist:
                patient_form = PatientForm()
                existing_patient = None
        else:
            patient_form = PatientForm()
            existing_patient = None

    today = timezone.localdate()
    bills_today_qs = Bill.objects.filter(created_at__date=today)
    today_bills_count = bills_today_qs.count()
    today_patients_count = bills_today_qs.values('patient').distinct().count()

    return render(request, 'billing_app/patient_form.html', {
        'patient_form': patient_form,
        'today_bills_count': today_bills_count,
        'today_patients_count': today_patients_count,
        'existing_patient_id': patient_id if request.method == 'GET' else request.POST.get('patient_id'),
    })

@login_required
def bill_summary(request, bill_id):
    bill = Bill.objects.get(id=bill_id)
    total_amount = sum((item.total_price() for item in bill.items.all()), Decimal(0))
    today = timezone.localdate()
    bills_today_qs = Bill.objects.filter(created_at__date=today)
    today_bills_count = bills_today_qs.count()
    today_patients_count = bills_today_qs.values('patient').distinct().count()
    return render(request, 'billing_app/bill_summary.html', {
        'bill': bill,
        'total_amount': total_amount,
        'today_bills_count': today_bills_count,
        'today_patients_count': today_patients_count,
    })

@login_required
def patient_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    error_message = None
    try:
        if query:
            patients = Patient.objects.filter(Q(name__icontains=query)).order_by('name')
            patients = patients.prefetch_related(
                Prefetch(
                    'bill_set',
                    queryset=Bill.objects.order_by('-created_at').prefetch_related('items'),
                    to_attr='prefetched_bills',
                )
            )
            for p in patients:
                bills_data = []
                for b in (p.prefetched_bills[:5] if hasattr(p, 'prefetched_bills') else p.bill_set.all()[:5]):
                    try:
                        total_amount = sum((i.total_price() for i in b.items.all()), Decimal(0))
                    except InvalidOperation:
                        total_amount = None
                    bills_data.append({
                        'id': b.id,
                        'created_at': b.created_at,
                        'total_amount': total_amount,
                    })
                results.append({
                    'id': p.id,
                    'name': p.name,
                    'age': p.age,
                    'phone': p.phone,
                    'bills': bills_data,
                })
    except InvalidOperation:
        error_message = 'Some bill amounts are invalid. Totals hidden for affected bills.'
    except Exception:
        error_message = 'Something went wrong while searching. Please try again.'

    return render(request, 'billing_app/patient_search.html', {
        'query': query,
        'results': results,
        'error_message': error_message,
    })


@login_required
def patient_list(request):
    error_message = None
    results = []
    try:
        results = list_all_patients_with_recent_bills()
    except Exception:
        error_message = 'Could not load all patients due to invalid data in some bills.'
    return render(request, 'billing_app/patient_list.html', {'results': results, 'error_message': error_message})


@login_required
def patient_delete(request, patient_id: int):
    if request.method != 'POST':
        return redirect('patient_list')
    success, err = delete_patient_by_id(patient_id)
    # For simplicity, we can pass messages via query params or rely on template logic to fetch again
    return redirect('patient_list')
