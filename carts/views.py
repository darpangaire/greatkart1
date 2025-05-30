from django.shortcuts import render
from store.models import Product
from carts.models import Cart,CartItem
from django.shortcuts import redirect,get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from store.models import Variation
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


# Create your views here.
def _cart_id(request):
  cart = request.session.session_key
  if not cart:
    cart = request.session.create()
  return cart


def remove_cart(request,product_id,cart_item_id):
  product = get_object_or_404(Product,id = product_id)
  try:
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(user=request.user,product = product,id=cart_item_id)
    else:
      cart = Cart.objects.get(cart_id = _cart_id(request))
      cart_item = CartItem.objects.get(cart=cart,product = product,id=cart_item_id)
    if cart_item.quantity > 1:
      cart_item.quantity -= 1
      cart_item.save()
    else:
      cart_item.delete()
  except:
    pass
  return redirect('cart')



def remove_cart_item(request,product_id,cart_item_id):
  product = get_object_or_404(Product,id = product_id)
  if request.user.is_authenticated:
    cart_item = CartItem.objects.get(user=request.user,product = product,id=cart_item_id)
  else:
    cart = Cart.objects.get(cart_id = _cart_id(request))

    cart_item = CartItem.objects.get(cart=cart,product = product,id=cart_item_id)
  cart_item.delete()
  return redirect('cart')

  


def add_cart(request, product_id, color=None, size=None):
    product = Product.objects.get(id=product_id)
    current_user = request.user
    if current_user.is_authenticated:
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


      # Check for existing cart items
      is_cart_items_exists = CartItem.objects.filter(product=product,user = current_user).exists()
      
      if is_cart_items_exists:
        cart_item = CartItem.objects.filter(product=product,user = current_user)
        #existing variations -> database
        # current variation -> product_variations
        # item id -> database
        ex_var_list = []
        id = []
        for item in cart_item:
          existing_variation = list(item.variations.all().order_by('id'))
          product_variation_sorted = sorted(product_variation,key=lambda x:x.id)
          ex_var_list.append(existing_variation)
          id.append(item.id)
          
        print(ex_var_list)
        
        if product_variation_sorted in ex_var_list:
          # increase the cart items quantity
          index = ex_var_list.index(product_variation_sorted)
          item_id = id[index]
          item = CartItem.objects.get(product=product,id=item_id)
          item.quantity += 1
          item.save()
          
        
        
        else:
          item = CartItem.objects.create(product=product,quantity=1,user = current_user)
          if len(product_variation) > 0:
            item.variations.clear()         
            item.variations.add(*product_variation)
          item.save()
        
      else:
        cart_item = CartItem.objects.create(
          product=product,
          quantity=1,
          user = current_user
          
        )
        if len(product_variation) > 0:
          cart_item.variations.clear()
          cart_item.variations.add(*product_variation)          
        cart_item.save()
        
    # if user is not authenticated
    else:
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
      is_cart_items_exists = CartItem.objects.filter(product=product,cart=cart).exists()
      
      if is_cart_items_exists:
        cart_item = CartItem.objects.filter(product=product,cart=cart)
        #existing variations -> database
        # current variation -> product_variations
        # item id -> database
        ex_var_list = []
        id = []
        for item in cart_item:
          existing_variation = list(item.variations.all().order_by('id'))
          product_variation_sorted = sorted(product_variation,key=lambda x:x.id)
          ex_var_list.append(existing_variation)
          id.append(item.id)
          
        print(ex_var_list)
        
        if product_variation_sorted in ex_var_list:
          # increase the cart items quantity
          index = ex_var_list.index(product_variation_sorted)
          item_id = id[index]
          item = CartItem.objects.get(product=product,id=item_id)
          item.quantity += 1
          item.save()
          
        
        
        else:
          item = CartItem.objects.create(product=product,quantity=1,cart=cart)
          if len(product_variation) > 0:
            item.variations.clear()         
            item.variations.add(*product_variation)
          item.save()
        
      else:
        cart_item = CartItem.objects.create(
          product=product,
          quantity=1,
          cart=cart
          
        )
        if len(product_variation) > 0:
          cart_item.variations.clear()
          cart_item.variations.add(*product_variation)          
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



# @login_required(login_url = 'login')
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
    print(cart_items)
    
  except ObjectDoesNotExist:
    cart_items = []
    
  print(cart_items)
  
  context = {
    'total':total,
    'quantity':quantity,
    'cart_items':cart_items,
    'tax':tax,
    'grand_total':grand_total
    
  }
  return render(request,'store/checkout.html',context)





  
