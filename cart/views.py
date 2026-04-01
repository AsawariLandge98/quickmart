from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from store.models import ProductVariant, Coupon, Product
from django.utils import timezone
from django.db.models import Q
import json
import re

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    key = request.session.session_key
    if not key:
        request.session.create()
        key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=key, user=None)
    return cart

def cart_detail(request):
    cart = get_or_create_cart(request)
    items = cart.items.filter(saved_for_later=False).select_related('variant__product')
    saved = cart.items.filter(saved_for_later=True).select_related('variant__product')
    suggestions = []
    if items.exists():
        cat_ids = [i.variant.product.category_id for i in items]
        suggestions = Product.objects.filter(
            category_id__in=cat_ids, is_active=True
        ).exclude(
            id__in=[i.variant.product_id for i in items]
        ).prefetch_related('variants')[:4]
    return render(request, 'cart/cart.html', {
        'cart': cart, 'items': items, 'saved': saved, 'suggestions': suggestions
    })

@require_POST
def add_to_cart(request):
    variant_id = request.POST.get('variant_id')
    qty = int(request.POST.get('quantity', 1))
    variant = get_object_or_404(ProductVariant, id=variant_id, is_active=True)
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, defaults={'quantity': 0, 'saved_for_later': False})
    item.saved_for_later = False
    item.quantity += qty
    item.save()
    count = cart.get_count()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'count': count, 'message': f'{variant.product.name} added to cart!', 'subtotal': float(cart.get_subtotal()), 'total': float(cart.get_total())})
    messages.success(request, f'{variant.product.name} added to cart!')
    return redirect(request.META.get('HTTP_REFERER', '/'))

@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    action = request.POST.get('action', '')
    if action == 'increase': item.quantity += 1; item.save()
    elif action == 'decrease':
        item.quantity -= 1
        if item.quantity <= 0: item.delete()
        else: item.save()
    elif action == 'remove': item.delete()
    elif action == 'save_later': item.saved_for_later = True; item.save()
    elif action == 'move_to_cart': item.saved_for_later = False; item.save()
    cart = get_or_create_cart(request)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'count': cart.get_count(), 'subtotal': float(cart.get_subtotal()), 'delivery': float(cart.get_delivery_fee()), 'discount': float(cart.get_discount()), 'total': float(cart.get_total())})
    return redirect('cart:detail')

@require_POST
def apply_coupon(request):
    code = request.POST.get('code', '').strip().upper()
    cart = get_or_create_cart(request)
    now = timezone.now()
    try:
        coupon = Coupon.objects.get(code=code, is_active=True, valid_from__lte=now, valid_until__gte=now)
        if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
            msg = 'Coupon limit reached'; success = False
        elif cart.get_subtotal() < coupon.min_order_amount:
            msg = f'Min order Rs.{coupon.min_order_amount} required'; success = False
        else:
            cart.coupon = coupon; cart.save()
            msg = f'Coupon applied! You saved Rs.{cart.get_discount()}'; success = True
    except Coupon.DoesNotExist:
        msg = 'Invalid or expired coupon'; success = False
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': success, 'message': msg, 'discount': float(cart.get_discount()) if success else 0, 'total': float(cart.get_total())})
    if success: messages.success(request, msg)
    else: messages.error(request, msg)
    return redirect('cart:detail')

@require_POST
def remove_coupon(request):
    cart = get_or_create_cart(request)
    cart.coupon = None; cart.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'total': float(cart.get_total())})
    messages.info(request, 'Coupon removed')
    return redirect('cart:detail')

def cart_count_api(request):
    cart = get_or_create_cart(request)
    return JsonResponse({'count': cart.get_count(), 'total': float(cart.get_total())})

HINDI_NUMBERS = {'ek':1,'do':2,'teen':3,'tin':3,'char':4,'paanch':5,'panch':5,'chhe':6,'chha':6,'saat':7,'aath':8,'nau':9,'das':10,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10}
HINDI_ALIASES = {'aalu':'potato','aalo':'potato','aaloo':'potato','alu':'potato','tamatar':'tomato','pyaaz':'onion','pyaj':'onion','doodh':'milk','dudh':'milk','bread':'bread','anda':'egg','ande':'egg','eggs':'egg','chawal':'rice','chaawal':'rice','daal':'dal','dal':'dal','namak':'salt','cheeni':'sugar','tel':'oil','chai':'tea','chay':'tea','coffee':'coffee','biscuit':'biscuit','chips':'chips','namkeen':'namkeen','maida':'flour','atta':'wheat flour','aata':'wheat flour','makhan':'butter','paneer':'paneer','dahi':'curd','lassi':'lassi','matar':'peas','gajar':'carrot','palak':'spinach','gobhi':'cauliflower','kela':'banana','seb':'apple','santara':'orange','angoor':'grapes','sabun':'soap','shampoo':'shampoo'}

