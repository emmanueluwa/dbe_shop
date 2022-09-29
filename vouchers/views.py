from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Voucher
from .forms import VoucherApplyForm

@require_POST
def voucher_apply(request):
    now = timezone.now()
    form = VoucherApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            voucher = Voucher.objects.get(
                        #checking for case insensitive exact match
                        code__iexact = code, 
                        #less than equal to
                        valid_from__lte = now,
                        #greater than equal to
                        valid_to__gte = now,
                        active = True
                        )
            #store voucher id in user session
            request.session['voucher_id'] = voucher.id
        except Voucher.DoesNotExist:
            request.session['voucher_id'] = None
    
    return redirect('cart:cart_detail')
