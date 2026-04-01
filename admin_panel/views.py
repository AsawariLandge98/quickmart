from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from store.models import Product, Category, Brand, ProductVariant, Coupon, Banner
from orders.models import Order, OrderItem
from users.models import User
from store.models import Review

def admin_required(view_func):
    decorated = staff_member_required(view_func, login_url='/users/login/')
    return decorated

@admin_required
def dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    today_orders = Order.objects.filter(placed_at__date=today)
    today_revenue = today_orders.aggregate(s=Sum('total_amount'))['s'] or 0
    today_count = today_orders.count()
    month_orders = Order.objects.filter(placed_at__date__gte=month_ago)
    month_revenue = month_orders.aggregate(s=Sum('total_amount'))['s'] or 0
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    total_products = Product.objects.count()
    active_orders = Order.objects.filter(status__in=['pending','confirmed','picking','packed','dispatched','out_for_delivery']).count()
    weekly_data = []
    for i in range(6,-1,-1):
        d = today - timedelta(days=i)
        rev = Order.objects.filter(placed_at__date=d).aggregate(s=Sum('total_amount'))['s'] or 0
        cnt = Order.objects.filter(placed_at__date=d).count()
        weekly_data.append({'date': d.strftime('%a'), 'revenue': float(rev), 'orders': cnt})
    recent_orders = Order.objects.select_related('user').prefetch_related('items')[:10]
    top_products = OrderItem.objects.values('product_name').annotate(
        total_qty=Sum('quantity'), total_rev=Sum('total_price')
    ).order_by('-total_qty')[:5]
    low_stock = ProductVariant.objects.filter(stock__lte=10, is_active=True).select_related('product')[:10]
    return render(request, 'admin_panel/dashboard.html', {
        'today_revenue': today_revenue, 'today_count': today_count,
        'month_revenue': month_revenue, 'total_users': total_users,
        'new_users_today': new_users_today, 'total_products': total_products,
        'active_orders': active_orders, 'weekly_data': weekly_data,
        'recent_orders': recent_orders, 'top_products': top_products,
        'low_stock': low_stock,
    })

@admin_required
def products(request):
    q = request.GET.get('q','')
    cat = request.GET.get('category','')
    prods = Product.objects.select_related('category','brand').prefetch_related('variants')
    if q: prods = prods.filter(name__icontains=q)
    if cat: prods = prods.filter(category__slug=cat)
    prods = prods.order_by('-created_at')
    categories = Category.objects.filter(is_active=True)
    return render(request, 'admin_panel/products.html', {'products': prods, 'categories': categories, 'q': q, 'active_cat': cat})

@admin_required
def product_add(request):
    from store.forms import ProductForm, ProductVariantFormSet
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand') or None
        description = request.POST.get('description','')
        short_description = request.POST.get('short_description','')
        sku = request.POST.get('sku')
        image_url = request.POST.get('image_url','')
        is_featured = 'is_featured' in request.POST
        is_flash_sale = 'is_flash_sale' in request.POST
        from django.utils.text import slugify
        import uuid as _uuid
        slug = slugify(name)
        if Product.objects.filter(slug=slug).exists():
            slug = f"{slug}-{str(_uuid.uuid4())[:8]}"
        product = Product.objects.create(
            name=name, slug=slug, category_id=category_id, brand_id=brand_id,
            description=description, short_description=short_description,
            sku=sku or f"SKU-{str(_uuid.uuid4())[:8]}", image_url=image_url,
            is_featured=is_featured, is_flash_sale=is_flash_sale,
        )
        if request.FILES.get('image'):
            product.image = request.FILES['image']
            product.save()
        # variants
        v_names = request.POST.getlist('variant_name[]')
        v_prices = request.POST.getlist('variant_price[]')
        v_mrps = request.POST.getlist('variant_mrp[]')
        v_stocks = request.POST.getlist('variant_stock[]')
        for i, vn in enumerate(v_names):
            if vn and v_prices[i]:
                ProductVariant.objects.create(
                    product=product, name=vn,
                    sku=f"{product.sku}-{i+1}",
                    price=v_prices[i], mrp=v_mrps[i] if v_mrps[i] else v_prices[i],
                    stock=v_stocks[i] if v_stocks[i] else 100,
                )
        messages.success(request, f'Product "{name}" added!')
        return redirect('admin_panel:products')
    return render(request, 'admin_panel/product_form.html', {'categories': categories, 'brands': brands, 'action': 'Add'})

@admin_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    variants = product.variants.all()
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.category_id = request.POST.get('category', product.category_id)
        product.brand_id = request.POST.get('brand') or None
        product.description = request.POST.get('description','')
        product.short_description = request.POST.get('short_description','')
        product.image_url = request.POST.get('image_url','')
        product.is_featured = 'is_featured' in request.POST
        product.is_flash_sale = 'is_flash_sale' in request.POST
        product.is_active = 'is_active' in request.POST
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated!')
        return redirect('admin_panel:products')
    return render(request, 'admin_panel/product_form.html', {
        'product': product, 'categories': categories, 'brands': brands,
        'variants': variants, 'action': 'Edit'
    })

@admin_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = False
    product.save()
    messages.success(request, f'Product "{product.name}" deactivated')
    return redirect('admin_panel:products')

