from io import BytesIO
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order
import weasyprint
import os
os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")

@shared_task
def payment_completed(order_id):
    #send email when payment is successful
    order = Order.objects.get(id=order_id)
    subject = f'Shop - Invoice no. {order.id}'
    message = 'Please, find attached the invoice for your purchase.'
    email = EmailMessage(
              subject,
              message,
              'fulphrone@gmail.com',
              [order.email]
    )

    #generating the pdf
    html = render_to_string('orders/order/pdf.html', {'order':order})
    #manipulate string and bytes data in memory(in memory bytes buffer)
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

    #attach pdf to email
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    email.send()

