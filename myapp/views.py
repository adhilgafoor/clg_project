import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect


#  Create your views here.
from django.views.decorators.cache import never_cache

from myapp.models import *
from nearlive import settings


def logoutss(request):
    request.session.flush()
    messages.success(request, "You have been logged out successfully!")
    return redirect('/loginindex')

def loginindex(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request,user)
            request.session['lid']=user.id
            if user.is_superuser:
                 messages.success(request, "Admin loged in seccessfully.")
                 return redirect('/adminhome')

            elif user.groups.filter(name='admin').exists():
                messages.success(request, "Admin loged in seccessfully.")
                return redirect('/adminhome')

            elif user.groups.filter(name='BuissnessAccount').exists():
                try:
                    business_account = BussinessAccount.objects.get(USER=user, status = "approved")
                    if business_account.Type=="service provider":
                        messages.success(request, "loged in seccessfully.")
                        return redirect('/service_provider_home')

                    elif business_account.Type=="shop":
                        messages.success(request, "loged in seccessfully.")
                        return redirect('/shop_home')
                    elif business_account.Type=="fitness":
                        messages.success(request, "loged in seccessfully.")
                        return redirect('/fitness_home')

                except BussinessAccount.DoesNotExist:
                    messages.error(request, "❌ Wait For Admin Approval.")
                    return redirect('/loginindex')
            else:
                messages.error(request, "❌ You don't have permission to log in here.")
                return redirect('/loginindex')

        else:
            messages.error(request, "❌ Invalid username or password.")
            return redirect('/loginindex')

    return render(request, 'login index.html')


def admin_home(request):
    return render(request, 'adminFolder/adminindex.html')


@login_required(login_url='/loginindex')
@never_cache
def admins_changepassword(request):
    if request.method== 'POST':
        cpass=request.POST['currentPassword']
        npass = request.POST['newPassword']
        cmpass=request.POST['confirmPassword']

        user=request.user

        if not user.check_password(cpass):
            messages.error(request, 'Current password incorrect')
            return redirect('/admin_changepassword')
        if npass != cmpass:
            messages.error(request, 'New password and confirm password do not match')
            return redirect('/admin_changepassword')

        user.set_password(npass)
        user.save()
        messages.error(request, ' password changed')
        return redirect('/adminhome')
    return render(request, 'adminFolder/admin_change_psw.html')

@login_required(login_url='/loginindex')
@never_cache
def admin_verify_buissness(request):
    fg=BussinessAccount.objects.filter(status='pending')
    return render(request, 'adminFolder/admin_verify_account.html',{'data':fg})

@login_required(login_url='/loginindex')
@never_cache
def admin_approve_buissness(request,id):
    BussinessAccount.objects.filter(id=id).update(status='approved')
    return redirect('/admin_verify_buissness')


@login_required(login_url='/loginindex')
@never_cache
def admin_reject_buissness(request,id):
    BussinessAccount.objects.filter(id=id).update(status='rejected')
    return redirect('/admin_verify_buissness')

@login_required(login_url='/loginindex')
@never_cache
def admin_approved_buissness(request):
    fg=BussinessAccount.objects.filter(status='approved')
    return render(request, 'adminFolder/admin_verifyed_account.html',{'data':fg})

@login_required(login_url='/loginindex')
@never_cache
def admin_delete_buissness(request, id):
    try:
        account = BussinessAccount.objects.get(id=id)
        user = account.USER
        account.delete()
        if user:
            user.delete()
        messages.success(request, 'Business account deleted successfully.')
    except BussinessAccount.DoesNotExist:
        messages.error(request, 'Account not found.')
    return redirect('/admin_approved_buissness')

@login_required(login_url='/loginindex')
@never_cache
def admin_add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        details = request.POST['details']

        print(name,details)

        c = Category()
        c.Categoryname = name
        c.Details = details
        c.save()
        return redirect('/admin_view_category')
    return render(request, 'adminFolder/admin_add_category.html')

@login_required(login_url='/loginindex')
@never_cache
def admin_view_category(request):
    fg=Category.objects.all()
    return render(request, 'adminFolder/admin_view_category.html',{'data':fg})


@login_required(login_url='/loginindex')
@never_cache
def admin_edit_category(request,id):
    c=Category.objects.get(id=id)
    if request.method == 'POST':
        name = request.POST['name']
        details = request.POST['details']

        print(name,details)

        c.Categoryname = name
        c.Details = details
        c.save()
        return redirect('/admin_view_category')
    return render(request, 'adminFolder/admin_edit_category.html',{'data':c})


@login_required(login_url='/loginindex')
@never_cache
def admin_delete_category(request,id):
    Category.objects.get(id=id).delete()
    return redirect('/admin_view_category')

@login_required(login_url='/loginindex')
@never_cache
def admin_view_complaints(request):
    Ca = Complaints.objects.filter().order_by("-Date")
    return render(request, 'adminFolder/admin_view_complaints.html',{'data':Ca})

@login_required(login_url='/loginindex')
@never_cache
def admin_view_complaints_search(request):
    fdate=request.POST['fdate']
    tdate=request.POST['tdate']
    fg=Complaints.objects.filter(Date__range=[fdate,tdate])
    return render(request, 'adminFolder/admin_view_complaints.html',{'data':fg})

@login_required(login_url='/loginindex')
@never_cache
def admin_reply_complaints(request,id):
    Ca = Complaints.objects.get(id=id)
    if request.method == 'POST':
        repl = request.POST['reply']
        Ca.Reply = repl
        Ca.Status="Replied"
        Ca.save()
        return redirect('/admin_view_complaints')
    return render(request, 'adminFolder/admin_reply_complaints.html',{'data':Ca})


@login_required(login_url='/loginindex')
@never_cache
def admin_view_users(request):
    Ca = UserAccount.objects.all()
    return render(request, 'adminFolder/admin_view_users.html',{'data':Ca})


@login_required(login_url='/loginindex')
@never_cache
def admin_service_review(request):
    Ca = Review.objects.all()
    return render(request, 'adminFolder/admin_view_review.html',{'data':Ca})


@login_required(login_url='/loginindex')
@never_cache
def admin_appFeedBack(request):
    Ca = FeedBack.objects.all()
    return render(request, 'adminFolder/admin_view_feedback.html',{'data':Ca})


# =============BUSSINESS ACCOUNT REG============

