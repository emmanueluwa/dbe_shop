from .cart import Cart

#make cart accessable to every template
def cart(request):
    return {'cart': Cart(request)}
