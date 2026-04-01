from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User, Address
from .forms import RegisterForm, LoginForm, AddressForm, ProfileForm

def register_view(request):
    if request.user.is_authenticated: return redirect('/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to QuickMart, {user.first_name}! 🎉')
            return redirect(request.POST.get('next','/'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated: return redirect('/')
    if request.method == 'POST':
        email = request.POST.get('email','')
        password = request.POST.get('password','')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}! 👋')
            return redirect(request.POST.get('next','/'))
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'users/login.html', {'next': request.GET.get('next','/')})

def logout_view(request):
    logout(request)
    messages.info(request, 'Signed out successfully')
    return redirect('/')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    addresses = request.user.addresses.all()
    return render(request, 'users/profile.html', {'form': form, 'addresses': addresses})

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            if addr.is_default:
                request.user.addresses.update(is_default=False)
            addr.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': addr.id, 'label': addr.label,
                    'address': f"{addr.address_line1}, {addr.city}", 'full_name': addr.full_name})
            messages.success(request, 'Address added!')
            return redirect(request.POST.get('next','users:profile'))
    else:
        form = AddressForm()
    return render(request, 'users/address_form.html', {'form': form, 'action': 'Add'})

@login_required
def edit_address(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=addr)
        if form.is_valid():
            if form.cleaned_data.get('is_default'):
                request.user.addresses.exclude(pk=pk).update(is_default=False)
            form.save()
            messages.success(request, 'Address updated!')
            return redirect('users:profile')
    else:
        form = AddressForm(instance=addr)
    return render(request, 'users/address_form.html', {'form': form, 'action': 'Edit'})

@login_required
def delete_address(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    addr.delete()
    messages.success(request, 'Address removed')
    return redirect('users:profile')

@login_required
def wishlist_view(request):
    from store.models import Wishlist
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'users/wishlist.html', {'items': items})

@login_required
def toggle_wishlist(request, product_id):
    from store.models import Wishlist, Product
    product = get_object_or_404(Product, id=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'removed', 'message': 'Removed from wishlist'})
    return JsonResponse({'status': 'added', 'message': 'Added to wishlist ❤️'})

@login_required
def spin_wheel(request):
    if request.method == 'POST':
        import random
        cost = 50
        if request.user.reward_coins < cost:
            return JsonResponse({'success': False, 'message': 'Not enough coins!'})
        prizes = [
            {'label': '10% OFF', 'type': 'discount', 'value': 10},
            {'label': '₹50 Cashback', 'type': 'coins', 'value': 100},
            {'label': 'Free Delivery', 'type': 'free_delivery', 'value': 1},
            {'label': 'Try Again', 'type': 'none', 'value': 0},
            {'label': '20% OFF', 'type': 'discount', 'value': 20},
            {'label': '100 Coins', 'type': 'coins', 'value': 100},
            {'label': '₹30 Back', 'type': 'coins', 'value': 60},
            {'label': 'Try Again', 'type': 'none', 'value': 0},
        ]
        prize = random.choice(prizes)
        request.user.reward_coins -= cost
        if prize['type'] == 'coins':
            request.user.reward_coins += prize['value']
        request.user.save()
        return JsonResponse({'success': True, 'prize': prize, 'coins': request.user.reward_coins})
    return render(request, 'users/spin.html')
