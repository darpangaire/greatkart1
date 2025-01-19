from django.shortcuts import render
from store.models import Product
from carts.models import Cart,CartItem
from django.shortcuts import redirect,get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from store.models import Variation
from django.contrib.auth.decorators import login_required


# Create your views here.
def _cart_id(request):
  cart = request.session.session_key
  if not cart:
    cart = request.session.create()
  return cart


def remove_cart(request,product_id):
  cart = Cart.objects.get(cart_id = _cart_id(request))
  product = get_object_or_404(Product,id = product_id)
  cart_item = CartItem.objects.get(cart=cart,product = product)
  if cart_item.quantity > 1:
    cart_item.quantity -= 1
    cart_item.save()
  else:
    cart_item.delete()
  return redirect('cart')

def remove_cart_item(request,product_id):
  cart = Cart.objects.get(cart_id = _cart_id(request))
  product = get_object_or_404(Product,id = product_id)
  cart_item = CartItem.objects.get(cart=cart,product = product)
  cart_item.delete()
  return redirect('cart')

  


def add_cart(request, product_id, color=None, size=None):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    # Get or create cart
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    # Check for existing cart items
    cart_items = CartItem.objects.filter(product=product, cart=cart)
    if cart_items.exists():
        for item in cart_items:
            existing_variations = list(item.variations.all())
            if product_variation == existing_variations:
                item.quantity += 1
                item.save()
                break
        else:
            # If no matching variation, create a new cart item
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )
            if product_variation:
                cart_item.variations.set(product_variation)
            cart_item.save()
    else:
        # If no cart item exists, create a new one
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
        if product_variation:
            cart_item.variations.set(product_variation)
        cart_item.save()

    return redirect('cart')

    

def cart(request,total = 0,quantity=0,cart_items=None):
  tax= 0
  grand_total = 0
  try:
    if request.user.is_authenticated:
      cart_items = CartItem.objects.filter(user=request.user,is_active = True)
      
    else:
      cart = Cart.objects.get(cart_id = _cart_id(request))
      cart_items = CartItem.objects.filter(cart = cart,is_active = True)
    for cart_item in cart_items:
      total += (cart_item.product.price * cart_item.quantity)
      quantity += cart_item.quantity
      
    tax = (2*total)/100
    grand_total = total + tax  
    
    
  except ObjectDoesNotExist:
    pass
  
  context = {
    'total':total,
    'quantity':quantity,
    'cart_items':cart_items,
    'tax':tax,
    'grand_total':grand_total
    
  }
  return render(request,'store/cart.html',context)



@login_required(login_url = 'login')
def checkout(request,total = 0,quantity=0,cart_items=None):
  tax= 0
  grand_total = 0
  try:
    cart = Cart.objects.get(cart_id = _cart_id(request))
    cart_items = CartItem.objects.filter(cart = cart,is_active = True)
    for cart_item in cart_items:
      total += (cart_item.product.price * cart_item.quantity)
      quantity += cart_item.quantity
      
    tax = (2*total)/100
    grand_total = total + tax  
    
    
  except ObjectDoesNotExist:
    pass
  
  context = {
    'total':total,
    'quantity':quantity,
    'cart_items':cart_items,
    'tax':tax,
    'grand_total':grand_total
    
  }
  return render(request,'store/checkout.html',context)





  
