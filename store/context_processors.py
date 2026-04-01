from .models import Category

def store_context(request):
    return {
        'nav_categories': Category.objects.filter(is_active=True, parent=None).order_by('sort_order')[:8],
    }
