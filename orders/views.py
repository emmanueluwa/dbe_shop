from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
import os
os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.voucher:
                order.voucher = cart.voucher
                order.discount = cart.voucher.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order = order,
                    product = item['product'],
                    price = item['price'],
                    quantity = item['quantity']
                )
            cart.clear()
            #add async task to message queue, for celery worker
            order_created.delay(order.id)
            #store oder id in user session
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})

#check if is_active and is_staff == True
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    #saving rendered html
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    #response header, specifying file name
    response['Content-Desposition'] = f'filename=order_{order.id}.pdf'

    #write generated pdf to HttpResponse object
    weasyprint.HTML(string=html).write_pdf(
                                    response, 
                                    stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
                                    )
    return response