def BuissnessAccount_Reg(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        place = request.POST['place']
        dicts = request.POST['dict']
        pin = request.POST['pin']
        proof = request.FILES['proof']
        photo = request.FILES['photo']
        lat = request.POST['lat']
        longi = request.POST['longii']
        type = request.POST['type']
        username = request.POST['username']
        paswword = request.POST['password']
        print(name,email,phone,place,dicts,pin,proof,photo,lat,longi,type,username,paswword)


        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('/BuissnessAccount_Reg')

        user = User.objects.create_user(username=username, password=paswword, email=email)
        buss, created = Group.objects.get_or_create(name='BuissnessAccount')
        user.groups.add(buss)
        user.save()

        clctr = BussinessAccount()
        fs = FileSystemStorage()
        path1 = fs.save(photo.name, photo)
        path2 = fs.save(proof.name, proof)


        clctr.Name = name
        clctr.Type = type
        clctr.Email = email
        clctr.Phone = phone
        clctr.Place = place
        clctr.Pin = pin
        clctr.District = dicts
        clctr.latitude = lat
        clctr.longitude = longi
        clctr.status = 'pending'
        clctr.Photo = path1
        clctr.Proof = path2
        clctr.USER = user
        clctr.save()

        messages.success(request, 'success')
        return redirect('/loginindex')
    return render(request, 'bussiness_account_reg.html')

# ===============================SERVICE PROVIDER==========
def service_provider_home(request):
    return render(request, 'Service Provider folder/service_provider_home.html')
@login_required(login_url='/loginindex')
def service_changepassword(request):
    if request.method== 'POST':
        cpass=request.POST['currentPassword']
        npass = request.POST['newPassword']
        cmpass=request.POST['confirmPassword']

        user=request.user

        if not user.check_password(cpass):
            messages.error(request, 'Current password incorrect')
            return redirect('/service_changepassword')
        if npass != cmpass:
            messages.error(request, 'New password and confirm password do not match')
            return redirect('/service_changepassword')

        user.set_password(npass)
        user.save()
        messages.error(request, ' password changed')
        return redirect('/service_provider_home')
    return render(request, 'Service Provider folder/provider_change_psw.html')

@login_required(login_url='/loginindex')
def service_providerProfile(request):
    p = BussinessAccount.objects.get(USER=request.user)
    return render(request, 'Service Provider folder/viewProfile.html',{'data':p})

@login_required(login_url='/loginindex')
def serviceProvider_Edit_profile(request):
    clctr = BussinessAccount.objects.get(USER=request.user)

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        place = request.POST['place']
        dicts = request.POST['dict']
        pin = request.POST['pin']
        lat = request.POST['lat']
        longi = request.POST['longii']
        print(name,email,phone,place,dicts,pin,lat,longi,type)


        if 'photo' in request.FILES and 'proof' in request.FILES:

            proof = request.FILES['proof']
            photo = request.FILES['photo']
            fs1 = FileSystemStorage()
            path1 = fs1.save(photo.name, photo)
            path2 = fs1.save(proof.name, proof)
            clctr.Photo = path1
            clctr.Proof = path2


        clctr.Name = name
        clctr.Email = email
        clctr.Phone = phone
        clctr.Place = place
        clctr.Pin = pin
        clctr.District = dicts
        clctr.latitude = lat
        clctr.longitude = longi
        clctr.save()

        messages.success(request, 'success')
        return redirect('/service_providerProfile')
    return render(request, 'Service Provider folder/provider_editProfile.html',{'data':clctr})


@login_required(login_url='/loginindex')
def provider_viewCategory(request):
    p = Category.objects.all()
    return render(request, 'Service Provider folder/provider_view_category.html',{'data':p})

@login_required(login_url='/loginindex')
def provider_addServices(request):
    p = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        amount = request.POST['amount']
        photo = request.FILES['photo']
        details = request.POST['details']
        category = request.POST['category']
        print(name, amount, photo, details,category)

        fs = FileSystemStorage()
        path = fs.save(photo.name,photo)

        s = Service()
        s.Servicename=name
        s.Amount=amount
        s.Photo=path
        s.Details=details
        s.CATEGORY_id=category
        s.BUSSINESSACCOUNT = BussinessAccount.objects.get(USER=request.user)
        s.save()
        messages.success(request, 'success')
        return redirect('/provider_viewServices')
    return render(request, 'Service Provider folder/provider_add_services.html',{'data':p})

@login_required(login_url='/loginindex')
def provider_viewServices(request):
    p = Service.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'Service Provider folder/provider_view_services.html',{'data':p})


@login_required(login_url='/loginindex')
def provider_edit_services(request,id):
    s=Category.objects.all()
    c=Service.objects.get(id=id)
    if request.method == 'POST':
        Servicename = request.POST['name']
        Amount = request.POST['amount']
        Details = request.POST['details']
        category = request.POST['category']

        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            fs =FileSystemStorage()
            path = fs.save(photo.name,photo)
            c.Photo = path

        c.Servicename = Servicename
        c.Amount = Amount
        c.Details = Details
        c.CATEGORY_id = category
        c.save()
        return redirect('/provider_viewServices')
    return render(request, 'Service Provider folder/provider_edit_services.html',{'data':c,"s":s})

@login_required(login_url='/loginindex')
def provider_delete_services(request,id):
    Service.objects.get(id=id).delete()
    return redirect('/provider_viewServices')


@login_required(login_url='/loginindex')
def provider_view_review(request,id):
    s=Service.objects.get(id=id)
    r=Review.objects.filter(SERVICE_id=s)
    return render(request, 'Service Provider folder/provider_view_review.html',{'data':r})

@login_required(login_url='/loginindex')
def provider_addavailability(request):
    p = Service.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)
    if request.method == "POST":
        service = request.POST['service']
        status = request.POST['status']
        ftime = request.POST['ftime']
        ttime = request.POST['ttime']
        from datetime import datetime

        s = AvilableStatus()
        s.Date=datetime.now().today()
        s.SERVICE_id=service
        s.Status=status
        s.Fromtime=ftime
        s.Totime=ttime
        s.save()
        messages.success(request, 'success')
        return redirect('/provider_viewStatus')
    return render(request, 'Service Provider folder/provider_add_availability.html',{'data':p})

@login_required(login_url='/loginindex')
def provider_viewStatus(request):
    p = AvilableStatus.objects.filter(SERVICE__BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'Service Provider folder/provider_view_availabilitystatus.html',{'data':p})



def provider_edit_availability(request,id):
    d= Service.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)
    s= AvilableStatus.objects.get(id=id)
    if request.method == "POST":
        service = request.POST['service']
        status = request.POST['status']
        ftime = request.POST['ftime']
        ttime = request.POST['ttime']


        s.SERVICE_id = service
        s.Status = status
        s.Fromtime = ftime
        s.Totime = ttime
        s.save()
        messages.success(request, 'success')
        return redirect('/provider_viewStatus')
    return render(request, 'Service Provider folder/provider_edit_availability.html',{'data':s,"gh":d})

def provider_delete_availability(request,id):
    AvilableStatus.objects.get(id=id).delete()
    return redirect('/provider_viewStatus')

@login_required(login_url='/loginindex')
def provider_viewRequests(request):
    p = ServiceBooking.objects.filter(SERVICE__BUSSINESSACCOUNT__USER_id=request.user, Status="pending")
    return render(request, 'Service Provider folder/provider_view_Requests.html',{'data':p})


@login_required(login_url='/loginindex')
def provider_viewRequests_search(request):
    fdate=request.POST['fdate']
    tdate=request.POST['tdate']
    fg=ServiceBooking.objects.filter(Date__range=[fdate,tdate],SERVICE__BUSSINESSACCOUNT__USER_id=request.user, Status="pending")
    return render(request, 'Service Provider folder/provider_view_Requests.html',{'data':fg})


@login_required(login_url='/loginindex')
def provider_Requests_Approve(request,id):
    ServiceBooking.objects.filter(id=id).update(Status='approved')
    return redirect('/provider_viewRequests')

@login_required(login_url='/loginindex')
def provider_Requests_Reject(request,id):
    ServiceBooking.objects.filter(id=id).update(Status='rejected')
    return redirect('/provider_viewRequests')

@login_required(login_url='/loginindex')
def provider_viewApproved_Requests(request):
    p = ServiceBooking.objects.filter(SERVICE__BUSSINESSACCOUNT__USER_id=request.user, Status="approved")
    return render(request, 'Service Provider folder/provider_view_ApprovedRequests.html',{'data':p})



def chat3(request,id):
    print(id,"00000000000000000")
    request.session["userid"] = id
    print(request.session["userid"],"this is user id=======")
    cid = str(request.session["userid"])
    request.session["new"] = cid
    return render(request, "Service Provider folder/providerChat.html", {'toid': cid})

def provider_chat_view(request):
    fromid = request.session["lid"]
    toid = request.session["userid"]
    print(fromid,'fromidsssss============')
    print(toid,'toidssssssssssid============')
    from django.db.models import Q

    res = chat.objects.filter(
        Q(FROM_ID_id=fromid, TO_ID_id=toid) |
        Q(FROM_ID_id=toid, TO_ID_id=fromid)
    ).order_by('date')
    l = []

    for i in res:
        l.append({"id": i.id, "message": i.messages, "to": i.TO_ID_id, "date": i.date, "from": i.FROM_ID_id})
    return JsonResponse({"data": l, 'toid': request.session["userid"]})

def provider_chat_send(request, msg):
    lid = request.session["lid"]
    toid = request.session["userid"]
    message = msg
    print(message, 'gfdtd=======ghftgf======hgff======ghfdgfc')
    import datetime
    d = datetime.datetime.now().date()
    chatobt = chat()
    chatobt.messages = message
    chatobt.TO_ID_id = toid
    chatobt.FROM_ID_id = lid
    chatobt.date = d
    chatobt.time = datetime.datetime.now().time()
    chatobt.save()

    return JsonResponse({"status": "ok"})










 # ==================================================USER MODULE STARTS===================
 # ==================================================USER MODULE STARTS===================
 # ==================================================USER MODULE STARTS===================





# ===================================END PROVIDER MODULE==
# ==========================SHOP OWNER MODULE===


def shop_home(request):
    # return render(request, 'shopFolder/shop home.html')
    return render(request, 'shopFolder/shop_home.html')

