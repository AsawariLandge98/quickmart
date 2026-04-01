from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from orders.models import Order
from .models import Payment
import json, hmac, hashlib

@login_required
def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'upi')
        if payment_method == 'cod':
            order.status = 'confirmed'
            order.payment_status = 'pending'
            order.save()
            return redirect('orders:success', order_id=order.id)
        # Demo: simulate Razorpay
        payment = Payment.objects.create(
            order=order, gateway='razorpay', method=payment_method,
            amount=order.total_amount, gateway_order_id=f'order_demo_{order.order_number}'
        )
        return render(request, 'payments/pay.html', {
            'order': order, 'payment': payment,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount_paise': int(order.total_amount * 100),
        })
    return render(request, 'payments/initiate.html', {'order': order})

@login_required
def payment_success(request):
    order_id = request.GET.get('order_id') or request.POST.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.payment_status = 'captured'
            order.status = 'confirmed'
            order.save()
            Payment.objects.filter(order=order).update(status='captured')
        except Order.DoesNotExist:
            pass
    return redirect('orders:list')

@login_required
def payment_failed(request):
    return render(request, 'payments/failed.html')

@login_required
def request_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        reason = request.POST.get('reason','')
        order.status = 'refund_initiated'
        order.save()
        from orders.models import OrderStatusHistory
        OrderStatusHistory.objects.create(order=order, status='refund_initiated', note=reason)
        from django.contrib import messages
        messages.success(request, 'Refund request submitted. Processing in 3-5 days.')
        return redirect('orders:detail', order_id=order_id)
    return render(request, 'payments/refund.html', {'order': order})
