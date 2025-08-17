from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import json
from django.views.decorators.http import require_http_methods
from .models import Gst_User,Invoice,InvoiceItem,Purchase,PurchaseItem,RecentActivity
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum, Count
User = get_user_model()  # Uses your CustomUser
@csrf_exempt
@require_http_methods(["POST"])
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            phone = data.get('phone')
            company_name = data.get('company_name')
            gstin = data.get('gstin')
            pan = data.get('pan')
            address = data.get('address', '')
            city = data.get('city', '')
            state = data.get('state', '')
            pincode = data.get('pincode', '')

            required_fields = [email, username, password, company_name, gstin, pan]
            if not all(required_fields):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            if Gst_User.objects.filter(gstin=gstin).exists():
                return JsonResponse({'error': 'GSTIN already exists'}, status=400)
            if Gst_User.objects.filter(pan=pan).exists():
                return JsonResponse({'error': 'PAN already exists'}, status=400)

            # Create base user
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,  
            )

            # Create extended GST user
            gst_user = Gst_User.objects.create(
                user=user,
                gstin=gstin,
                pan=pan,
                phone=phone,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                company_name=company_name,
            )

            return JsonResponse({
                "status": "success",
                "user_id": user.id,
                "gst_user_id": gst_user.id
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"status": "error", "message": "Missing email or password"}, status=400)

        # Lookup username from email
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User does not exist"}, status=400)

        # Authenticate with username and password
        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"status": "success", "message": "Logged in"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=400)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_user(request):
    try:
        gst_user = get_object_or_404(Gst_User, user=request.user)
        user = gst_user.user

        data = {
           "user_id":user.id,
           "username":user.username,
           "phone":gst_user.phone,
           "address":gst_user.address,
           "city":gst_user.city,
           "state":gst_user.state,
           "pincode":gst_user.pincode,
           "comapny":gst_user.company_name,
           "gst_number":gst_user.gstin,
           "pan":gst_user.pan
        }
        return JsonResponse({"status": "success", "gst_user": data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_user(request):
    try:
        gst_user = get_object_or_404(Gst_User, user=request.user)
        user = gst_user.user
        user.delete()
        return JsonResponse({"status": "success", "message": "Employee deleted"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
@csrf_exempt
@require_http_methods(["POST"])
def create_invoice(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'unauthenticated', 'message': 'Login required'}, status=401)
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            invoice = Invoice.objects.create(
                user=request.user,
                invoice_no=data['invoiceNo'],
                date=data['date'],
                gstin=data.get('gstin', ''),
                customer_name=data['customerName'],
                customer_address=data.get('customerAddress', ''),
                cgst=data.get('cgst', 0),
                sgst=data.get('sgst', 0),
                igst=data.get('igst', 0),
                total_amount=data['totalAmount']
            )

            for item in data['items']:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item['description'],
                    quantity=item['quantity'],
                    rate=item['rate'],
                    amount=item['amount']
                )

            return JsonResponse({'status': 'success', 'message': 'Invoice created successfully.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST method allowed.'}, status=405)
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_invoices(request):
    try:
        invoices = Invoice.objects.filter(user=request.user).order_by('-date')
        invoice_data = []

        for invoice in invoices:
            invoice_data.append({
                'id': invoice.id,
                'invoiceNo': invoice.invoice_no,
                'date': invoice.date.strftime('%Y-%m-%d'),
                'customerName': invoice.customer_name,
                'amount': invoice.total_amount,
                'gst': invoice.cgst + invoice.sgst + invoice.igst,
                'status': 'paid' if invoice.total_amount < 30000 else 'pending',  # or use a real field
                'itc_status': invoice.itc_status or 'eligible',  # Default to 'eligible' if empty
            })

        return JsonResponse({'status': 'success', 'invoices': invoice_data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def gstr_report_view(request):
    try:
        data = json.loads(request.body)
        gstr_type = data.get("gstr_type")  # 'gstr1', 'gstr2', 'gstr3b'
        month_str = data.get("month")      # '2024-06'
        
        if gstr_type not in ["gstr1", "gstr2", "gstr3b"]:
            return JsonResponse({"error": "Invalid GSTR type"}, status=400)

        if not month_str or "-" not in month_str:
            return JsonResponse({"error": "Month (YYYY-MM) is required"}, status=400)

        year, month = map(int, month_str.split("-"))

        if gstr_type == "gstr1":
            invoices = Invoice.objects.filter(user=request.user, date__year=year, date__month=month)
            data = [
                {
                    "invoice_no": inv.invoice_no,
                    "date": inv.date.strftime("%Y-%m-%d"),
                    "customer": inv.customer_name,
                    "amount": inv.total_amount,
                    "gstin": inv.gstin,
                    "cgst": inv.cgst,
                    "sgst": inv.sgst,
                    "igst": inv.igst,
                }
                for inv in invoices
            ]
            return JsonResponse({"status": "success", "report_type": "GSTR-1", "data": data})

        elif gstr_type == "gstr2":
            purchases = Purchase.objects.filter(user=request.user, date__year=year, date__month=month)
            data = [
                {
                    "purchase_no": p.purchase_no,
                    "date": p.date.strftime("%Y-%m-%d"),
                    "supplier": p.supplier_name,
                    "amount": p.total_amount,
                    "gstin": p.gstin,
                    "cgst": p.cgst,
                    "sgst": p.sgst,
                    "igst": p.igst,
                }
                for p in purchases
            ]
            return JsonResponse({"status": "success", "report_type": "GSTR-2", "data": data})

        elif gstr_type == "gstr3b":
            invoices = Invoice.objects.filter(user=request.user, date__year=year, date__month=month)
            total_taxable = sum(inv.total_amount for inv in invoices)
            total_cgst = sum(inv.cgst for inv in invoices)
            total_sgst = sum(inv.sgst for inv in invoices)
            total_igst = sum(inv.igst for inv in invoices)

            data = {
                "outwardSupplies": total_taxable,
                "inwardSupplies": total_taxable * 0.6,  # Mocked data
                "netTax": total_cgst + total_sgst + total_igst,
                "interest": 500,  # Mocked
                "penalty": 200,   # Mocked
                "totalPayable": total_cgst + total_sgst + total_igst + 500 + 200,
            }
            return JsonResponse({"status": "success", "report_type": "GSTR-3B", "data": data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_purchase(request):
    try:
        data = json.loads(request.body)
        purchase = Purchase.objects.create(
            user=request.user,
            purchase_no=data['purchaseNo'],
            date=data['date'],
            gstin=data.get('gstin', ''),
            supplier_name=data['supplierName'],
            supplier_address=data.get('supplierAddress', ''),
            cgst=data.get('cgst', 0),
            sgst=data.get('sgst', 0),
            igst=data.get('igst', 0),
            total_amount=data['totalAmount']
        )

        for item in data['items']:
            PurchaseItem.objects.create(
                purchase=purchase,
                description=item['description'],
                quantity=item['quantity'],
                rate=item['rate'],
                amount=item['amount']
            )

        return JsonResponse({'status': 'success', 'message': 'Purchase recorded.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .models import Invoice, Purchase  # adjust import as needed

@csrf_exempt
@login_required
def itc_tracker(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        month = int(data.get('month'))
        year = int(data.get('year'))

        # -------------------- INVOICES --------------------
        invoices = Invoice.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        )

        # -------------------- PURCHASES --------------------
        purchases = Purchase.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        )

        total_eligible = 0.0
        claimed = 0.0
        reversed_amt = 0.0
        transactions = []

        # Process Invoices
        for inv in invoices:
            itc = float(inv.cgst + inv.sgst + inv.igst)
            total_eligible += itc

            if inv.itc_status == 'claimed':
                claimed += itc
            elif inv.itc_status == 'reversed':
                reversed_amt += itc

            transactions.append({
                "id": inv.id,
                "source": "Invoice",
                "invoice": inv.invoice_no,
                "vendor": inv.customer_name,
                "amount": float(inv.total_amount),
                "itc": itc,
                "status": inv.itc_status,
                "date": inv.created_at.strftime("%Y-%m-%d")
            })

        # Process Purchases
        for pur in purchases:
            itc = float(pur.cgst + pur.sgst + pur.igst)
            total_eligible += itc

            if pur.itc_status == 'claimed':
                claimed += itc
            elif pur.itc_status == 'reversed':
                reversed_amt += itc

            transactions.append({
                "id": pur.id,
                "source": "Purchase",
                "invoice": pur.purchase_no,
                "vendor": pur.supplier_name,
                "amount": float(pur.total_amount),
                "itc": itc,
                "status": pur.itc_status,
                "date": pur.created_at.strftime("%Y-%m-%d")
            })

        remaining = total_eligible - claimed - reversed_amt

        return JsonResponse({
            "status": "success",
            "month": month,
            "year": year,
            "itc_data": {
                "totalEligible": total_eligible,
                "claimed": claimed,
                "remaining": remaining,
                "reversed": reversed_amt
            },
            "transactions": transactions
        })

    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def update_itc_status(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'unauthenticated', 'message': 'Login required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        invoice_number = data.get('invoice')
        date = data.get('date')
        action = data.get('action')

        if not invoice_number or not date or action not in ['claim', 'reverse']:
            return JsonResponse({'error': 'Missing or invalid data'}, status=400)

        invoice = Invoice.objects.filter(user=request.user, invoice_no=invoice_number, date=date).first()

        if not invoice:
            return JsonResponse({'error': 'Invoice not found'}, status=404)

        if action == 'claim':
            invoice.itc_status = 'claimed'
        elif action == 'reverse':
            invoice.itc_status = 'reversed'

        invoice.save()

        RecentActivity.objects.create(
            user=request.user,
            invoice_number=invoice_number,
            action=action
        )

        return JsonResponse({'status': 'success', 'new_status': invoice.itc_status})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def monthly_summary(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        month = int(data.get('month'))
        year = int(data.get('year'))

        invoices = Invoice.objects.filter(user=request.user, date__month=month, date__year=year)
        purchases = Purchase.objects.filter(user=request.user, date__month=month, date__year=year)

        total_sales = sum(inv.total_amount for inv in invoices)
        total_tax = sum(inv.cgst + inv.sgst + inv.igst for inv in invoices)

        itc_claimed = sum(p.cgst + p.sgst + p.igst for p in purchases if p.itc_status == 'claimed')
        gst_payable = total_tax - itc_claimed

        return JsonResponse({
            "status": "success",
            "month": month,
            "year": year,
            "summary": {
                "sales": round(total_sales, 2),
                "tax": round(total_tax, 2),
                "itc": round(itc_claimed, 2),
                "gstPayable": round(gst_payable, 2)
            }
        })

    except Exception as e:
        print("Monthly summary error:", str(e))
        return JsonResponse({'error': str(e)}, status=400)
@csrf_exempt
@login_required
def get_recent_activities(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method allowed'}, status=405)

    try:
        recent = RecentActivity.objects.filter(user=request.user).order_by('-timestamp')[:10]
        data = [
            {
                "invoice": r.invoice_number,
                "action": r.action,
                "timestamp": r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for r in recent
        ]
        return JsonResponse({'status': 'success', 'activities': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def dashboard_stats(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method allowed'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'unauthenticated', 'message': 'Login required'}, status=401)
    try:
        user = request.user

        # Total Invoices
        total_invoices = Invoice.objects.filter(user=user).count()

        # Output GST (Sales)
        output_gst = Invoice.objects.filter(user=user).aggregate(
            total_cgst=models.Sum('cgst') or 0,
            total_sgst=models.Sum('sgst') or 0,
            total_igst=models.Sum('igst') or 0,
        )

        total_output_gst = (output_gst['total_cgst'] or 0) + (output_gst['total_sgst'] or 0) + (output_gst['total_igst'] or 0)

        # ITC Claimed
        itc = Purchase.objects.filter(user=user, itc_status='claimed').aggregate(
            claimed_cgst=models.Sum('cgst') or 0,
            claimed_sgst=models.Sum('sgst') or 0,
            claimed_igst=models.Sum('igst') or 0
        )

        total_itc = (itc['claimed_cgst'] or 0) + (itc['claimed_sgst'] or 0) + (itc['claimed_igst'] or 0)

        # GST Payable = Output GST - ITC
        gst_payable = total_output_gst - total_itc

        return JsonResponse({
            'status': 'success',
            'totalInvoices': total_invoices,
            'gstPayable': round(gst_payable, 2),
            'itcClaimed': round(total_itc, 2),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def platform_overview(request):
    try:
        total_businesses = Gst_User.objects.count()

        tax_totals = Invoice.objects.aggregate(
            total_cgst=Sum('cgst') or 0,
            total_sgst=Sum('sgst') or 0,
            total_igst=Sum('igst') or 0
        )

        total_gst = (tax_totals['total_cgst'] or 0) + \
                    (tax_totals['total_sgst'] or 0) + \
                    (tax_totals['total_igst'] or 0)

        response_data = {
            "status": "success",
            "stats": [
                {"value": f"{total_businesses:,}+", "label": "Happy Businesses"},
                {"value": f"₹{int(total_gst):,}+", "label": "GST Filed"},
                {"value": "99.9%", "label": "Uptime"},
                {"value": "24/7", "label": "Support"}
            ]
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
# views.py
import csv
import io
import json
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Invoice, Purchase

@csrf_exempt
@login_required
def export_report(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        report = data.get("report")
        export_format = data.get("format")
        month = int(data.get("month"))
        year = int(data.get("year"))
        gstr_type = data.get("gstr_type")  # Only needed for gstr

        filename = f"{report}_report_{month}_{year}"
        rows = []
        headers = []

        # ========== REPORT DATA PREPARATION ==========
        if report == "itc":
            invoices = Invoice.objects.filter(user=request.user, date__year=year, date__month=month)
            purchases = Purchase.objects.filter(user=request.user, date__year=year, date__month=month)

            headers = ['Source', 'Invoice No', 'Vendor', 'Amount', 'ITC', 'Status', 'Date']

            for inv in invoices:
                rows.append([
                    "Invoice", inv.invoice_no, inv.customer_name, float(inv.total_amount),
                    float(inv.cgst + inv.sgst + inv.igst), inv.itc_status, inv.created_at.strftime("%Y-%m-%d")
                ])
            for pur in purchases:
                rows.append([
                    "Purchase", pur.purchase_no, pur.supplier_name, float(pur.total_amount),
                    float(pur.cgst + pur.sgst + pur.igst), pur.itc_status, pur.created_at.strftime("%Y-%m-%d")
                ])

        elif report == "invoice":
            invoices = Invoice.objects.filter(user=request.user, date__year=year, date__month=month)
            headers = ['Invoice No', 'Date', 'Customer Name', 'Amount', 'GSTIN', 'CGST', 'SGST', 'IGST']
            for inv in invoices:
                rows.append([
                    inv.invoice_no, inv.date.strftime("%Y-%m-%d"), inv.customer_name,
                    float(inv.total_amount), inv.gstin, inv.cgst, inv.sgst, inv.igst
                ])

        elif report == "gstr":
            if gstr_type not in ["gstr1", "gstr2", "gstr3b"]:
                return JsonResponse({"error": "Invalid GSTR type"}, status=400)
            if gstr_type == "gstr1":
                invoices = Invoice.objects.filter(user=request.user, date__year=year, date__month=month)
                headers = ['Invoice No', 'Date', 'Customer', 'Amount', 'GSTIN', 'CGST', 'SGST', 'IGST']
                for inv in invoices:
                    rows.append([
                        inv.invoice_no, inv.date.strftime("%Y-%m-%d"), inv.customer_name,
                        float(inv.total_amount), inv.gstin, inv.cgst, inv.sgst, inv.igst
                    ])
            elif gstr_type == "gstr2":
                purchases = Purchase.objects.filter(user=request.user, date__year=year, date__month=month)
                headers = ['Purchase No', 'Date', 'Supplier', 'Amount', 'GSTIN', 'CGST', 'SGST', 'IGST']
                for p in purchases:
                    rows.append([
                        p.purchase_no, p.date.strftime("%Y-%m-%d"), p.supplier_name,
                        float(p.total_amount), p.gstin, p.cgst, p.sgst, p.igst
                    ])
            elif gstr_type == "gstr3b":
                invoices = Invoice.objects.filter(user=request.user, date__year=year, date__month=month)
                total_taxable = sum(inv.total_amount for inv in invoices)
                total_cgst = sum(inv.cgst for inv in invoices)
                total_sgst = sum(inv.sgst for inv in invoices)
                total_igst = sum(inv.igst for inv in invoices)

                headers = ['Outward Supplies', 'Inward Supplies', 'Net Tax', 'Interest', 'Penalty', 'Total Payable']
                rows.append([
                    total_taxable, total_taxable * 0.6,
                    total_cgst + total_sgst + total_igst, 500, 200,
                    total_cgst + total_sgst + total_igst + 500 + 200
                ])

        elif report == "summary":
            invoices = Invoice.objects.filter(user=request.user, date__year=year, date__month=month)
            purchases = Purchase.objects.filter(user=request.user, date__year=year, date__month=month)
            total_sales = sum(inv.total_amount for inv in invoices)
            total_tax = sum(inv.cgst + inv.sgst + inv.igst for inv in invoices)
            itc_claimed = sum(p.cgst + p.sgst + p.igst for p in purchases if p.itc_status == 'claimed')
            gst_payable = total_tax - itc_claimed

            headers = ['Total Sales', 'Total Tax', 'ITC Claimed', 'GST Payable']
            rows.append([total_sales, total_tax, itc_claimed, gst_payable])

        else:
            return JsonResponse({"error": "Invalid report type"}, status=400)

        # ========== FORMAT HANDLING ==========
        if export_format == "csv" or export_format == "excel":
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(headers)
            writer.writerows(rows)
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            return response

        elif export_format == "pdf":
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            y = height - 50

            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, f"{report.upper()} Report - {month}/{year}")
            y -= 30

            p.setFont("Helvetica-Bold", 10)
            for i, header in enumerate(headers):
                p.drawString(50 + i * 80, y, str(header)[:12])
            y -= 15

            p.setFont("Helvetica", 10)
            for row in rows:
                if y < 60:
                    p.showPage()
                    y = height - 50
                for i, val in enumerate(row):
                    p.drawString(50 + i * 80, y, str(val)[:12])
                y -= 15

            p.save()
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            return response

        else:
            return JsonResponse({"error": "Invalid format"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@login_required
def purchase_create(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        purchase = Purchase.objects.create(
            user=request.user,
            purchase_no=data['purchaseNo'],
            date=data['date'],
            gstin=data.get('gstin', ''),
            supplier_name=data['supplierName'],
            supplier_address=data.get('supplierAddress', ''),
            cgst=data.get('cgst', 0),
            sgst=data.get('sgst', 0),
            igst=data.get('igst', 0),
            total_amount=data['totalAmount']
        )

        for item in data['items']:
            PurchaseItem.objects.create(
                purchase=purchase,
                description=item['description'],
                quantity=item['quantity'],
                rate=item['rate'],
                amount=item['amount']
            )

        return JsonResponse({'status': 'success', 'message': 'Purchase created successfully.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@login_required
def purchase_list(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Only GET allowed'}, status=405)

    try:
        purchases = Purchase.objects.filter(user=request.user).order_by('-date')
        purchase_data = []

        for p in purchases:
            purchase_data.append({
                'id': p.id,
                'purchaseNo': p.purchase_no,
                'date': p.date.strftime('%Y-%m-%d'),
                'supplierName': p.supplier_name,
                'amount': p.total_amount,
                'gst': p.cgst + p.sgst + p.igst,
                'status': 'paid' if p.total_amount < 25000 else 'pending',
                'itc_status': p.itc_status or 'eligible'
            })

        return JsonResponse({'status': 'success', 'purchases': purchase_data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
