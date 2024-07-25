from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Flowers,Favorits,Cart,Category,Subcategory,MyOrders,Transection
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm, SignupForm
from django.contrib.auth.models import User
from django.db.models import OuterRef, Subquery,Exists,When,Value,Case,CharField
from django.http import HttpResponse,HttpResponseBadRequest,JsonResponse
from django.db import models
from django.db.models import F, ExpressionWrapper, DecimalField,Sum,Q
from decimal import Decimal
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import FileSystemStorage
import requests
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import jsons
import shortuuid
import base64
import time
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from collections import defaultdict
from .phonepe import makepayment,phonepecallback
from .helper import Round
from .vrandexp import newPriceExpression,isCarted,isFavorite
from firebase_admin import auth
# Create your views here.
NEWUSER='newuser'
PASSWORD_RESET='passwordReset'
UNKNOWN='unknown'
OTPVERIFY='otpverify'
MOBILENUMBER='mobilenumber'
NOSESSION='nosessionfound'
def index(request):
    return render(request,"test.html")

def testhome(request):
    return render(request,"testhome.html")
def flowerhome(request):
    catss=""
    subcatss=""
    category_id=request.GET.get('catId','')
    query =request.GET.get('q','')
    subcategory_id=request.GET.get('subcatId','')
    userid=request.user.id
    print(f"query is here {query}")
    if query:
        print("Query search")
        flowerList = Flowers.objects.filter( Q(name__icontains=query) | Q(details__icontains=query)).annotate(
                    is_favorite=isFavorite(userid),
                    is_carted=isCarted(userid),
                    new_price = newPriceExpression
                    )
        query="q="+query+"&"
    elif category_id:
        print("Catagory search")
        catss=Category.objects.get(id=category_id)
        flowerList = Flowers.objects.filter(cats__id=category_id).annotate(
                    is_favorite=isFavorite(userid),
                    is_carted=isCarted(userid),
                    new_price = newPriceExpression
        )
        category_id="catId="+category_id +"&"
    elif subcategory_id:
        print("Subcategory search")
        subcatss=Subcategory.objects.get(id=subcategory_id)
        catss=subcatss.category
        flowerList = Flowers.objects.filter(subcat__id=subcategory_id).annotate(
                    is_favorite=isFavorite(userid),
                    is_carted=isCarted(userid),
                    new_price = newPriceExpression
        )
        subcategory_id="subcatId="+subcategory_id +"&"
    else:
        print("Home")
        flowerList = Flowers.objects.annotate(
                is_favorite=isFavorite(userid),
                is_carted=isCarted(userid),
                new_price = newPriceExpression
        )
    p = Paginator(flowerList, 10)
    page_number = request.GET.get('page','')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    subquery=query+category_id+subcategory_id
    context = {'page_obj': page_obj,'catss':catss,'subcatss':subcatss,'subquery':subquery}
    
    return render(request,"flowerhome.html",context)
@csrf_protect
def newsignup(request):
    message={"text":"signup bad request","color_code":"danger"}
    otpverify = request.session.get(OTPVERIFY,NOSESSION)
    mobilenumber = request.session.get(MOBILENUMBER,NOSESSION)
    print("otp beryfy here ------------------")
    print(otpverify)
    
    if ((mobilenumber!=NOSESSION) and (otpverify == NEWUSER or otpverify == PASSWORD_RESET)):
        if request.method == 'POST':
            print(mobilenumber)
            pass1 = request.POST.get('sigup_password')
            pass2 = request.POST.get('sigup_password2')
            if(pass1==pass2):
                try:
                    user, created = User.objects.get_or_create(username=mobilenumber)
                    user.set_password(pass1)
                    user.save()
                    if(user):
                        request.session.flush()
                    if otpverify == PASSWORD_RESET:
                        message={"text":"password changed successfully please login","color_code":"success"}
                    elif otpverify == NEWUSER:
                        message={"text":"signup successfully please login","color_code":"success"}
                    else:
                        message={"text":"unknown error","color_code":"warning"}
                        print('this is logical error please verify')
                except User.DoesNotExist:
                    message={"text":"user must verify otp to signup","color_code":"warning"}
                    
            else:
                message={"text":"both password should be same","color_code":"danger"}
    context = {'message': message,'openpopup':'regpopup'}
    ##return render(request,"flowerhome.html",context)
    return JsonResponse(context)