# def shopss_home(request):
#     return render(request, 'shopFolder/shop_home.html')
@login_required(login_url='/loginindex')
def shop_changepassword(request):
    if request.method== 'POST':
        cpass=request.POST['currentPassword']
        npass = request.POST['newPassword']
        cmpass=request.POST['confirmPassword']

        user=request.user

        if not user.check_password(cpass):
            messages.error(request, 'Current password incorrect')
            return redirect('/shop_changepassword')
        if npass != cmpass:
            messages.error(request, 'New password and confirm password do not match')
            return redirect('/shop_changepassword')

        user.set_password(npass)
        user.save()
        messages.error(request, ' password changed')
        return redirect('/shop_home')
    return render(request, 'shopFolder/shop_change_psw.html')

@login_required(login_url='/loginindex')
def shop_Profile(request):
    p = BussinessAccount.objects.get(USER=request.user)
    return render(request, 'shopFolder/shop_viewProfile.html',{'data':p})

@login_required(login_url='/loginindex')
def shop_Edit_profile(request):
    clctr = BussinessAccount.objects.get(USER=request.user)

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        place = request.POST['place']
        dicts = request.POST['dict']
        pin = request.POST['pin']
        lat = request.POST['lat']
        longi = request.POST['longii']
        print(name,email,phone,place,dicts,pin,lat,longi,type)


        if 'photo' in request.FILES and 'proof' in request.FILES:

            proof = request.FILES['proof']
            photo = request.FILES['photo']
            fs1 = FileSystemStorage()
            path1 = fs1.save(photo.name, photo)
            path2 = fs1.save(proof.name, proof)
            clctr.Photo = path1
            clctr.Proof = path2


        clctr.Name = name
        clctr.Email = email
        clctr.Phone = phone
        clctr.Place = place
        clctr.Pin = pin
        clctr.District = dicts
        clctr.latitude = lat
        clctr.longitude = longi
        clctr.save()

        messages.success(request, 'success')
        return redirect('/shop_Profile')
    return render(request, 'shopFolder/shop_editProfile.html',{'data':clctr})

@login_required(login_url='/loginindex')
def shop_add_products(request):
    c = Category.objects.all()
    if request.method == 'POST':
        product = request.POST['pname']
        price = request.POST['price']
        photo = request.FILES['photo']
        cat = request.POST['cat']



        clctr = Product()
        fs = FileSystemStorage()
        path1 = fs.save(photo.name, photo)


        clctr.Product = product
        clctr.Price = price
        clctr.Photo = path1
        clctr.BUSSINESSACCOUNT = BussinessAccount.objects.get(USER=request.user)
        clctr.CATEGORY_id = cat
        clctr.save()

        messages.success(request, 'success')
        return redirect('/shop_add_products')
    return render(request, 'shopFolder/shop_add_products.html',{'data':c})


@login_required(login_url='/loginindex')
def shop_view_products(request):
    p = Product.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'shopFolder/shop_view_products.html',{'data':p})


@login_required(login_url='/loginindex')
def shop_edit_products(request,id):
    d= Category.objects.all()
    clctr = Product.objects.get(id=id)
    if request.method == "POST":
        product = request.POST['pname']
        price = request.POST['price']
        cat = request.POST['cat']

        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            fs = FileSystemStorage()
            path1 = fs.save(photo.name, photo)
            clctr.Photo = path1

        clctr.Product = product
        clctr.Price = price
        clctr.BUSSINESSACCOUNT = BussinessAccount.objects.get(USER=request.user)
        clctr.CATEGORY_id = cat
        clctr.save()
        messages.success(request, 'success')
        return redirect('/shop_view_products')
    return render(request, 'shopFolder/shop_edit_products.html',{'data':clctr,"gh":d})

def shop_delete_products(request,id):
    Product.objects.get(id=id).delete()
    return redirect('/shop_view_products')


@login_required(login_url='/loginindex')
def shop_add_offers(request,id):
    c = Product.objects.get(id=id)
    if request.method == 'POST':
        price = request.POST['price']
        Offername = request.POST['Offername']
        Fromdate = request.POST['Fromdate']
        Todate = request.POST['Todate']
        Details = request.POST['Details']

        clctr = Offers()

        clctr.PRODUCT = c
        clctr.Offername = Offername
        clctr.Amount = price
        clctr.Fromdate = Fromdate
        clctr.Todate = Todate
        clctr.Details = Details
        clctr.save()

        messages.success(request, 'success')
        return redirect('/shop_view_offers')
    return render(request, 'shopFolder/shop_add_offers.html',{'data':c})


@login_required(login_url='/loginindex')
def shop_view_offers(request):
    p = Offers.objects.filter(PRODUCT__BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'shopFolder/shop_view_offers.html',{'data':p})

@login_required(login_url='/loginindex')
def shop_edit_offers(request,id):
    clctr = Offers.objects.get(id=id)
    if request.method == "POST":
        Offername = request.POST['Offername']
        Amount = request.POST['price']
        Fromdate = request.POST['Fromdate']
        todate = request.POST['todate']
        details = request.POST['Details']


        clctr.Offername = Offername
        clctr.Amount = Amount
        clctr.Fromdate = Fromdate
        clctr.Todate = todate
        clctr.Details = details
        clctr.save()
        messages.success(request, 'success')
        return redirect('/shop_view_offers')
    return render(request, 'shopFolder/shop_edit_offers.html',{'data':clctr})

def shop_delete_offers(request,id):
    Offers.objects.get(id=id).delete()
    return redirect('/shop_view_offers')

@login_required(login_url='/loginindex')
def shop_add_stock(request):
    p=Product.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)

    if request.method == 'POST':
        stock_details = request.POST['stock']
        product = request.POST['select']


        clctr = Stock()

        clctr.stock_details = stock_details
        clctr.product_id = product
        clctr.save()

        messages.success(request, 'success')
        return redirect('/shop_view_stock')
    return render(request, 'shopFolder/shop_add_stock.html',{'data':p})

@login_required(login_url='/loginindex')
def shop_view_stock(request):
    p = Stock.objects.filter(product__BUSSINESSACCOUNT__USER_id=request.user)
    print(p)
    return render(request, 'shopFolder/shop_view_STOCK.html',{'data':p})

@login_required(login_url='/loginindex')
def shop_edit_stock(request,id):
    p=Product.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)
    clctr = Stock.objects.get(id=id)
    if request.method == "POST":
        stock_details = request.POST['stock']
        products = request.POST['select']

        clctr.stock_details = stock_details
        clctr.product_id = products
        clctr.save()
        messages.success(request, 'success')
        return redirect('/shop_view_stock')
    return render(request, 'shopFolder/shop_edit_stock.html',{'data':clctr,"st":p})

@login_required(login_url='/loginindex')
def shop_delete_stock(request,id):
    Stock.objects.get(id=id).delete()
    return redirect('/shop_view_stock')

@login_required(login_url='/loginindex')
def shop_view_productreview(request,id):
    a = ProductReview.objects.filter(PRODUCT_id=id)
    return render(request, 'shopFolder/shop_view_productreview.html', {'data': a})

@login_required(login_url='/loginindex')
def shop_view_orders(request):
    o = OrderSub.objects.filter(PRODUCT__BUSSINESSACCOUNT__USER_id=request.user)
    l=[]
    for i in o:
        total = float(i.Quantity) * float(i.PRODUCT.Price)
        l.append({'orderdata':i, 'total':total})
    return render(request, 'shopFolder/shop_view_orders.html',{'data':l,})


def chat2(request, id):
    print(id,"00000000000000000")
    request.session["userid"] = id
    print(request.session["userid"],"this is user id=======")
    cid = str(request.session["userid"])
    request.session["new"] = cid
    return render(request, "shopFolder/shopChat.html", {'toid': cid})

def shop_chat_view(request):
    fromid = request.session["lid"]
    toid = request.session["userid"]
    print(fromid,'fromidsssss============')
    print(toid,'toidssssssssssid============')
    from django.db.models import Q

    res = chat.objects.filter(Q(FROM_ID_id=fromid, TO_ID_id=toid) | Q(FROM_ID_id=toid, TO_ID_id=fromid))
    l = []

    for i in res:
        l.append({"id": i.id, "message": i.messages, "to": i.TO_ID_id, "date": i.date, "from": i.FROM_ID_id})
    return JsonResponse({"data": l, 'toid': request.session["userid"]})

def shop_chat_send(request, msg):
    lid = request.session["lid"]
    toid = request.session["userid"]
    message = msg
    print(message, 'gfdtd=======ghftgf======hgff======ghfdgfc')
    import datetime
    d = datetime.datetime.now().date()
    chatobt = chat()
    chatobt.messages = message
    chatobt.TO_ID_id = toid
    chatobt.FROM_ID_id = lid
    chatobt.date = d
    chatobt.time = datetime.datetime.now().time()
    chatobt.save()

    return JsonResponse({"status": "ok"})










 # ==================================================USER MODULE STARTS===================
 # ==================================================USER MODULE STARTS===================
 # ==================================================USER MODULE STARTS===================









