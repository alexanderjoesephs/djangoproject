from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import User, Product, Cart, CartItem, PastOrder, OrderItem, Review
from django.db import IntegrityError
import json
from django.views.decorators.csrf import csrf_exempt


def home(request):
    products = Product.objects.all()
    intro = True

    if request.method == "GET":
        if request.user.is_authenticated:
            user = request.user
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            return render(request, "authuser/home.html", {"products":products, "users_items":users_items, "intro":intro})
        else:
            return render(request, "authuser/home.html", {"products":products, "intro":intro})
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            
            login(request, user)
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            return render(request, "authuser/home.html", {"products":products, "users_items":users_items, "intro":intro})
        else:
            return render(request, "authuser/home.html", {"message":"couldn't find user account", "products":products, "intro":intro})
        

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
        name = request.POST["username"]
        if password!=confirm_password:
            return render(request, "authuser/createaccount.html", {"message":"passwords don't match"})
        try:
            user = User.objects.create_user(email, password)
            user.name = name
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
            #get reviews and create array to render stars
            reviews = Review.objects.filter(product=product)
            stars = "<span class='one fa fa-star checked'></span>"
            """for review in reviews:
                num = int(review.rating)
                print(num)
                s = []
                for i in range(num):
                    s.append('checked')
                for i in range(5-num):
                    s.append('unchecked')
                stars.append(s)
            print(stars)"""
            return render(request, "authuser/productview.html", {"product": product, "users_items":users_items, "reviews":reviews,"stars":stars})
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
            
            total_cost = 0
            for item in users_items:
                price = item.product.price * item.quantity
                total_cost = price + total_cost
            
            return render(request, "authuser/checkout.html", {"users_items":users_items,"total_cost":total_cost})
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
            total_cost = 0
            for item in users_items:
                price = item.product.price * item.quantity
                total_cost = price + total_cost
            return render(request, "authuser/checkout.html", {"users_items":users_items,"total_cost":total_cost})
        


def your_orders(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            pastOrder = PastOrder.objects.create(ordered_by=user)
            pastOrder.save()
            for item in users_items:
                orderItem = OrderItem.objects.create(pastOrder=pastOrder, product=item.product, quantity=item.quantity, size=item.size, ordered_at=pastOrder.ordered_at)
                orderItem.save()
            users_items = CartItem.objects.filter(cart=users_cart).delete()
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            return render(request, "authuser/message_about_project.html", {"users_items":users_items})
        
    if request.method == "GET":
        user = request.user
        users_cart = Cart.objects.get(owner=user)
        users_items = CartItem.objects.filter(cart=users_cart)
        pastOrders = PastOrder.objects.filter(ordered_by=user)
        pastOrderItems = OrderItem.objects.filter(pastOrder__in=pastOrders).order_by('-ordered_at')
        users_reviews= Review.objects.filter(author=user)
        products_reviewed = []
        for review in users_reviews:
            products_reviewed.append(review.product)
        
        return render(request, "authuser/your_orders.html", {"users_items":users_items, "pastOrderItems": pastOrderItems, "user":user, "products_reviewed": products_reviewed})
    
def leaguerange(request, league):
    if league=='All':
        products = Product.objects.all()
    else:
        products = Product.objects.filter(league=league)
    if request.method == "GET":
        if request.user.is_authenticated:
            user = request.user
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            return render(request, "authuser/home.html", {"products":products, "users_items":users_items})
        else:
            return render(request, "authuser/home.html", {"products":products})
        

def timerange(request):
    if request.method == "POST":
        fromyear = request.POST["fromyear"]
        toyear = request.POST["toyear"]
        products = Product.objects.filter(year__gte=fromyear).filter(year__lte=toyear)
        if request.user.is_authenticated:
            user = request.user
            users_cart = Cart.objects.get(owner=user)
            users_items = CartItem.objects.filter(cart=users_cart)
            
            return render(request, "authuser/home.html", {"products":products, "users_items":users_items})
        else:
            return render(request, "authuser/home.html", {"products":products})
        

def review(request):
    if request.method=="PUT":
        data = json.loads(request.body)
        content = data['content']
        productid = data['productid']
        rating = data['rating']
        user = data['user']
        author = User.objects.get(email=user)
        product = Product.objects.get(pk=productid)
        review = Review.objects.create(author=author, content=content, product=product, rating=rating)
        review.save()
        return HttpResponse(status=204)
    