@csrf_protect
def newlogin(request):
    message={"text":"login bad request","color_code":"danger"}
    if request.method == 'POST':
        countrycode = request.POST.get('sigin_username_countrycode')
        username = request.POST.get('sigin_username')
        password = request.POST.get('sigin_password')
        if(countrycode==""):
            message={"text":"country code not be empty","color_code":"warning"}
        if(username==""):
            message={"text":"mobile number not be empty","color_code":"warning"}
        if(len(username)<10):
            message={"text":"mobile number should be 10 digit","color_code":"warning"}
        elif(password==""):
            message={"text":"password should not be empty","color_code":"warning"}
        else:
            username=countrycode+username
            username=username.strip()
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)    
                message={"text":"logged in successfully","color_code":"success"}
            else:
                existing_user = User.objects.filter(username=username).exists()
                if existing_user:
                    message={"text":"password incorrect","color_code":"danger"}
                else:                           
                    message={"text":"user does not exist","color_code":"warning"}
    context = {'message': message,'openpopup':'loginpopup'}
    return JsonResponse(context)
            
# signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)    
                return redirect('flowerhome')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# logout page
@login_required
def user_logout(request):
    logout(request)
    return redirect('flowerhome')

def favurl(request):
    message="unknown"
    if(request.user.is_authenticated):
        if request.method == 'POST':
            ##userob = request.POST.get('plantob')
            flowerob_id = request.POST.get('flowerob_id')
            userob_id = request.user.id
            fav, created = Favorits.objects.get_or_create(flowerob_id=flowerob_id,userob_id=userob_id)
            if(created):
                message="liked"
            else:
                fav.delete()
                message="like_removed"
        cartcount = Cart.objects.filter(userob_id=request.user.id).count()
    else:
        message="not_loggedin"
    likecount = Favorits.objects.filter(userob_id=request.user.id).count()
    context = {'message':message,'likecount':likecount}
    return JsonResponse(context)

def carturl(request):
    message="unknown"
    if(request.user.is_authenticated):
        if request.method == 'POST':
            ##userob = request.POST.get('plantob')
            cart_id = request.POST.get('cart_id')
            if(cart_id):
                Cart.objects.filter(id=cart_id).delete()
                message="carted_removed"
            else:
                flowerob_id = request.POST.get('flowerob_id')
                userob_id = request.user.id
                cart, created = Cart.objects.get_or_create(flowerob_id=flowerob_id,userob_id=userob_id)
                if(created):
                    message="carted"
                else:
                    cart.delete()
                    message="carted_removed"
            cartcount = Cart.objects.filter(userob_id=request.user.id).count()
            context = {'message':message,'cartcount':cartcount}
            return JsonResponse(context)
    else:
        message="not_loggedin"
        context = {'message':message}
    return JsonResponse(context)
##cartpage
@login_required
def cart(request):
    message="unknown"
    if(request.user.is_authenticated):
        userid=request.user.id
        # Calculate new price as price - (price * offpercentage / 100)
        item_total=ExpressionWrapper(
        Round((F('flowerob__price') - (F('flowerob__price') * F('flowerob__offvalue') / 100))*F('quantity'),2),
        output_field=DecimalField(max_digits=10, decimal_places=2))

        new_price_expression = ExpressionWrapper(
                Round(F('flowerob__price') - (F('flowerob__price') * F('flowerob__offvalue') / 100), 2),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )

        
        carts=Cart.objects.filter(userob_id=userid).select_related('flowerob').annotate(newprice=new_price_expression).annotate(itemtotal=item_total)
        # Calculate total price
        total_price = carts.aggregate(total=Sum('itemtotal'))['total']
        context={'carts':carts,'total_price':total_price}
        return render(request,"cart.html",context)
    else:
        message="not_loggedin"
        context = {'message':message}
    return JsonResponse(context)
@login_required
@require_POST
def updateCart(request):
    message="unknown"
    if(request.user.is_authenticated):
        userid=request.user.id
        doaction = request.POST.get('doaction')
        flowerId = request.POST.get('flowerId')
        try:
            cart_item = get_object_or_404(Cart, userob_id=userid, flowerob_id=flowerId)
            if doaction == 'plus':
                cart_item.quantity += 1
                cart_item.save()
                response = {'status': 'success', 'new_quantity': cart_item.quantity}
            elif doaction == 'minus':
                if(cart_item.quantity>1):
                    cart_item.quantity -= 1
                    cart_item.save()
                    response = {'status': 'success', 'new_quantity': cart_item.quantity}
                response = {'status': 'success', 'new_quantity': cart_item.quantity}
            else:
                response = {'status': 'failure', 'message': 'Invalid action'}
            updated_cartcount = Cart.objects.filter(userob_id=request.user.id).count()
            request.session['cartcount'] = updated_cartcount
        except Cart.DoesNotExist:
            response = {'status': 'failure', 'message': 'Cart item does not exist'}
    else:
        message="not_loggedin"
        response = {'message':message}
    return JsonResponse(response)