@admin_required
def orders_list(request):
    status = request.GET.get('status','')
    orders = Order.objects.select_related('user','delivery_address').prefetch_related('items')
    if status: orders = orders.filter(status=status)
    return render(request, 'admin_panel/orders.html', {'orders': orders, 'status_filter': status,
        'status_choices': Order.STATUS_CHOICES})

@admin_required
def order_detail(request, order_id):
    order = Order.objects.prefetch_related('items','history').select_related('user','delivery_address').get(id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        note = request.POST.get('note','')
        if new_status:
            order.status = new_status
            order.save()
            from orders.models import OrderStatusHistory
            OrderStatusHistory.objects.create(order=order, status=new_status, note=note)
            messages.success(request, f'Order status updated to {new_status}')
        return redirect('admin_panel:order_detail', order_id=order_id)
    return render(request, 'admin_panel/order_detail.html', {'order': order,
        'status_choices': Order.STATUS_CHOICES})

@admin_required
def users_list(request):
    q = request.GET.get('q','')
    users = User.objects.all().order_by('-date_joined')
    if q: users = users.filter(email__icontains=q) | users.filter(full_name__icontains=q)
    return render(request, 'admin_panel/users.html', {'users': users, 'q': q})

@admin_required
def user_detail(request, user_id):
    u = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=u)[:10]
    return render(request, 'admin_panel/user_detail.html', {'u': u, 'orders': orders})

@admin_required
def toggle_user_active(request, user_id):
    u = get_object_or_404(User, id=user_id)
    u.is_active = not u.is_active
    u.save()
    return JsonResponse({'active': u.is_active})

@admin_required
def inventory(request):
    variants = ProductVariant.objects.select_related('product').order_by('stock')
    return render(request, 'admin_panel/inventory.html', {'variants': variants})

@admin_required
def update_stock(request, variant_id):
    if request.method == 'POST':
        v = get_object_or_404(ProductVariant, id=variant_id)
        v.stock = int(request.POST.get('stock', v.stock))
        v.save()
        return JsonResponse({'success': True, 'stock': v.stock})
    return JsonResponse({'success': False})

@admin_required
def analytics(request):
    today = timezone.now().date()
    monthly_data = []
    for i in range(11,-1,-1):
        d = today.replace(day=1) - timedelta(days=i*30)
        rev = Order.objects.filter(placed_at__year=d.year, placed_at__month=d.month).aggregate(s=Sum('total_amount'))['s'] or 0
        cnt = Order.objects.filter(placed_at__year=d.year, placed_at__month=d.month).count()
        monthly_data.append({'month': d.strftime('%b'), 'revenue': float(rev), 'orders': cnt})
    cat_sales = OrderItem.objects.values('variant__product__category__name').annotate(
        total=Sum('total_price')).order_by('-total')[:6]
    return render(request, 'admin_panel/analytics.html', {
        'monthly_data': monthly_data, 'cat_sales': list(cat_sales)
    })

@admin_required
def coupons(request):
    coupons = Coupon.objects.all().order_by('-valid_until')
    return render(request, 'admin_panel/coupons.html', {'coupons': coupons})

@admin_required
def coupon_add(request):
    if request.method == 'POST':
        from django.utils.dateparse import parse_datetime
        Coupon.objects.create(
            code=request.POST['code'].upper(),
            description=request.POST['description'],
            discount_type=request.POST['discount_type'],
            discount_value=request.POST['discount_value'],
            min_order_amount=request.POST.get('min_order_amount',0),
            valid_from=parse_datetime(request.POST['valid_from']) or timezone.now(),
            valid_until=parse_datetime(request.POST['valid_until']) or timezone.now()+timedelta(days=30),
        )
        messages.success(request, 'Coupon created!')
        return redirect('admin_panel:coupons')
    return render(request, 'admin_panel/coupon_form.html')

@admin_required
def categories_manage(request):
    cats = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon','🛒')
        from django.utils.text import slugify
        Category.objects.create(name=name, slug=slugify(name), icon=icon)
        messages.success(request, 'Category added!')
        return redirect('admin_panel:categories')
    return render(request, 'admin_panel/categories.html', {'categories': cats})

@admin_required
def reviews_list(request):
    reviews = Review.objects.select_related('product','user').order_by('-created_at')
    return render(request, 'admin_panel/reviews.html', {'reviews': reviews})

@admin_required
def delete_review(request, review_id):
    r = get_object_or_404(Review, id=review_id)
    r.delete()
    messages.success(request, 'Review deleted')
    return redirect('admin_panel:reviews')

@admin_required
def banners_manage(request):
    banners = Banner.objects.all()
    if request.method == 'POST':
        Banner.objects.create(
            title=request.POST['title'],
            subtitle=request.POST.get('subtitle',''),
            emoji=request.POST.get('emoji',''),
            link_url=request.POST.get('link_url',''),
            button_text=request.POST.get('button_text','Shop Now'),
            bg_color=request.POST.get('bg_color','linear-gradient(135deg,#1a1a2e,#16213e)'),
        )
        messages.success(request, 'Banner added!')
        return redirect('admin_panel:banners')
    return render(request, 'admin_panel/banners.html', {'banners': banners})
