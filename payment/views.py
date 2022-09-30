from django.shortcuts import render, redirect, reverse, get_object_or_404
from decimal import Decimal
import stripe
from django.conf import settings
from orders.models import Order

#creating stripe instance
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        #stripe data for checkout session
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        #order items(line_items) for checkout session
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                  #charged in lowest currency unit
                  'unit_amount': int(item.price * Decimal('100')),
                  'currency': 'gbp',
                  'product_data': {
                      'name': item.product.name,
                  },
                },
                'quantity': item.quantity,
            })
        #stripe voucher
        if order.voucher:
            stripe_voucher = stripe.Coupon.create(
                    name = order.voucher.code,
                    percent_off = order.discount,
                    duration = 'once'
            )
            #linking the voucher to the checkout session
            session_data['discounts'] = [{
                    'coupon': stripe_voucher.id
            }]

        session = stripe.checkout.Session.create(**session_data)
        #status code 303 recommended to redirect apps to new uri after http POST
        return redirect(session.url, code=303)
    else:
        #locals() returns dict
        return render(request, 'payment/process.html', locals())


def payment_completed(request):
    return render(request, 'payment/completed.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')