@login_required
def favpage(request):
    message="unknown"
    if(request.user.is_authenticated):
        userid=request.user.id
        cart_subquery=Cart.objects.filter(userob_id=userid,flowerob_id=OuterRef('flowerob_id'))
        ##cart_subquery=Cart.objects.filter(userob_id=userid,flowerob_id=OuterRef('pk'))
        favs=Favorits.objects.filter(userob_id=userid).select_related('flowerob').annotate(is_carted=Case(When(Exists(cart_subquery),
                then=Value("carted")),default=Value("not_carted"),output_field=CharField()))
        p = Paginator(favs, 2)
        page_number = request.GET.get('page')
        try:
            page_obj = p.get_page(page_number)  # returns the desired page object
        except PageNotAnInteger:
            # if page_number is not an integer then assign the first page
            page_obj = p.page(1)
        except EmptyPage:
            # if page is empty then return last page
            page_obj = p.page(p.num_pages)
        context = {'page_obj': page_obj}
        return render(request,"favpage.html",context)
    else:
        message="not_loggedin"
        context = {'message':message}
    return JsonResponse(context)

@login_required
def uploadPlants(request):
    message="unknown"
    if(request.user.is_authenticated):
        if request.method == 'POST':
            name = request.POST.get('name')
            image = request.POST.get('image')
            myfile = request.FILES.get('image') if 'image' in request.FILES else None
            details = request.POST.get('details')
            price = request.POST.get('price')
            offvalue = request.POST.get('offvalue')
            cats = request.POST.get('cats')
            subcat = request.POST.get('subcat')
            adddate = request.POST.get('adddate')
            is_active = request.POST.get('is_active')

            # Validation flags and messages
            errors = []
            if not name:
                errors.append("Name is required.")
            if not myfile:
                errors.append("Image file is required.")
            if not details:
                errors.append("Details are required.")
            try:
                price = Decimal(price)
                if price <= 0:
                    errors.append("Price must be a positive number.")
            except (TypeError, ValueError):
                errors.append("Invalid price format.")
            try:
                offvalue = Decimal(offvalue)
                if offvalue < 0:
                    errors.append("Offvalue must be a non-negative number.")
            except (TypeError, ValueError):
                errors.append("Invalid offvalue format.")
            if not cats:
                errors.append("Category is required.")
            if not subcat:
                errors.append("Subcategory is required.")
            try:
                from datetime import datetime
                adddate = datetime.strptime(adddate, '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD.")
            if is_active not in ['True', 'False']:
                errors.append("Is_active must be 'True' or 'False'.")
            if errors:
                return render(request, "uploadplants.html", {'message': 'Error', 'errors': errors})

            custom_directory = 'flowerimages/'
            custom_path = os.path.join(settings.MEDIA_ROOT, custom_directory)
            print(custom_path)
            if not os.path.exists(custom_path):
                os.makedirs(custom_path)
            fs = FileSystemStorage(location=custom_path, base_url=os.path.join(settings.MEDIA_URL, custom_directory))
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename).strip('media/')
            print(uploaded_file_url)
            flower = Flowers.objects.create(name=name,imagetitle=name,image=uploaded_file_url,details=details,
                                            cats_id=cats,subcat_id=subcat,
                                             price=price,offvalue=offvalue,adddate=adddate,is_active=is_active)
           
        return render(request,"uploadplants.html",{'message':'success'})
    else:
        return redirect('flowerhome')


@login_required
def getSubCat(request):
    catid = request.POST.get('catid')
    subCats=Subcategory.objects.filter(category_id=catid).all()
    subCats_list = list(subCats.values())
    context = {'subCats': subCats_list}
    return JsonResponse(context)
@login_required
def geCat(request):
    cats=Category.objects.all()
    cats_list = list(cats.values())
    ##print(cats_list)
    context = {'cats': cats_list}
    return JsonResponse(context)
def plantDetails(request):
    if request.method == 'POST':
        flowerid = request.POST.get('flowerid')
        userid=request.user.id
        print(flowerid)
        print(userid)
        flower = Flowers.objects.annotate(
            is_favorite=isFavorite(userid),
                is_carted=isCarted(userid),
                new_price=newPriceExpression
                ).get(id=flowerid)##this gate should be written at last to get the unique result
        print(flower)
        context = {'flower': flower}
    return render(request,"plantDetails.html",context)

def checkout(request):
    return makepayment(request)
def custom_404(request):
    return render(request, '404.html')
@csrf_exempt
def callback(request):
    return phonepecallback(request)