def extract_quantity(text):
    text = text.lower()
    match = re.search(r'\b(\d+)\b', text)
    if match: return int(match.group(1))
    for word, num in HINDI_NUMBERS.items():
        if re.search(r'\b' + word + r'\b', text): return num
    return 1

def parse_voice_command(text):
    text = text.lower().strip()
    results = []
    parts = re.split(r'\b(aur|and|,|tatha)\b', text)
    for part in parts:
        part = part.strip()
        if not part or part in ('aur','and','tatha',','): continue
        fillers = ['add karo','chahiye','lena hai','lao','mangwao','cart mein','cart me','dalo','please','zara','kilo','kg','gram','litre','liter','packet','bottle','box','piece','pcs','pack','nos']
        clean = part
        for f in fillers: clean = re.sub(r'\b' + re.escape(f) + r'\b', '', clean)
        clean = clean.strip()
        qty = extract_quantity(part)
        for word in HINDI_NUMBERS: clean = re.sub(r'\b' + word + r'\b', '', clean)
        clean = re.sub(r'\b\d+\b', '', clean).strip()
        if not clean: continue
        search_term = clean
        for hindi, english in HINDI_ALIASES.items():
            if re.search(r'\b' + hindi + r'\b', clean): search_term = english; break
        results.append({'original': part.strip(), 'product_name': search_term.strip(), 'quantity': qty})
    return results

def search_products_for_voice(product_name, limit=3):
    if not product_name: return []
    words = product_name.split()
    
    # First try exact name match
    exact = Product.objects.filter(
        name__icontains=product_name, is_active=True
    ).prefetch_related("variants").distinct()[:limit]
    
    if exact.exists():
        result = []
        for p in exact:
            variant = p.default_variant
            if variant:
                result.append({"id": str(p.id), "name": p.name, "variant_id": variant.id, "variant_name": variant.name, "price": float(variant.price), "image": p.display_image or "", "category": p.category.name})
        if result: return result
    
    # Then try tags and brand
    q = Q()
    for word in words:
        if len(word) > 2:
            q |= Q(name__icontains=word)
            q |= Q(tags__icontains=word)
            q |= Q(brand__name__icontains=word)
    
    products = Product.objects.filter(q, is_active=True).prefetch_related("variants").distinct()[:limit]
    result = []
    for p in products:
        variant = p.default_variant
        if variant:
            result.append({"id": str(p.id), "name": p.name, "variant_id": variant.id, "variant_name": variant.name, "price": float(variant.price), "image": p.display_image or "", "category": p.category.name})
    return result

@require_POST
def voice_search(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
    except Exception:
        text = request.POST.get('text', '').strip()
    if not text: return JsonResponse({'success': False, 'error': 'No text provided'})
    commands = parse_voice_command(text)
    if not commands: return JsonResponse({'success': False, 'error': 'Samajh nahi aaya. Dobara boliye.', 'original_text': text})
    response_items = []
    for cmd in commands:
        products = search_products_for_voice(cmd['product_name'])
        response_items.append({'query': cmd['original'], 'product_name': cmd['product_name'], 'quantity': cmd['quantity'], 'products': products, 'found': len(products) > 0})
    return JsonResponse({'success': True, 'original_text': text, 'items': response_items})

@require_POST
def voice_add_to_cart(request):
    try:
        data = json.loads(request.body)
        variant_id = data.get('variant_id')
        qty = int(data.get('quantity', 1))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid data'})
    variant = get_object_or_404(ProductVariant, id=variant_id, is_active=True)
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, defaults={'quantity': 0, 'saved_for_later': False})
    item.saved_for_later = False
    item.quantity += qty
    item.save()
    return JsonResponse({'success': True, 'message': f'{variant.product.name} cart mein add ho gaya!', 'count': cart.get_count(), 'product_name': variant.product.name, 'quantity': item.quantity})