# =========================END ===

# =============START FITNESS MODULE=======

def fitness_home(request):
    return render(request, 'fitnessFolder/main_home_page.html')

def fitness_changepassword(request):
    if request.method== 'POST':
        cpass=request.POST['currentPassword']
        npass = request.POST['newPassword']
        cmpass=request.POST['confirmPassword']

        user=request.user

        if not user.check_password(cpass):
            messages.error(request, 'Current password incorrect')
            return redirect('/fitness_changepassword')
        if npass != cmpass:
            messages.error(request, 'New password and confirm password do not match')
            return redirect('/fitness_changepassword')

        user.set_password(npass)
        user.save()
        messages.error(request, ' password changed')
        return redirect('/fitness_home')
    return render(request, 'fitnessFolder/fitness_change_psw.html')


def fitness_Profile(request):
    p = BussinessAccount.objects.get(USER=request.user)
    return render(request, 'fitnessFolder/fitviewProfile.html',{'data':p})

def fitness_Edit_profile(request):
    clctr = BussinessAccount.objects.get(USER=request.user)

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        place = request.POST['place']
        dicts = request.POST['dict']
        pin = request.POST['pin']
        lat = request.POST['lat']
        longi = request.POST['longii']
        print(name,email,phone,place,dicts,pin,lat,longi,type)


        if 'photo' in request.FILES and 'proof' in request.FILES:

            proof = request.FILES['proof']
            photo = request.FILES['photo']
            fs1 = FileSystemStorage()
            path1 = fs1.save(photo.name, photo)
            path2 = fs1.save(proof.name, proof)
            clctr.Photo = path1
            clctr.Proof = path2


        clctr.Name = name
        clctr.Email = email
        clctr.Phone = phone
        clctr.Place = place
        clctr.Pin = pin
        clctr.District = dicts
        clctr.latitude = lat
        clctr.longitude = longi
        clctr.save()

        messages.success(request, 'success')
        return redirect('/fitness_Profile')
    return render(request, 'fitnessFolder/fitness_editProfile.html',{'data':clctr})

def fitness_add_specialisation(request):
    if request.method == 'POST':
        name = request.POST['name']
        amount = request.POST['amount']
        details = request.POST['details']

        clctr = Specialisation()

        clctr.Name = name
        clctr.TotalAmount = amount
        clctr.Details = details
        clctr.FITNESS = BussinessAccount.objects.get(USER=request.user)
        clctr.save()

        messages.success(request, 'success')
        return redirect('/fitness_add_specialisation')
    return render(request, 'fitnessFolder/fitness_add_specialisation.html')

def fit_view_specialisations(request):
    p = Specialisation.objects.filter(FITNESS__USER_id=request.user)
    return render(request, 'fitnessFolder/fit_view_special.html',{'data':p})

def fitness_edit_specialisation(request,id):
    clctr = Specialisation.objects.get(id=id)
    if request.method == "POST":
        name = request.POST['name']
        amount = request.POST['amount']
        details = request.POST['details']


        clctr.Name = name
        clctr.TotalAmount = amount
        clctr.Details = details
        clctr.FITNESS = BussinessAccount.objects.get(USER=request.user)
        clctr.save()

        messages.success(request, 'success')
        return redirect('/fit_view_specialisations')
    return render(request, 'fitnessFolder/fitness_edit_specialisation.html',{'data':clctr})

def fitness_delete_specialisation(request,id):
    Specialisation.objects.get(id=id).delete()
    return redirect('/fit_view_specialisations')


def fitness_add_Services(request):
    p = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        amount = request.POST['amount']
        photo = request.FILES['photo']
        details = request.POST['details']
        category = request.POST['category']
        print(name, amount, photo, details,category)

        fs = FileSystemStorage()
        path = fs.save(photo.name,photo)

        s = Service()
        s.Servicename=name
        s.Amount=amount
        s.Photo=path
        s.Details=details
        s.CATEGORY_id=category
        s.BUSSINESSACCOUNT = BussinessAccount.objects.get(USER=request.user)
        s.save()
        messages.success(request, 'success')
        return redirect('/fitness_viewServices')
    return render(request, 'fitnessFolder/fitness_add_services.html',{'data':p})


def fitness_viewServices(request):
    p = Service.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'fitnessFolder/fitness_view_services.html',{'data':p})

def fitness_edit_services(request,id):
    s=Category.objects.all()
    c=Service.objects.get(id=id)
    if request.method == 'POST':
        Servicename = request.POST['name']
        Amount = request.POST['amount']
        Details = request.POST['details']
        category = request.POST['category']

        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            fs =FileSystemStorage()
            path = fs.save(photo.name,photo)
            c.Photo = path

        c.Servicename = Servicename
        c.Amount = Amount
        c.Details = Details
        c.CATEGORY_id = category
        c.save()
        return redirect('/fitness_viewServices')
    return render(request, 'fitnessFolder/fitness_edit_services.html',{'data':c,"s":s})

def fitness_delete_services(request,id):
    Service.objects.get(id=id).delete()
    return redirect('/fitness_viewServices')


def fitness_view_review(request,id):
    s=Service.objects.get(id=id)
    r=Review.objects.filter(SERVICE_id=s)
    return render(request, 'fitnessFolder/fitness_view_review.html',{'data':r})

def fit_addavailability(request):
    p = Service.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)
    if request.method == "POST":
        service = request.POST['service']
        status = request.POST['status']
        ftime = request.POST['ftime']
        ttime = request.POST['ttime']
        from datetime import datetime

        s = AvilableStatus()
        s.Date=datetime.now().today()
        s.SERVICE_id=service
        s.Status=status
        s.Fromtime=ftime
        s.Totime=ttime
        s.save()
        messages.success(request, 'success')
        return redirect('/fitness_viewStatus')
    return render(request, 'fitnessFolder/fitness_add_availability.html',{'data':p})

def fitness_viewStatus(request):
    p = AvilableStatus.objects.filter(SERVICE__BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'fitnessFolder/fitness_view_availabilitystatus.html',{'data':p})

def fitness_edit_availability(request,id):
    d= Service.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)
    s= AvilableStatus.objects.get(id=id)
    if request.method == "POST":
        service = request.POST['service']
        status = request.POST['status']
        ftime = request.POST['ftime']
        ttime = request.POST['ttime']


        s.SERVICE_id = service
        s.Status = status
        s.Fromtime = ftime
        s.Totime = ttime
        s.save()
        messages.success(request, 'success')
        return redirect('/provider_viewStatus')
    return render(request, 'fitnessFolder/fitness_edit_availability.html',{'data':s,"gh":d})

def fitness_delete_availability(request,id):
    AvilableStatus.objects.get(id=id).delete()
    return redirect('/provider_viewStatus')

def fitness_add_facility(request):
    if request.method == "POST":
        name = request.POST['name']
        photo = request.FILES['photo']
        details = request.POST['details']

        fs = FileSystemStorage()
        path = fs.save(photo.name,photo)

        s = Facility()
        s.facilityName=name
        s.Photo=path
        s.Details=details
        s.FITNESS = BussinessAccount.objects.get(USER=request.user)
        s.save()
        messages.success(request, 'success')
        return redirect('/fitness_add_facility')
    return render(request, 'fitnessFolder/fitness_add_facility.html',)

def fitness_view_facility(request):
    p = Facility.objects.filter(FITNESS__USER_id=request.user)
    return render(request, 'fitnessFolder/fitness_view_facility.html',{'data':p})

def fitness_edit_facility(request,id):
    c=Facility.objects.get(id=id)
    if request.method == 'POST':
        name = request.POST['name']
        details = request.POST['details']

        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            fs =FileSystemStorage()
            path = fs.save(photo.name,photo)
            c.Photo = path

        c.facilityName = name
        c.Details = details
        c.save()
        return redirect('/fitness_view_facility')
    return render(request, 'fitnessFolder/fitness_edit_facility.html',{'data':c,})

def fitness_delete_facility(request,id):
    Facility.objects.get(id=id).delete()
    return redirect('/fitness_view_facility')