@login_required
def myorders(request):
    userid=request.user.id
    # Calculate new price as price - (price * offpercentage / 100)
    item_total=ExpressionWrapper(
    Round((F('amount') - (F('amount') * F('offvalue') / 100))*F('quantity'),2),
    output_field=DecimalField(max_digits=10, decimal_places=2))
    new_price_expression = ExpressionWrapper(
    Round(F('amount') - (F('amount') * F('offvalue') / 100),2),
    output_field=DecimalField(max_digits=10, decimal_places=2))
    # Calculate total price
    orders = MyOrders.objects.filter(userob_id=userid).select_related('flowerob') \
        .annotate(newprice=new_price_expression, itemtotal=item_total).order_by('-orderDate')
        #.values('transactionId', 'newprice', 'itemtotal', 'quantity')
    #print(f"init orders is {orders}")
    grouped_orders = defaultdict(lambda: {'tritems': [], 'total_discounted_price': Decimal('0.00'),
                                          'total_mrp': Decimal('0.00'),
                                          'total_discount': Decimal('0.00'),
                                           'status': None,'transectiondate':None})

    for order in orders:
        transaction_id = order.transactionId
        status="unknown"
        transectiondate=""
        try:
            trob=Transection.objects.get(transactionId=transaction_id)
            transectiondate=trob.transectiondate
            if(trob.statusCode=="PAYMENT_SUCCESS"):
                status="payment done online successfully"
            else:
                status=trob.statusCode
        except Transection.DoesNotExist:
            status="no payment found please contact seller"
        print(f"Flower ID: {order.flowerob.id}")
    # We have no object! Do something...
        grouped_orders[transaction_id]['status']=status
        grouped_orders[transaction_id]['transectiondate']=transectiondate
        grouped_orders[transaction_id]['tritems'].append({
            'newprice': order.newprice,
            'itemtotal': order.itemtotal,
            'quantity': order.quantity,
            'offvalue':order.offvalue,
            'amount':order.amount,
            'flower': {
                'name': order.flowerob.name,
                'id': order.flowerob.id,
                'image': order.flowerob.image.url,
                'details': order.flowerob.details,
            }
        })
        grouped_orders[transaction_id]['total_discounted_price'] += ((order.newprice) * (order.quantity))
        grouped_orders[transaction_id]['total_mrp'] += ((order.amount) * (order.quantity))
        #grouped_orders[transaction_id]['total_discount'] += (((order.amount)*(order.offvalue)/100) * (order.quantity))
    grouped_orders[transaction_id]['total_discount']=grouped_orders[transaction_id]['total_mrp']-grouped_orders[transaction_id]['total_discounted_price']
    # Convert the grouped_orders to a list for the context
    grouped_orders_list = [{'transactionId': k, **v} for k, v in grouped_orders.items()]


    #print(grouped_orders_list)
    #total_price = orders.aggregate(total=Sum('itemtotal'))['total']
    context={'orders':grouped_orders_list}
    return render(request,"myorders.html",context)


def verification(request):
    return render(request, 'verification.html')

def verify(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        otp = data.get('otp')
        ##### add a coulmn like if phone is verified but password not set
        try:
            # Verify the OTP using Firebase Admin SDK
            decoded_token = auth.verify_id_token(otp)
            uid = decoded_token['uid']
            phone_number = decoded_token.get('phone_number')
            request.session[MOBILENUMBER] = phone_number
            user= User.objects.get(username=phone_number)
            print(uid)
            print(phone_number)
            if(user):
                request.session[OTPVERIFY] = PASSWORD_RESET
                return JsonResponse({"status": "reset", "uid": uid}, status=400)
            else:
                return JsonResponse({"status": "failure", "message": str(e)}, status=400)
        except User.DoesNotExist:
            request.session[OTPVERIFY] = NEWUSER  # Example user ID
            return JsonResponse({"status": "success", "uid": uid}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({"status": "failure", "message": str(e)}, status=400)
def checkUser(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        phoneNumber = data.get('phoneNumber')
        resetPassword=data.get('resetPassword')
        mobilenumber = request.session.get(MOBILENUMBER,NOSESSION)
        if(phoneNumber==mobilenumber):
            return JsonResponse({"status": "otpVerified"}, status=200)
        else:
            try:
                user=User.objects.get(username=phoneNumber)
                print(user)
                print(mobilenumber)
                print(resetPassword)
                if(user and (resetPassword=="no")):
                    print("hit 1 resetPassword "+resetPassword)
                    return JsonResponse({"status": "exist"}, status=400)
                elif(user and (resetPassword=="yes")):
                    print("hit 2 resetPassword "+ resetPassword)
                    return JsonResponse({"status": "reset"}, status=200)
                else:
                    print("hit 3")
                    return JsonResponse({"status": "failed"}, status=400)
            except User.DoesNotExist:
                    return JsonResponse({"status": "notExist"}, status=200)