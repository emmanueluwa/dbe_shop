from decimal import Decimal
from django.conf import settings
from shop.models import Product

class Cart:
    def __init__(self, request):
        #initialise the cart, making session accessibale to other methods in this class
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            #save empty cart in session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    

    ##iterating through items in cart and accessing the related product instances
    def __iter__(self):
        #get products from db
        product_ids = self.cart.keys()
        #retrieve product objects for cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            #returns generator object
            yield item
    

    #number of items in cart
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
      

    def add(self, product, quantity=1, override_quantity=False):
        #convert to json friendly string key name
        product_id = str(product.id)
        if product_id not in self.cart:
            #price turned to string to serialize it
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()


    def save(self):
        #marking session as modified ensures it gets saved
        self.session.modified = True 

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    #clear session, remove cart from session
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
