from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Order, OrderItem, OrderStatusHistory
from cart.views import get_or_create_cart
from users.models import Address

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    items = cart.items.filter(saved_for_later=False).select_related('variant__product')
    if not items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('cart:detail')
    addresses = request.user.addresses.all()
    return render(request, 'orders/checkout.html', {
        'cart': cart, 'items': items, 'addresses': addresses,
        'payment_methods': [
            ('upi','📱 UPI (PhonePe / GPay / Paytm)'),
            ('card','💳 Credit / Debit Card'),
            ('netbanking','🏦 Net Banking'),
            ('cod','💵 Cash on Delivery'),
        ]
    })

@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('orders:checkout')
    cart = get_or_create_cart(request)
    items = cart.items.filter(saved_for_later=False).select_related('variant__product')
    if not items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('cart:detail')
    address_id = request.POST.get('address_id')
    payment_method = request.POST.get('payment_method','cod')
    special_instructions = request.POST.get('special_instructions','')
    if not address_id:
        messages.error(request, 'Please select a delivery address')
        return redirect('orders:checkout')
    address = get_object_or_404(Address, id=address_id, user=request.user)
    order = Order.objects.create(
        user=request.user,
        delivery_address=address,
        payment_method=payment_method,
        subtotal=cart.get_subtotal(),
        delivery_fee=cart.get_delivery_fee(),
        discount_amount=cart.get_discount(),
        total_amount=cart.get_total(),
        coupon_code=cart.coupon.code if cart.coupon else '',
        special_instructions=special_instructions,
        estimated_delivery=timezone.now() + timezone.timedelta(minutes=10),
    )
    for item in items:
        OrderItem.objects.create(
            order=order, variant=item.variant,
            product_name=item.variant.product.name,
            variant_name=item.variant.name,
            product_image=str(item.variant.product.display_image or ''),
            quantity=item.quantity,
            unit_price=item.variant.price,
            total_price=item.get_total(),
        )
        item.variant.stock = max(0, item.variant.stock - item.quantity)
        item.variant.save()
        item.variant.product.total_sold += item.quantity
        item.variant.product.save()
    OrderStatusHistory.objects.create(order=order, status='pending', note='Order placed')
    if payment_method == 'cod':
        order.payment_status = 'pending'
        order.status = 'confirmed'
        order.save()
        OrderStatusHistory.objects.create(order=order, status='confirmed', note='Order confirmed')
    coins_earned = int(order.total_amount / 10)
    request.user.reward_coins += coins_earned
    order.coins_earned = coins_earned
    order.save()
    request.user.save()
    if cart.coupon:
        cart.coupon.usage_count += 1
        cart.coupon.save()
    cart.items.all().delete()
    cart.coupon = None
    cart.save()
    messages.success(request, f'🎉 Order #{order.order_number} placed! Earned {coins_earned} coins.')
    return redirect('orders:success', order_id=order.id)

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/success.html', {'order': order})

@login_required
def order_list(request):
    status_filter = request.GET.get('status','')
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    if status_filter: orders = orders.filter(status=status_filter)
    return render(request, 'orders/order_list.html', {'orders': orders, 'status_filter': status_filter})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status not in ['pending','confirmed']:
        messages.error(request, 'Order cannot be cancelled at this stage')
        return redirect('orders:detail', order_id=order_id)
    if request.method == 'POST':
        reason = request.POST.get('reason','Customer request')
        order.status = 'cancelled'
        order.cancelled_at = timezone.now()
        order.cancellation_reason = reason
        order.save()
        OrderStatusHistory.objects.create(order=order, status='cancelled', note=reason)
        for item in order.items.all():
            item.variant.stock += item.quantity
            item.variant.save()
        messages.success(request, 'Order cancelled. Refund will be processed in 3-5 days.')
        return redirect('orders:list')
    return render(request, 'orders/cancel.html', {'order': order})

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    try: tracking = order.tracking
    except: tracking = None
    return render(request, 'orders/tracking.html', {'order': order, 'tracking': tracking})

@login_required
def reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = get_or_create_cart(request)
    added = 0
    for item in order.items.all():
        if item.variant.is_in_stock:
            ci, created = CartItem_model.objects.get_or_create(cart=cart, variant=item.variant, defaults={'quantity':0})
            ci.quantity += item.quantity
            ci.saved_for_later = False
            ci.save()
            added += 1
    messages.success(request, f'✅ {added} items added to cart!')
    return redirect('cart:detail')


