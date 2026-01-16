from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class BussinessAccount(models.Model):
    Name = models.CharField(max_length=100)
    Email = models.CharField(max_length=50)
    Phone = models.CharField(max_length=50)
    Place = models.CharField(max_length=50)
    District = models.CharField(max_length=530)
    Pin = models.CharField(max_length=50)
    status = models.CharField(max_length=50,default='pending')
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    Photo = models.FileField(upload_to='business_photos/')
    Proof = models.FileField(upload_to='business_proofs/')
    Type = models.CharField(max_length=50)
    USER=models.OneToOneField(User,on_delete=models.CASCADE)

class UserAccount(models.Model):
    Name = models.CharField(max_length=100)
    Email = models.CharField(max_length=50)
    Phone = models.CharField(max_length=50)
    Photo = models.CharField(max_length=250)
    Place = models.CharField(max_length=50)
    District = models.CharField(max_length=50)
    Pin = models.CharField(max_length=50)
    USER=models.OneToOneField(User,on_delete=models.CASCADE)

class Category(models.Model):
    Categoryname = models.CharField(max_length=100)
    Details = models.CharField(max_length=100)


class Service(models.Model):
    Servicename = models.CharField(max_length=100)
    Amount = models.CharField(max_length=100)
    Photo = models.FileField(upload_to='service_photos/')
    Details = models.CharField(max_length=100)
    CATEGORY=models.ForeignKey(Category, on_delete=models.CASCADE)
    BUSSINESSACCOUNT=models.ForeignKey(BussinessAccount, on_delete=models.CASCADE)

class Complaints(models.Model):
    Date = models.DateTimeField()
    Complaints =  models.CharField(max_length=100)
    USER=models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    Status =  models.CharField(max_length=100, default="pending")
    Reply =  models.CharField(max_length=100, default="pending")


class Review(models.Model):
    Date =  models.DateField()
    Review =  models.CharField(max_length=100)
    Rating =  models.CharField(max_length=100)
    USER=models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    SERVICE=models.ForeignKey(Service,on_delete=models.CASCADE)

class AvilableStatus(models.Model):
    Date = models.DateTimeField()
    SERVICE=models.ForeignKey(Service,on_delete=models.CASCADE)
    Status =  models.CharField(max_length=100)
    Fromtime =  models.CharField(max_length=100)
    Totime =  models.CharField(max_length=100)



class Product(models.Model):
    Product =  models.CharField(max_length=100)
    Price =  models.CharField(max_length=100)
    Photo =  models.FileField(upload_to='product_photos/')
    BUSSINESSACCOUNT=models.ForeignKey(BussinessAccount, on_delete=models.CASCADE)
    CATEGORY=models.ForeignKey(Category,on_delete=models.CASCADE)


class Stock(models.Model):
    stock_details=models.CharField(max_length=30)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)

class OrderMain(models.Model):
    Date = models.DateTimeField()
    USER=models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    Amount =  models.CharField(max_length=100)
    Status =  models.CharField(max_length=100)
    SHOP=models.ForeignKey(BussinessAccount,on_delete=models.CASCADE)


class OrderSub(models.Model):
    PRODUCT=models.ForeignKey(Product,on_delete=models.CASCADE)
    Quantity =  models.CharField(max_length=100)
    ORDERMAIN=models.ForeignKey(OrderMain,on_delete=models.CASCADE)


class Cart(models.Model):
    Date = models.DateTimeField()
    USER=models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    PRODUCT=models.ForeignKey(Product,on_delete=models.CASCADE)
    Quantity =  models.CharField(max_length=100)


class ProductReview(models.Model):
    USER=models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    PRODUCT=models.ForeignKey(Product,on_delete=models.CASCADE)
    Date = models.DateField()
    Ratings = models.CharField(max_length=100)
    Review = models.CharField(max_length=100)


class ProductPayment(models.Model):
    ORDERSUB=models.ForeignKey(OrderSub,on_delete=models.CASCADE)
    Date = models.DateField()
    TotalAmount = models.CharField(max_length=100)
    Status = models.CharField(max_length=100)

class Offers(models.Model):
    PRODUCT=models.ForeignKey(Product,on_delete=models.CASCADE)
    Offername = models.CharField(max_length=100)
    Amount = models.CharField(max_length=100)
    Fromdate = models.DateField()
    Todate = models.DateField()
    Details = models.CharField(max_length=100)



class Slot(models.Model):
    Date = models.DateField()
    Status = models.CharField(max_length=100)
    Amount = models.CharField(max_length=100)
    SlotNumber = models.CharField(max_length=100)
    AVILABLE = models.ForeignKey(AvilableStatus, on_delete=models.CASCADE)



class BookSlot(models.Model):
    USER = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    SLOT = models.ForeignKey(Slot, on_delete=models.CASCADE)
    Date = models.DateField()
    Status = models.CharField(max_length=100)

class BookSlotpayment(models.Model):
    BOOKSLOT = models.ForeignKey(BookSlot, on_delete=models.CASCADE)
    Date = models.DateField()
    Status = models.CharField(max_length=100)
    Amount = models.CharField(max_length=100)

class Fitnessoffers(models.Model):
    OfferName = models.CharField(max_length=100)
    Amount = models.CharField(max_length=50)
    Package = models.CharField(max_length=50)
    Startdate = models.DateField()
    EndDate = models.DateField()
    Details = models.CharField(max_length=50)
    SERVICE=models.ForeignKey(Service,on_delete=models.CASCADE)


class Specialisation(models.Model):
    Name = models.CharField(max_length=100)
    TotalAmount = models.CharField(max_length=100)
    Details = models.CharField(max_length=100)
    FITNESS = models.ForeignKey(BussinessAccount, on_delete=models.CASCADE)


class ServiceBooking(models.Model):
    USER = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    SERVICE = models.ForeignKey(Service, on_delete=models.CASCADE)
    Date = models.DateField()
    Status = models.CharField(max_length=100)


class ServicePayment(models.Model):
    SERVICEBOKKING=models.ForeignKey(ServiceBooking,on_delete=models.CASCADE)
    Date  = models.DateField()
    TotalAmount = models.CharField(max_length=100)
    Status = models.CharField(max_length=100)

class Facility(models.Model):
    FITNESS=models.ForeignKey(BussinessAccount,on_delete=models.CASCADE)
    facilityName = models.CharField(max_length=100)
    Photo = models.FileField(upload_to='facility_photos/')
    Details = models.CharField(max_length=100)

class AspectFeedBack(models.Model):
    Date = models.DateTimeField()
    Feedback =  models.CharField(max_length=100)
    USER=models.ForeignKey(UserAccount,on_delete=models.CASCADE)

class FeedBack(models.Model):
    Date = models.DateTimeField()
    Feedback =  models.CharField(max_length=100)
    USER=models.ForeignKey(UserAccount,on_delete=models.CASCADE)

class chat(models.Model):
    FROM_ID=models.ForeignKey(User,on_delete=models.CASCADE,related_name='user1')
    TO_ID=models.ForeignKey(User,on_delete=models.CASCADE,related_name='user2')
    messages =  models.CharField(max_length=100)
    date =  models.DateField(max_length=100)

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)