def fitness_add_offers(request):
    s = Service.objects.filter(BUSSINESSACCOUNT__USER=request.user)
    if request.method == "POST":
        name = request.POST['name']
        amount = request.POST['amount']
        package = request.POST['package']
        sdate = request.POST['sdate']
        edate = request.POST['edate']
        details = request.POST['details']
        service = request.POST['service']

        s = Fitnessoffers()
        s.OfferName=name
        s.Amount=amount
        s.Package=package
        s.Startdate=sdate
        s.EndDate=edate
        s.Details=details
        s.SERVICE_id = service
        s.save()
        messages.success(request, 'success')
        return redirect('/fitness_add_facility')
    return render(request, 'fitnessFolder/fitness_add_offers.html',{'data':s})


def fitness_view_offers(request):
    p = Fitnessoffers.objects.filter(SERVICE__BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'fitnessFolder/fitness_view_offers.html',{'data':p})


def fitness_edit_offers(request,id):
    d= Service.objects.filter(BUSSINESSACCOUNT__USER_id=request.user)
    s= Fitnessoffers.objects.get(id=id)
    if request.method == "POST":
        name = request.POST['name']
        amount = request.POST['amount']
        package = request.POST['package']
        sdate = request.POST['sdate']
        edate = request.POST['edate']
        details = request.POST['details']
        service = request.POST['service']


        s.OfferName = name
        s.Amount = amount
        s.Package = package
        s.Startdate = sdate
        s.EndDate = edate
        s.Details = details
        s.SERVICE_id = service
        s.save()
        messages.success(request, 'success')
        return redirect('/fitness_view_offers')
    return render(request, 'fitnessFolder/fitness_edit_offers.html', {'data': s, 'smm':d})


def fitness_delete_offers(request,id):
    Fitnessoffers.objects.get(id=id).delete()
    messages.success(request, 'Deleted')
    return redirect('/fitness_view_offers')


def fitness_add_Slots(request,id):
    a = AvilableStatus.objects.get(id=id)
    if request.method == "POST":
        Date = request.POST['Date']
        amount = request.POST['amount']
        slotnumber = request.POST['slotnumber']
        status = request.POST['status']

        s = Slot()
        s.Date=Date
        s.Status=status
        s.Amount=amount
        s.SlotNumber=slotnumber
        s.AVILABLE= a
        s.save()
        messages.success(request, 'success')
        return redirect('/view_added_SLOT')
    return render(request, 'fitnessFolder/fitness_add_slot.html')

def view_added_SLOT(request):
    a=Slot.objects.filter(AVILABLE__SERVICE__BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'fitnessFolder/fitness_view_slots.html',{'data':a})

def fitness_edit_Slots(request,id):
    s = Slot.objects.get(id=id)
    if request.method == "POST":
        Date = request.POST['Date']
        amount = request.POST['amount']
        slotnumber = request.POST['slotnumber']
        status = request.POST['status']


        s.Date=Date
        s.Status=status
        s.Amount=amount
        s.SlotNumber=slotnumber
        s.save()
        messages.success(request, 'success')
        return redirect('/view_added_SLOT')
    return render(request, 'fitnessFolder/fitness_edit_slot.html',{'data':s})


def fintness_delete_slot(request,id):
    Slot.objects.get(id=id).delete()
    messages.success(request, 'Deleted')
    return redirect('/view_added_SLOT')


def fitness_view_appointments(request):
    a=ServiceBooking.objects.filter(Status="pending", SERVICE__BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'fitnessFolder/fitness_view_slotbookings.html',{'data':a})

def fintness_approve_appointments(request,id):
    ServiceBooking.objects.filter(id=id).update(Status="approved")
    messages.success(request, 'Approved')
    return redirect('/fitness_view_appointments')

def fintness_reject_appointments(request,id):
    ServiceBooking.objects.filter(id=id).update(Status="rejected")
    messages.success(request, 'Rejected')
    return redirect('/fitness_view_appointments')


def fitness_view_approved(request):
    a=ServiceBooking.objects.filter(Status="approved", SERVICE__BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'fitnessFolder/fitness_view_slotbookingsapproved.html',{'data':a})

def fitness_view_payments(request):
    a=BookSlotpayment.objects.filter(BOOKSLOT__SLOT__AVILABLE__SERVICE__BUSSINESSACCOUNT__USER_id=request.user)
    return render(request, 'fitnessFolder/fitness_view_slotbookingsapproved.html',{'data':a})

def chat1(request, id):
    print(id,"00000000000000000")
    request.session["userid"] = id
    print(request.session["userid"],"this is user id=======")
    cid = str(request.session["userid"])
    request.session["new"] = cid
    return render(request, "fitnessFolder/FitChat.html", {'toid': cid})

def fit_chat_view(request):
    fromid = request.session["lid"]
    toid = request.session["userid"]
    print(fromid,'fromidsssss============')
    print(toid,'toidssssssssssid============')
    from django.db.models import Q

    res = chat.objects.filter(
        Q(FROM_ID_id=fromid, TO_ID_id=toid) |
        Q(FROM_ID_id=toid, TO_ID_id=fromid)
    ).order_by('date')
    l = []

    for i in res:
        l.append({"id": i.id, "message": i.messages, "to": i.TO_ID_id, "date": i.date, "from": i.FROM_ID_id})
    return JsonResponse({"data": l, 'toid': request.session["userid"]})

def fit_chat_send(request, msg):
    lid = request.session["lid"]
    toid = request.session["userid"]
    message = msg
    print(message, 'gfdtd=======ghftgf======hgff======ghfdgfc')
    import datetime
    d = datetime.datetime.now().date()
    chatobt = chat()
    chatobt.messages = message
    chatobt.TO_ID_id = toid
    chatobt.FROM_ID_id = lid
    chatobt.date = d
    chatobt.time = datetime.datetime.now().time()
    chatobt.save()

    return JsonResponse({"status": "ok"})










 # ==================================================USER MODULE STARTS===================
 # ==================================================USER MODULE STARTS===================
 # ==================================================USER MODULE STARTS===================







# =====================================USER MODULE
def user_login(request):
    username = request.POST['username']
    password = request.POST['psw']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        if user.groups.filter(name="user").exists():
            return JsonResponse({'status':'ok', 'lid':user.id})
        else:
            return JsonResponse({'status': 'error', 'message': 'Not a customer'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})


def Customer_reg(request):
    fname = request.POST['fname']
    phone = request.POST['Phone_no']
    photo = request.FILES['photo']
    email = request.POST['Email_id']
    place = request.POST['place']
    district = request.POST['district']
    pin = request.POST['pin']
    psw = request.POST['password']
    cpsw = request.POST['cpassword']
    username = request.POST['username']
    print(psw)
    from datetime import datetime
    if psw==cpsw:
        user = User.objects.create(username=username, password=make_password(cpsw), email=email)
        user.save()
        user.groups.add(Group.objects.get(name='user'))

        fs = FileSystemStorage()
        date = datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
        fs.save(date, photo)
        path = fs.url(date)


        vu = UserAccount()

        vu.Name = fname
        vu.Phone = phone
        vu.Email = email
        vu.Place = place
        vu.Photo = path
        vu.Pin = pin
        vu.District = district
        vu.USER=user
        vu.save()
        return JsonResponse({'status':'ok'})
    else:
        return JsonResponse({'status':'no'})


def customer_viewprofile(request):
    lid = request.POST['lid']
    c = UserAccount.objects.get(USER=lid)
    return JsonResponse({'status': 'ok',
                         'fname': c.Name,
                         'phone':c.Phone,
                         'email':c.Email,
                         'place':c.Place,
                         'dict':c.District,
                         'pin':c.Pin,
                         'photo':c.Photo
                         })

def cust_editprofile(request):
    fname = request.POST['fname']
    phone = request.POST['Phone_no']
    email = request.POST['Email_id']
    place = request.POST['place']
    district = request.POST['district']
    pin = request.POST['pin']
    lid = request.POST['lid']
    vu = UserAccount.objects.get(USER=lid)

    from datetime import datetime
    if 'photo' in request.FILES:

        photo = request.FILES['photo']

        fs = FileSystemStorage()
        date = datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
        fs.save(date, photo)
        path = fs.url(date)
        vu.Photo = path

    vu.Name = fname
    vu.Phone = phone
    vu.Email = email
    vu.Place = place
    vu.Pin = pin
    vu.District = district
    vu.save()
    return JsonResponse({'status': 'ok'})

