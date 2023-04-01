from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import User, Product, Cart, CartItem
from django.db import IntegrityError

def home(request):
    products = Product.objects.all()
    

    if request.method == "GET":
        if request.user.is_authenticated:
            user = request.user
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            return render(request, "authuser/home.html", {"products":products, "users_items":users_items})
        else:
            return render(request, "authuser/home.html", {"products":products})
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            print('found user')
            login(request, user)
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            return render(request, "authuser/home.html", {"products":products, "users_items":users_items})
        else:
            return render(request, "authuser/home.html", {"message":"couldn't find user account", "products":products})
        

def logoutview(request):
    if request.method == "POST":
        logout(request)
        return render(request, "authuser/logout.html")
    
def createaccount(request):
    if request.method == "GET":
        return render(request, "authuser/createaccount.html")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password!=confirm_password:
            return render(request, "authuser/createaccount.html", {"message":"passwords don't match"})
        try:
            user = User.objects.create_user(email, password)
            user.save()
            cart = Cart.objects.create(owner=user)
            cart.save()
        except IntegrityError:
            return render(request, "authuser/createaccount.html", {"message":"email in use"})
        login(request, user)
        products = Product.objects.all()
        return render(request, "authuser/home.html", {"products":products})
    
def productview(request, id):
    if request.method=="GET":
        product = Product.objects.get(id=id)
        if request.user.is_authenticated:
            user = request.user
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            return render(request, "authuser/productview.html", {"product": product, "users_items":users_items})
        else:
            return render(request, "authuser/productview.html",{"product": product})
    if request.method=="POST":
        form_message = "Please enter a valid size and quantity."
        user = request.user
        users_cart = Cart.objects.get(owner=user)
        users_items = CartItem.objects.filter(cart=users_cart)
        product = Product.objects.get(id=id)
        quantity = request.POST["quantity"]
        size = request.POST["size"]
        cart = Cart.objects.get(owner=request.user)
        product = Product.objects.get(id=id)
        if (quantity!='q' and size!='Size'):
            quantity = int(quantity)
            if(quantity>0 and quantity<10):
                cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity, size=size)
                form_message = 'This item was added to your cart successfully.'
            else:
                return render(request, "authuser/productview.html",{"product": product, "users_items":users_items})
        else:
            return render(request, "authuser/productview.html",{"product": product, "users_items":users_items, "form_message":form_message})
        return render(request, "authuser/productview.html",{"product": product, "users_items":users_items, "form_message":form_message})


def checkout(request):
    if request.method=="GET":
        if request.user.is_authenticated:
            user = request.user
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            return render(request, "authuser/checkout.html", {"users_items":users_items})
        else:
            message = "Plesae log in or register to access the checkout" 
            return render(request, "authuser/checkout.html", {"message": message})
    if request.method=="POST":
        if request.user.is_authenticated:
            user = request.user
            users_cart = Cart.objects.get(owner=user)
            item_to_edit = request.POST["item_to_edit"]
            new_quantity = request.POST["new_quantity"]
            cartItemToChange = CartItem.objects.get(cart=users_cart, id=item_to_edit)
            if new_quantity=="0":
                cartItemToChange.delete()
            elif new_quantity != "q":
                cartItemToChange.quantity = new_quantity
                cartItemToChange.save()
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            return render(request, "authuser/checkout.html", {"users_items":users_items})