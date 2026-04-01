from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from orders.models import Order

@login_required
def track_live(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'delivery/live_track.html', {'order': order})

def get_eta(request):
    return JsonResponse({'eta_minutes': 10, 'status': 'on_the_way'})