def userchangepassword(request):
    currentpassword = request.POST["currentpassword"]
    newpassword = request.POST["newpassword"]
    confirmpassword = request.POST["confirmpassword"]
    lid = request.POST["lid"]  # This should be a user ID or similar


    user = User.objects.get(id=lid)  # Get actual User object from ID
    if not user.check_password(currentpassword):
        return JsonResponse({"status": "incorrect_password"})

    if newpassword != confirmpassword:
        return JsonResponse({'status': 'password_mismatch'})

    user.set_password(newpassword)
    user.save()
    logout(request)  # Optional: Only use if user is logged in via session

    return JsonResponse({'status': 'ok'})


from django.http import JsonResponse
from geopy.distance import geodesic


def user_view_centers(request):
    lid = request.POST['lid']

    # Get user's current location from request
    user_lat = float(request.POST.get('user_latitude', 0))
    user_lon = float(request.POST.get('user_longitude', 0))

    ad = BussinessAccount.objects.all()
    l = []

    for i in ad:
        try:
            # Calculate distance between user and business center
            center_coords = (float(i.latitude), float(i.longitude))
            user_coords = (user_lat, user_lon)
            distance_km = geodesic(user_coords, center_coords).km
            distance_km = round(distance_km, 2)
        except (ValueError, TypeError):
            distance_km = None

        l.append({
            'id': i.id,
            'Name': i.Name,
            'Email': i.Email,
            'Phone': i.Phone,
            'Place': i.Place,
            'District': i.District,
            'latitude': i.latitude,
            'longitude': i.longitude,
            'distance_km': distance_km
        })

    # Sort by distance (nearest first)
    l.sort(key=lambda x: x['distance_km'] if x['distance_km'] is not None else float('inf'))

    print(l)
    return JsonResponse({'status': 'ok', 'data': l})




# def user_view_centers(request):
#     lid = request.POST['lid']
#     ad = BussinessAccount.objects.all()
#     l = []
#     for i in ad:
#         l.append({'id': i.id,
#                   'Name': i.Name,
#                   'Email': i.Email,
#                   'Phone': i.Phone,
#                   'Place': i.Place,
#                   'District': i.District,
#                   'latitude': i.latitude,
#                   'longitude': i.longitude,
#                   })
#     print(l)
#     return JsonResponse({'status': 'ok', 'data': l})

def user_view_services(request):
    bid = request.POST['bid']
    k=Service.objects.filter(BUSSINESSACCOUNT_id=bid)
    l = []
    for i in k:
        l.append({'id': i.id,
                  'Servicename': i.Servicename,
                  'Amount': i.Amount,
                  'Photo': i.Photo.url,
                  'Details': i.Details,
                  'CATEGORY': i.CATEGORY.Categoryname,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})


def user_view_availability(request):
    sid = request.POST['sid']
    k=AvilableStatus.objects.filter(SERVICE_id=sid)
    l = []
    for i in k:
        l.append({'id': i.id,
                  'Date': i.Date,
                  'Status': i.Status,
                  'Fromtime': i.Fromtime,
                  'Totime': i.Totime,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})

def service_booking(request):
    sbi = request.POST['sbi']
    lid = request.POST['lid']

    from datetime import datetime

    s=ServiceBooking()
    s.USER = UserAccount.objects.get(USER=lid)
    s.SERVICE = Service.objects.get(id=sbi)
    s.Date=datetime.now().date()
    s.Status="pending"
    s.save()
    return JsonResponse({'status': 'ok'})



def user_view_requeststatus(request):
    lid = request.POST['lid']
    k=ServiceBooking.objects.filter(USER__USER_id=lid)
    l = []
    for i in k:
        l.append({
                  'ids': i.id,
                  'busid': i.SERVICE.BUSSINESSACCOUNT.USER.id,
                  'busname': i.SERVICE.BUSSINESSACCOUNT.Name,
                  'Servicename': i.SERVICE.Servicename,
                  'sid': i.SERVICE.id,
                  'Amount': i.SERVICE.Amount,
                  'Date': i.Date,
                  'Status': i.Status,
                  'CATEGORY': i.SERVICE.CATEGORY.Categoryname,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})









from django.http import JsonResponse
from datetime import datetime


def cartpayment(request):
    sid = request.POST["sid"]
    print(sid)
    total_amount = request.POST["total_amount"]

    payment = ServicePayment()
    payment.Date = datetime.now().today()
    payment.Status = 'paid'
    payment.SERVICEBOKKING = ServiceBooking.objects.get(SERVICE__id= sid)
    payment.TotalAmount=str(total_amount)
    payment.save()
    return JsonResponse({'status': 'ok'})



def user_view_facilities(request):
    k=Facility.objects.all()
    l = []
    for i in k:
        l.append({'ids': i.id,
                  'facilityName': i.facilityName,
                  'Photo': i.Photo.url,
                  'Details': i.Details,
                  'FITNESS': i.FITNESS.Name,
                  'Email': i.FITNESS.Email,
                  'Phone': i.FITNESS.Phone,
                  'Place': i.FITNESS.Place,
                  'latitude': i.FITNESS.latitude,
                  'longitude': i.FITNESS.longitude,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})



def user_sendFeedback(request):
    sid = request.POST["lid"]
    Feedback = request.POST["review"]

    p = FeedBack()
    p.Date = datetime.now().today()
    p.Feedback = Feedback
    p.USER = UserAccount.objects.get(USER_id=sid)
    p.save()
    return JsonResponse({'status': 'ok'})



def user_sendComplaints(request):
    sid = request.POST["lid"]
    comps = request.POST["cmps"]

    p = Complaints()
    p.Date = datetime.now().today()
    p.Complaints = comps
    p.Status = "pending"
    p.Reply = "pending"
    p.USER = UserAccount.objects.get(USER_id=sid)
    p.save()
    return JsonResponse({'status': 'ok'})



def user_view_reply(request):
    lid=request.POST['lid']
    k=Complaints.objects.filter(USER__USER_id=lid)
    l = []
    for i in k:
        l.append({'id': i.id,
                  'Date': i.Date,
                  'Complaints': i.Complaints,
                  'Status': i.Status,
                  'Reply': i.Reply,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})





def user_view_slot(request):
    aid=request.POST['aid']
    k=Slot.objects.filter(AVILABLE_id=aid)
    l = []
    for i in k:
        l.append({'id': i.id,
                  'Date': i.Date,
                  'Amount': i.Amount,
                  'Status': i.Status,
                  'SlotNumber': i.SlotNumber,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})


def slot_booking(request):
    bid = request.POST['bid']
    lid = request.POST['lid']
    print(lid)
    print(bid)
    from datetime import datetime

    s=BookSlot()
    s.USER = UserAccount.objects.get(USER=lid)
    s.SLOT = Slot.objects.get(id=bid)
    s.Date=datetime.now().date()
    s.Status="pending"
    s.save()
    return JsonResponse({'status': 'ok'})





def user_view_booked_slots(request):
    lid = request.POST['lid']
    k=BookSlot.objects.filter(USER__USER_id=lid)
    l = []
    for i in k:
        l.append({'id': i.id,
                  'SlotDate': i.SLOT.Date,
                  'Amount': i.SLOT.Amount,
                  'SlotNumber': i.SLOT.SlotNumber,
                  'SlotStatus': i.SLOT.Status,
                  'bookeddate': i.Date,
                  'Status': i.Status,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})



def slotpayment(request):
    sid = request.POST["sid"]
    total_amount = request.POST["total_amount"]

    payment = BookSlotpayment()
    payment.Date = datetime.now().today()
    payment.Status = 'paid'
    payment.BOOKSLOT = BookSlot.objects.get(id=sid)
    payment.Amount=str(total_amount)
    payment.save()
    return JsonResponse({'status': 'ok'})


def user_view_paymentDetails(request):
    bsid = request.POST.get('bsid', None)
    print(bsid, "===================================================bsid")
    l = []
    if bsid and bsid.isdigit():
        payments = BookSlotpayment.objects.filter(BOOKSLOT_id=bsid)
        for p in payments:
            l.append({
                'ids': p.id,
                'amount': p.Amount,
                'Paymentdate': p.Date,
                'status': p.Status,
            })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})


# def user_view_offers(request):
#     k=Offers.objects.all()
#     l = []
#     for i in k:
#         l.append({'id': i.id,
#                   'Offername': i.Offername,
#                   'Amount': i.Amount,
#                   'Fromdate': i.Fromdate,
#                   'Todate': i.Todate,
#                   'ProductName': i.PRODUCT.Product,
#                   'productid': i.PRODUCT.id,
#                   'ProductPrice': i.PRODUCT.Price,
#                   'Photo': i.PRODUCT.Photo.url,
#                   })
#     print(l)
#     return JsonResponse({'status': 'ok', 'data': l})

