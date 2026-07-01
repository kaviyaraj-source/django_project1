from django.shortcuts import render,redirect
from .form import CustomUserForm
from django.http import HttpResponse
from . models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import json
from django.http import JsonResponse



# Create your views here.
def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,"shop/home.html",{"products":products})

def favviewpage(request):
    if request.user.is_authenticated:
        fav=favourite.objects.filter(user=request.user)
        return render(request,"shop/fav.html",{"fav":fav})
    else:
        return redirect("/")
    
def remove_fav(request,fid):
    item=favourite.objects.get(id=fid)
    item.delete()
    return redirect("/favviewpage")




def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,"shop/cart.html",{"cart":cart})
    else:
        return redirect("/")
    
    
def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart")

def fav_page(request):
    if request.headers.get('X-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            product_id=data['pid']
            #print(data['request.user.id'])
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if favourite.objects.filter(user=request.user.id,product_id=product_id):
                    return JsonResponse({'status':'Product Alreay in favourite'},status=200)
                else:
                    favourite.objects.create(user=request.user,product_id=product_id)
                    return JsonResponse({'status':'Product Add to Favourite'},status=200)
            else:
                return JsonResponse({'status':'Login to Add favourite'},status=200)
        else:
            return JsonResponse({'status':'Login to Add favourite'},status=200)
    else:
        return JsonResponse({'status':'Invalid Access'},status=200)




def add_to_cart(request):
    #print("the fun called")
    if request.headers.get('X-requested-with')=='XMLHttpRequest':
        #print("the first if called")
        if request.user.is_authenticated:
            #print("the second if called")
            data=json.load(request)
            product_qty=data['product_qty']
            product_id=data['pid']
            #print(request.user.id)
            product_status=Product.objects.get(id=product_id)
            if product_status:
                #print("the product_status if called")
                if Cart.objects.filter(user=request.user,product_id=product_id):
                    #print("the product_status if called")
                    return JsonResponse({'status':'Product Alreay in Cart'},status=200)
                else:
                    #print("the product_status else called")
                    if product_status.quantity>=product_qty:
                        Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                        #print("the product_status if called")
                        return JsonResponse({'status':'product Added to Cart'},status=200)
                    else:
                        return JsonResponse({'status':'Product Stock Not Available'},status=200)
            else:
                return JsonResponse({'status':'Login to Add Cart'},status=200)
        else:
            return JsonResponse({'status':'Login to Add Cart'},status=200)
    else:
        #print("the else executed")
        return JsonResponse({'status':'Invalid Access'},status=200)

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out Successfully")
        return redirect("/")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=="POST":
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully")
                return redirect("/")
            else:
                messages.error(request,"Invalid User Name Or Password")
                return redirect("/login")
        return render(request,"shop/login.html")

def register(request):
    form=CustomUserForm()
    if request.method=="POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Success You Can Login Now..!")
            return redirect('/login')
    return render(request,"shop/register.html",{'form':form})

def collections(request):
    category=Category.objects.filter(status=0)
    return render(request,"shop/collections.html",{"category":category})

def collectionsview(request,name):
    if(Category.objects.filter(name=name,status=0)):
        #products=Product.objects.filter(Category__name=name)
        products = Product.objects.filter(category__name=name)
        return render(request,"shop/products/index.html",{"products":products,"category_name":name})
    else:
        messages.warning(request,"No Such Category Found")
        return redirect('collections')


def product_details(request,cname,pname):
    if(Category.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request,"shop/products/product_details.html",{"products":products})
        else:
            messages.error(request,"No Such Products Found")
            return redirect('collections')
    else:
        messages.error(request,"No Such Categorys Found")
        return redirect('collections')
