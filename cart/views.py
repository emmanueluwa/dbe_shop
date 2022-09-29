from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from vouchers.forms import VoucherApplyForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        clean_data = form.cleaned_data
        cart.add(
            product = product, 
            quantity = clean_data['quantity'],
            override_quantity = clean_data['override']
            )
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
          initial={
            'quantity': item['quantity'],
            'override': True
          })
    voucher_apply_form = VoucherApplyForm()
    return render(
                request, 
                'cart/detail.html', 
                {'cart': cart, 'voucher_apply_form': voucher_apply_form}
    )