def user_view_offers(request):
    k = Offers.objects.all()
    l = []
    for i in k:
        # Try to fetch the stock details for the given product
        stock = Stock.objects.filter(product=i.PRODUCT.id).first()
        stock_details = stock.stock_details if stock else None

        l.append({
            'id': i.id,
            'Offername': i.Offername,
            'Amount': i.Amount,
            'Fromdate': i.Fromdate,
            'Todate': i.Todate,
            'ProductName': i.PRODUCT.Product,
            'productid': i.PRODUCT.id,
            'ProductPrice': i.PRODUCT.Price,
            'Photo': i.PRODUCT.Photo.url,
            'StockDetails': stock_details
        })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})






def addtocart(request):
    date = datetime.now().today()
    lid = request.POST['lid']
    pid = request.POST['pid']

    quantity = int(request.POST['quantity'])

    print(quantity,'qqqqq')

    user = UserAccount.objects.get(USER=lid)
    # p = Product.objects.get(id=pid).price
    p = Product.objects.get(id=pid)

    print(p, '---------')


    obj = Cart()
    obj.Date = date
    obj.USER = user
    obj.PRODUCT_id = pid
    obj.Quantity = quantity
    obj.save()


    st = Stock.objects.get(product=p)
    oldstock = int(st.stock_details)
    if oldstock >= quantity:
        st.stock_details = str(oldstock - quantity)
        st.save()
    else:
        return JsonResponse({'status': 'no', 'message': 'Insufficient stock'})
    return JsonResponse({'status': 'ok'})



from datetime import datetime

def user_view_cart(request):
    lid = request.POST['lid']
    k = Cart.objects.filter(USER__USER_id=lid)
    l = []
    total = 0
    now = datetime.now().date()

    for i in k:
        product = i.PRODUCT
        # Check for active offers
        offer = Offers.objects.filter(PRODUCT=product, Fromdate__lte=now, Todate__gte=now).order_by('-Amount').first()
        if offer:
            price = float(offer.Amount)
            offername = offer.Offername
        else:
            price = float(product.Price)
            offername = None

        item_total = price * int(i.Quantity)
        total += item_total

        l.append({
            'id': i.id,
            'Date': i.Date,
            'Quantity': i.Quantity,
            'productname': product.Product,
            'productid': product.id,
            'productprice': price,
            'Photo': product.Photo.url,
            'offername': offername,
            'item_total': item_total,
        })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l, 'cart_total': total})

# def deletefromcart(request):
#     id=request.POST['cid']
#     Cart.objects.get(id=id).delete()
#     return JsonResponse(
#         {
#             'status': 'ok'
#         }
#     )


def deletefromcart(request):
    id = request.POST['cid']
    cart_item = Cart.objects.get(id=id)
    product = cart_item.PRODUCT
    quantity = int(cart_item.Quantity)


    # Update stock for this product
    try:
        stock = Stock.objects.get(product=product)
        current_stock = int(stock.stock_details)
        stock.stock_details = str(current_stock + quantity)
        stock.save()
    except Stock.DoesNotExist:
        # You may want to handle this case, e.g., log it or create a new stock record if needed
        pass

    cart_item.delete()

    return JsonResponse({'status': 'ok'})


from django.http import JsonResponse
from datetime import datetime


def cartpaymentss(request):

    lid = request.POST.get("lid")

    if not lid:
        return JsonResponse({'status': 'error', 'message': 'User ID not provided'})

    cart_items = Cart.objects.filter(USER__USER_id=lid)

    if not cart_items.exists():
        return JsonResponse({'status': 'error', 'message': 'Cart is empty'})

    user = UserAccount.objects.get(USER_id=lid)

    shop_ids = []
    for item in cart_items:
        shop_id = item.PRODUCT.BUSSINESSACCOUNT.id
        if shop_id not in shop_ids:
            shop_ids.append(shop_id)

    for shop_id in shop_ids:
        shop_cart_items = cart_items.filter(PRODUCT__BUSSINESSACCOUNT_id=shop_id)

        total_amount = 0
        now = datetime.now().date()

        for item in shop_cart_items:
            product = item.PRODUCT
            offer = Offers.objects.filter(
                PRODUCT=product,
                Fromdate__lte=now,
                Todate__gte=now
            ).order_by('-Amount').first()

            if offer:
                price = float(offer.Amount)
            else:
                price = float(product.Price)

            total_amount += price * int(item.Quantity)

        order_main = OrderMain()
        order_main.USER = user
        order_main.Date = datetime.now()
        order_main.Amount = str(total_amount)
        order_main.Status = 'paid'
        order_main.SHOP = BussinessAccount.objects.get(id=shop_id)
        order_main.save()

        for item in shop_cart_items:
            order_sub = OrderSub()
            order_sub.PRODUCT = item.PRODUCT
            order_sub.Quantity = item.Quantity
            order_sub.ORDERMAIN = order_main
            order_sub.save()

        payment = ProductPayment()
        payment.ORDERSUB = order_sub   
        payment.Date = datetime.now().date()
        payment.TotalAmount = str(total_amount)
        payment.Status = 'paid'
        payment.save()

        shop_cart_items.delete()

    return JsonResponse({'status': 'ok', 'message': 'Payment successful'})



def user_view_products(request):
    bid = request.POST['bid']
    k = Product.objects.filter(BUSSINESSACCOUNT_id=bid)
    l = []
    for i in k:
        stock = Stock.objects.filter(product=i).first()
        stock_details = stock.stock_details if stock else None

        l.append({
            'id': i.id,
            'Product': i.Product,
            'Amount': i.Price,
            'Category': i.CATEGORY.Categoryname,
            'Details': i.CATEGORY.Details,
            'Photo': i.Photo.url,
            'StockDetails': stock_details,  
        })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})


def user_view_orders(request):
    lid = request.POST['lid']
    print(lid)
    p =ProductPayment.objects.filter(ORDERSUB__ORDERMAIN__USER__USER_id=lid)
    l=[]
    for i in p:
        l.append({
            'id':i.id,
            'ordereddate':i.Date,
            'Amount':i.TotalAmount,
            'Status':i.Status,
            'Quantity':i.ORDERSUB.Quantity,
            'ProductName':i.ORDERSUB.PRODUCT.Product,
            'Productid': i.ORDERSUB.PRODUCT.id,
            'ProductPrice':i.ORDERSUB.PRODUCT.Price,
            'Photo':i.ORDERSUB.PRODUCT.Photo.url,
            'ShopName':i.ORDERSUB.ORDERMAIN.SHOP.Name,
            'ShopEmail':i.ORDERSUB.ORDERMAIN.SHOP.Email,
            'ShopPhone':i.ORDERSUB.ORDERMAIN.SHOP.Phone,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})

def sendproductreview(request):
    rating=request.POST["rating"]
    rev=request.POST["review"]
    lid=request.POST["lid"]
    pid=request.POST["pid"]
    print(pid)

    obj=ProductReview()
    obj.Ratings=rating
    obj.Review=rev
    obj.Date=datetime.now().today()
    obj.USER=UserAccount.objects.get(USER=lid)
    obj.PRODUCT=Product.objects.get(id=pid)
    obj.save()
    return JsonResponse({'status': 'ok'})




def sendservicereview(request):
    rating=request.POST["rating"]
    rev=request.POST["review"]
    lid=request.POST["lid"]
    sid=request.POST["sid"]
    print(sid)

    obj=Review()
    obj.Rating=rating
    obj.Review=rev
    obj.Date=datetime.now().today()
    obj.USER=UserAccount.objects.get(USER=lid)
    obj.SERVICE=Service.objects.get(id=sid)
    obj.save()
    return JsonResponse({'status': 'ok'})


from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai

GOOGLE_API_KEY = 'AIzaSyCvddPiaJ3B9sM1C4IUEH_oyfbGqVeqCFU'
genai.configure(api_key=GOOGLE_API_KEY)

model = None
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
        model = genai.GenerativeModel('gemini-2.5-flash')
        break

def generate_gemini_response(prompt):
    response = model.generate_content(prompt)
    return response.text


@csrf_exempt
def chatss(request):
    if request.method == 'POST':
        user_message = json.loads(request.body).get('message')
        gemini_response = generate_gemini_response(user_message)
        return JsonResponse({'response': gemini_response})


