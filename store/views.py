from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Brand, Review, Banner, Coupon, Wishlist, ProductVariant

def home(request):
    categories = Category.objects.filter(is_active=True, parent=None)[:12]
    featured = Product.objects.filter(is_active=True, is_featured=True).prefetch_related('variants')[:8]
    flash_sale = Product.objects.filter(is_active=True, is_flash_sale=True).prefetch_related('variants')[:6]
    banners = Banner.objects.filter(is_active=True)[:3]
    trending = Product.objects.filter(is_active=True).order_by('-total_sold').prefetch_related('variants')[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at').prefetch_related('variants')[:8]
    return render(request, 'store/home.html', {
        'categories': categories, 'featured': featured, 'flash_sale': flash_sale,
        'banners': banners, 'trending': trending, 'new_arrivals': new_arrivals,
    })

def product_list(request):
    products = Product.objects.filter(is_active=True).prefetch_related('variants').select_related('category','brand')
    categories = Category.objects.filter(is_active=True, parent=None)
    brands = Brand.objects.filter(is_active=True)
    cat_slug = request.GET.get('category','')
    brand_slug = request.GET.get('brand','')
    min_price = request.GET.get('min_price','')
    max_price = request.GET.get('max_price','')
    min_rating = request.GET.get('min_rating','')
    sort = request.GET.get('sort','')
    q = request.GET.get('q','')
    if cat_slug: products = products.filter(category__slug=cat_slug)
    if brand_slug: products = products.filter(brand__slug=brand_slug)
    if min_price: products = products.filter(variants__price__gte=float(min_price))
    if max_price: products = products.filter(variants__price__lte=float(max_price))
    if min_rating: products = products.filter(average_rating__gte=float(min_rating))
    if q: products = products.filter(Q(name__icontains=q)|Q(description__icontains=q)|Q(brand__name__icontains=q))
    sort_map = {
        'price_asc': 'variants__price', 'price_desc': '-variants__price',
        'rating': '-average_rating', 'newest': '-created_at', 'popular': '-total_sold',
    }
    if sort and sort in sort_map: products = products.order_by(sort_map[sort])
    products = products.distinct()
    active_cat = Category.objects.filter(slug=cat_slug).first() if cat_slug else None
    return render(request, 'store/product_list.html', {
        'products': products, 'categories': categories, 'brands': brands,
        'active_cat': active_cat, 'active_brand': brand_slug, 'q': q,
        'min_price': min_price, 'max_price': max_price, 'sort': sort, 'min_rating': min_rating,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variants = product.variants.filter(is_active=True)
    reviews = product.reviews.all()[:10]
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:6]
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    rating_dist = {}
    for i in range(1,6):
        rating_dist[i] = reviews.filter(rating=i).count() if reviews else 0
    return render(request, 'store/product_detail.html', {
        'product': product, 'variants': variants, 'reviews': reviews,
        'related': related, 'in_wishlist': in_wishlist, 'rating_dist': rating_dist,
    })

@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        title = request.POST.get('title','')
        body = request.POST.get('body','')
        if body:
            Review.objects.update_or_create(
                product=product, user=request.user,
                defaults={'rating':rating,'title':title,'body':body}
            )
            avg = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.average_rating = avg or 0
            product.total_reviews = Review.objects.filter(product=product).count()
            product.save()
            messages.success(request, 'Review submitted!')
        return redirect('store:product_detail', slug=slug)

def search(request):
    q = request.GET.get('q','')
    results = []
    if q:
        results = Product.objects.filter(
            Q(name__icontains=q)|Q(description__icontains=q)|Q(brand__name__icontains=q),
            is_active=True
        ).prefetch_related('variants')[:20]
    return render(request, 'store/search.html', {'results': results, 'q': q})

def search_autocomplete(request):
    q = request.GET.get('q','')
    if len(q) < 2: return JsonResponse({'results':[]})
    products = Product.objects.filter(name__icontains=q, is_active=True).values('name','slug','id')[:8]
    cats = Category.objects.filter(name__icontains=q).values('name','slug')[:3]
    return JsonResponse({
        'results': list(products),
        'categories': list(cats),
    })

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True).prefetch_related('variants')
    subcategories = category.subcategories.filter(is_active=True)
    return render(request, 'store/category.html', {
        'category': category, 'products': products, 'subcategories': subcategories
    })

def all_categories(request):
    categories = Category.objects.filter(is_active=True, parent=None)
    return render(request, 'store/categories.html', {'categories': categories})