def user_view_fitnescenters(request):
    ad = BussinessAccount.objects.filter(Type='fitness')
    l = []
    for i in ad:
        l.append({'id': i.id,
                  'Name': i.Name,
                  'Email': i.Email,
                  'Phone': i.Phone,
                  'Place': i.Place,
                  'District': i.District,
                  'latitude': i.latitude,
                  'longitude': i.longitude,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})



def user_view_fitnescentersoffers(request):
    fid = request.POST['lid']
    print(fid)
    ad = Fitnessoffers.objects.filter(SERVICE__BUSSINESSACCOUNT_id=fid)
    l = []
    for i in ad:
        l.append({'id': i.id,
                  'OfferName': i.OfferName,
                  'Amount': i.Amount,
                  'Package': i.Package,
                  'Fromdate': i.Startdate,
                  'Todate': i.EndDate,
                  'Details': i.Details,
                  'SERVICEname': i.SERVICE.Servicename,
                  'SERVICEAmount': i.SERVICE.Amount,
                  'Photo': i.SERVICE.Photo.url,
                  })
    print(l)
    return JsonResponse({'status': 'ok', 'data': l})


def user_chat_send(request):

    from_id = request.POST.get("from_id")  
    to_id = request.POST.get("to_id")      
    message = request.POST.get("message")

    import datetime
    d = datetime.datetime.now().date()
    chatobt = chat()
    chatobt.messages = message
    chatobt.TO_ID_id = to_id
    chatobt.FROM_ID_id = from_id
    chatobt.date = d
    chatobt.save()

    return JsonResponse({"status": "ok"})


from django.http import JsonResponse
from django.db.models import Q

def chat_view_user(request):
    from_id = request.POST.get("from_id")
    to_id = request.POST.get("to_id")

    res = chat.objects.filter(
        Q(FROM_ID_id=from_id, TO_ID_id=to_id) | Q(FROM_ID_id=to_id, TO_ID_id=from_id)
    )

    l = []
    for i in res:
        l.append({
            "id": i.id,
            "msg": i.messages,
            "to": i.TO_ID.id,
            "date": i.date,
            "from": i.FROM_ID.id,
        })

    print(l)

    return JsonResponse({"data": l, 'toid': to_id,'status':'ok'})

from textblob import TextBlob 

def user_view_allservices(request):
    k = Service.objects.all()
    l = []
    for i in k:
        reviews = Review.objects.filter(SERVICE=i)
        ratings = []
        sentiments = []
        for review in reviews:
            try:
                rating = float(review.Rating)
            except:
                rating = 0
            ratings.append(rating)
            sentiments.append(TextBlob(review.Review).sentiment.polarity)

        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
        total_ratings = len(ratings)
        avg_sentiment = round(sum(sentiments) / len(sentiments), 2) if sentiments else 0

        score = avg_rating * 0.7 + avg_sentiment * 0.3

        l.append({
            'id': i.id,
            'Servicename': i.Servicename,
            'Amount': i.Amount,
            'Photo': i.Photo.url,
            'Details': i.Details,
            'CATEGORY': i.CATEGORY.Categoryname,
            'AverageRating': avg_rating,
            'TotalRatings': total_ratings,
            'SuggestedScore': score
        })
    l.sort(key=lambda x: x['SuggestedScore'], reverse=True)
    return JsonResponse({'status': 'ok', 'data': l})

        # def user_view_allservices(request):
#     k=Service.objects.all()
#     l = []
#     for i in k:
#         l.append({'id': i.id,
#                   'Servicename': i.Servicename,
#                   'Amount': i.Amount,
#                   'Photo': i.Photo.url,
#                   'Details': i.Details,
#                   'CATEGORY': i.CATEGORY.Categoryname,
#                   })
#     print(l)
#     return JsonResponse({'status': 'ok', 'data': l})




#######################forgotpassword###########################
def ForgotPassword(request):
    return render(request,'forgot_password.html')

def forgotPassword_otp(request):
    if 'email' in request.POST:
        request.session['email'] = request.POST['email']
    email=request.session['email']
    try:
        user=User.objects.get(email=email)
    except User.DoesNotExist:
        messages.warning(request,'Email doesnt match')
        return redirect('/loginindex')
    otp=random.randint(100000,999999)
    request.session['otp']=str(otp)
    request.session['email'] = email

    send_mail('Your Verification Code',
    f'Your verification code is {otp}',
    settings.EMAIL_HOST_USER,
    [email],
    fail_silently=False)
    messages.success(request,'OTP sent To your Mail')
    return redirect('/verifyOtp/')

def verifyOtp(request):
    return render(request,'otpverification.html')

def verifyOtpPost(request):
    entered_otp=request.POST['entered_otp']
    if request.session.get('otp') == entered_otp:
        messages.success(request,'otp verified')
        return redirect('/new_password/')
    else:
        messages.warning(request,'Invalid OTP!!')
        return redirect('/loginindex')

def new_password(request):
    return render(request,'new_password.html')

def changePassword(request):
    newpassword=request.POST['newPassword']
    confirmPassword=request.POST['confirmPassword']
    if newpassword == confirmPassword:
        email=request.session.get('email')
        user = User.objects.get(email=email)
        user.set_password(confirmPassword)
        user.save()
        messages.success(request, 'Password Updated Successfully')
        return redirect('/loginindex')
    else:
        messages.warning(request, 'The password doesnt match!!')
        return redirect('/new_password/')





def forgotpasswordflutter(request):
    email = request.POST['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Email not found'})

    otp = random.randint(100000, 999999)
    PasswordResetOTP.objects.create(email=email, otp=otp)

    send_mail('Your Verification Code',
              f'Your verification code is {otp}',
              settings.EMAIL_HOST_USER,
              [email],
              fail_silently=False)
    return JsonResponse({'status': 'ok', 'message': 'OTP sent'})


def verifyOtpflutterPost(request):
    email = request.POST['email']
    entered_otp = request.POST['entered_otp']
    otp_obj = PasswordResetOTP.objects.filter(email=email).latest('created_at')
    if otp_obj.otp == entered_otp:
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error'})


def changePasswordflutter(request):
    email = request.POST['email']
    newpassword = request.POST['newPassword']
    confirmPassword = request.POST['confirmPassword']
    if newpassword == confirmPassword:
        try:
            user = User.objects.get(email=email)
            user.set_password(confirmPassword)
            user.save()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Passwords do not match'})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
from .models import ProductPayment, ServicePayment, UserAccount

@csrf_exempt
def user_view_all_payments(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'})

    try:
        lid = request.POST.get('lid')  # User login ID
        if not lid:
            return JsonResponse({'status': 'error', 'message': 'Login required'})

        try:
            user_account = UserAccount.objects.get(USER__id=lid)
        except UserAccount.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})

        payments = []

        # === 1. Product Payments ===
        product_payments = ProductPayment.objects.filter(
            ORDERSUB__ORDERMAIN__USER=user_account
        ).select_related('ORDERSUB__ORDERMAIN', 'ORDERSUB__PRODUCT')

        for p in product_payments:
            payments.append({
                'id': p.id,
                'type': 'product',
                'amount': p.TotalAmount,
                'status': p.Status,
                'date': p.Date.strftime('%Y-%m-%d'),
                'description': f"Product Order #{p.ORDERSUB.ORDERMAIN.id}",
                'product_name': p.ORDERSUB.PRODUCT.Product if p.ORDERSUB.PRODUCT else 'N/A',
                'shop_name': p.ORDERSUB.ORDERMAIN.SHOP.Name,
            })

        # === 2. Service Payments ===
        service_payments = ServicePayment.objects.filter(
            SERVICEBOKKING__USER=user_account
        ).select_related('SERVICEBOKKING__SERVICE__BUSSINESSACCOUNT')

        for p in service_payments:
            service = p.SERVICEBOKKING.SERVICE
            payments.append({
                'id': p.id,
                'type': 'service',
                'amount': p.TotalAmount,
                'status': p.Status,
                'date': p.Date.strftime('%Y-%m-%d'),
                'description': f"Service Booking - {service.Servicename}",
                'service_name': service.Servicename,
                'provider_name': service.BUSSINESSACCOUNT.Name,
                'provider_phone': service.BUSSINESSACCOUNT.Phone,
            })

        # Optional: Sort by date (newest first)
        payments.sort(key=lambda x: x['date'], reverse=True)

        return JsonResponse({
            'status': 'ok',
            'data': payments,
            'total_payments': len(payments),
            'message': 'Payments retrieved successfully'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })