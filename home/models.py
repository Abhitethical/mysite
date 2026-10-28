from itertools import product
from django.db import models
from django.contrib.auth.models import User
import datetime
import os
from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(models.Model):
    profile_image = models.ImageField(
        upload_to="profile_images/",
        default="profile_images/default.png",
        blank=True,
        null=True
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    last_login_time = models.DateTimeField(blank=True, null=True)
    last_logout_time = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
    
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CustomerRegistration(models.Model):
    profile_image = models.ImageField(
        upload_to="profile_images/",
        default="profile_images/default.png",
        blank=True,
        null=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    phone_updated = models.BooleanField(default=False)
    address = models.TextField(blank=True)
    out_of_stock_at = models.DateTimeField(
    null=True,
    blank=True
)
    # Registration Date & Time
    created_at = models.DateTimeField(auto_now_add=True)

    # Last Updated
    updated_at = models.DateTimeField(auto_now=True)

    # Login Time
    login_time = models.DateTimeField(null=True, blank=True)

    # Logout Time
    logout_time = models.DateTimeField(null=True, blank=True)

    # Last Login
    last_login = models.DateTimeField(null=True, blank=True)

    # Active Status
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username




def getFileName(requset,filename):
  now_time=datetime.datetime.now().strftime("%Y%m%d%H:%M:%S")
  new_filename="%s%s"%(now_time,filename)
  return os.path.join('uploads/',new_filename)

class Catagory(models.Model):
  name=models.CharField(max_length=150,null=False,blank=False)
  image=models.ImageField(upload_to=getFileName,null=True,blank=True)
  description=models.TextField(max_length=500,null=False,blank=False)
  status=models.BooleanField(default=False,help_text="0-show,1-Hidden")
  created_at=models.DateTimeField(auto_now_add=True)

  def __str__(self) :
    return self.name
class Product(models.Model):
  
  SIZE_CHOICES = (
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'XX Large'),
  )
  category=models.ForeignKey(Catagory,on_delete=models.CASCADE)
  name=models.CharField(max_length=150,null=False,blank=False)
  vendor=models.CharField(max_length=150,null=False,blank=False)
  product_image=models.ImageField(upload_to=getFileName,null=True,blank=True)
  # Additional Images
  product_image2 = models.ImageField(
        upload_to=getFileName,
        null=True,
        blank=True
    )

  product_image3 = models.ImageField(
        upload_to=getFileName,
        null=True,
        blank=True
    )

  product_image4 = models.ImageField(
        upload_to=getFileName,
        null=True,
        blank=True
    )
      # Product Size
  size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        default='M'
    )
   # Coupon Details
  coupon_code = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
  coupon_discount = models.FloatField(
        default=0,
        help_text="Discount amount in ₹"
    )
      # Coupon expiry
  coupon_expiry = models.DateField(
        blank=True,
        null=True,
        help_text="Leave blank for no expiry"
    )

    # Enable/Disable coupon
  coupon_active = models.BooleanField(default=True)
  coupon_used = models.BooleanField(default=False)

  quantity=models.IntegerField(null=False,blank=False)
  original_price=models.FloatField(null=False,blank=False)
  selling_price=models.FloatField(null=False,blank=False)
  description=models.TextField(max_length=500,null=False,blank=False)
  status=models.BooleanField(default=False,help_text="0-show,1-Hidden")
  trending=models.BooleanField(default=False,help_text="0-default,1-Trending")
  created_at=models.DateTimeField(auto_now_add=True)
     # Size Prices
  price_s = models.FloatField(default=200)
  price_m = models.FloatField(default=400)
  price_l = models.FloatField(default=600)
  price_xl = models.FloatField(default=800)
  price_xxl = models.FloatField(default=1000)

  def get_price(self, size):
        prices = {
            'S': self.price_s,
            'M': self.price_m,
            'L': self.price_l,
            'XL': self.price_xl,
            'XXL': self.price_xxl,
        }
        return prices.get(size, self.price_m)
  @property
  def final_price(self):

    if self.coupon_expiry:

        if self.coupon_expiry < timezone.now().date():
            return self.selling_price


    return max(
        0,
        self.selling_price - self.coupon_discount
    )
  def __str__(self) :
    return self.name


from django.contrib.auth.models import User

class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=50)

    used_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'coupon_code')

class Cart(models.Model):
  user=models.ForeignKey(User,on_delete=models.CASCADE)
  product=models.ForeignKey(Product,on_delete=models.CASCADE)
  product_qty=models.IntegerField(null=False,blank=False)
  created_at=models.DateTimeField(auto_now_add=True)

  @property
  def total_cost(self):
    return self.product_qty*self.product.selling_price

  @property
  def total_costed(self):
    return self.product_qty*self.product.original_price

  
class Favourite(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	created_at=models.DateTimeField(auto_now_add=True)

class OrderPlacededx(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
   
    
    class Meta:
        ordering = ['-created_at']  # Newest first. Use ['created_at'] for oldest first

    def __str__(self):
        return f"Order {self.id} - {self.product.name} ({self.status})"


    @property
    def total_costed(self):
        return self.quantity*self.product.selling_price
    
    @property
    def total_costing(self):
        return self.total_costed+self.product.original_price
  

from django.db import models
from django.contrib.auth.models import User
#Advanced admin login security requirements
class AdminProfilez(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="admin_profiles",
    )

    # Verified admin email
    admin_email = models.EmailField(blank=True, default="")
    email_verified = models.BooleanField(default=False)

    # Password failure protection
    failed_password_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    # Password reset security
    password_reset_token_hash = models.CharField(
    max_length=64,
    blank=True,
    default="",
    )
    password_reset_expires_at = models.DateTimeField(
    null=True,
    blank=True,
    )
    # models.py

    password_reset_request_timestamps = models.JSONField(
    default=list,
    blank=True,
    )
    password_reset_requests = models.PositiveIntegerField(default=0)
    password_reset_window_start = models.DateTimeField(
    null=True,
    blank=True,
    )
    password_reset_locked_until = models.DateTimeField(
    null=True,
    blank=True,
    )
    # Email OTP security
    otp_hash = models.CharField(max_length=128, blank=True, default="")
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.PositiveIntegerField(default=0)
    otp_sent_at = models.DateTimeField(null=True, blank=True)
    otp_challenge_id = models.CharField(
        max_length=64, blank=True, default=""
    )

    # Audit information
    last_login_ip = models.GenericIPAddressField(
        null=True, blank=True
    )
    last_login_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def is_locked(self):
        return bool(
            self.locked_until and
            self.locked_until > timezone.now()
        )

    def clear_otp(self):
        self.otp_hash = ""
        self.otp_expires_at = None
        self.otp_sent_at = None
        self.otp_challenge_id = ""
        self.otp_attempts = 0




    
class Placedorderxx(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ('completed', 'Completed'),
    )
    SIZE_CHOICES = (
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'XX Large'),
    )
    size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        default='M'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True )
    

        # ✅ SNAPSHOT FIELDS (IMPORTANT)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_image = models.ImageField(upload_to='order_products/', blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vendor = models.CharField(max_length=150, blank=True, null=True)
 
   
    delivered_date = models.DateTimeField(null=True, blank=True)  # ✅ REQUIRED
    
    
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # You can store address & payment info if you prefer
    name = models.CharField(max_length=300, blank=True, null=True)
    address=models.TextField(max_length=500,null=False,blank=False)
    phone= models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)
    state = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by_admin = models.BooleanField(default=False)
     # ADD THESE TWO

    coupon_code=models.CharField(
        max_length=100,
        null=True,
        blank=True
    )


    coupon_discount=models.FloatField(
        default=0
    )
        # ✅ Track when order placed
    
    total_amount = models.FloatField(default=0)
    # etc.
    class Meta:
        ordering = ['-created_at']  # Newest first. Use ['created_at'] for oldest first
    
    def is_return_available(self):
        if self.status != "delivered":
            return False

        return (timezone.now() - self.created_at) <= timedelta(days=7)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
   
    #@property
    #def total_costed(self):
        return self.quantity*self.product.selling_price

    def total_costed(self):
        if not self.product:
         return 0
        return self.product.selling_price * self.quantity

    @property
    def total_costing(self):
        return self.total_costed+self.product.original_price
  






# models.py
from django.db import models
from django.contrib.auth.models import User



class ReturnRequested(models.Model):

    STATUS_CHOICES = (
        ("resubmitted","resubmitted"),
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("pickup_scheduled", "Pickup Scheduled"),
        ("picked_up", "Picked Up"),
        ("received", "Received"),
        ("inspected", "Inspected"),
        ("refunded", "Refunded"),
    )

    REASON_CHOICES = (
        ("defective", "Defective"),
        ("wrong_item", "Wrong Item"),
        ("not_satisfied", "Not Satisfied"),
        ("other", "Other"),
    )

    order = models.ForeignKey(Placedorderxx, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.CharField(max_length=150, blank=True, null=True)
    
    product_name = models.CharField(max_length=255, blank=True, null=True)
    product_image = models.ImageField(upload_to='order_products/', blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)


    # You can store address & payment info if you prefer
    name = models.CharField(max_length=300, blank=True, null=True)
    address=models.TextField(max_length=500,null=False,blank=False)
    phone= models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)
    state = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to="returns/", blank=True, null=True)
    video = models.FileField(upload_to="returns/videos/", blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="requested")
    reject_reason = models.TextField(blank=True, null=True)
    
    pickup_address = models.TextField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    pickup_time_slot = models.CharField(max_length=100, null=True, blank=True)
    pickup_reason = models.TextField(null=True, blank=True)
    pickup_partner = models.CharField(max_length=255,null=True,blank=True)
    pickup_tracking_id = models.CharField(max_length=255,null=True,blank=True)





# ===============================
    # REFUND DETAILS
    # ===============================

    refund_amount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)

    refund_method = models.CharField(max_length=100, null=True,blank=True)

    transaction_id = models.CharField(max_length=255,null=True,blank=True)

    refund_date = models.DateField(null=True,blank=True)

    seller_name = models.CharField(max_length=255,null=True,blank=True)

    seller_email = models.EmailField(null=True,blank=True)

    refund_approved_by = models.CharField(max_length=255,null=True,blank=True)

    # RESUBMISSION
    resubmit_reason = models.CharField(max_length=255,blank=True,null=True)

    resubmit_description = models.TextField(blank=True,null=True)

    resubmit_image = models.ImageField(
        upload_to='resubmit/',
        blank=True,
        null=True
    )

    resubmit_video = models.FileField(
        upload_to='resubmit/videos/',
        blank=True,
        null=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_return_allowed(self):
        if self.order.status == "Completed" and self.order.delivered_at:
         return timezone.now() <= self.order.delivered_at + timedelta(days=7)
        return False


class RefundTransaction(models.Model):

    METHOD_CHOICES = (
        ("original", "Original Payment"),
        ("wallet", "Wallet"),
        ("bank", "Bank Transfer"),
    )

    return_request = models.OneToOneField(ReturnRequested, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    



from datetime import timedelta
from django.utils import timezone

def can_return(order):
    if order.status != "completed":
        return False

    if not order.delivered_date:
        return False

    return timezone.now() <= order.delivered_date + timedelta(days=7)





# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class PasswordResetOTPds(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    otp_token = models.UUIDField(default=uuid.uuid4, editable=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)  # 5 minutes validity






class Orderz(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"





from django.db import models

class SiteVisit(models.Model):
    ip_address = models.GenericIPAddressField()
    visit_date = models.DateField(auto_now_add=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    spent_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.ip_address} - {self.visit_date}"



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    details = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Activity"




from django.db import models
from django.contrib.auth.models import User



class CustomerLoginLogout(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.customer.full_name} | Login: {self.login_time} | Logout: {self.logout_time}"






from django.db import models

class Sale(models.Model):
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return self.product_name






from django.db import models
from django.contrib.auth.models import User

class UserLoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)  # blank if user hasn't logged out yet

    def __str__(self):
        return f"{self.user.username} - {self.login_time.date()} | {self.login_time.time()} - {self.logout_time.time() if self.logout_time else 'Still Logged In'}"
















# models.py

from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.OneToOneField(Placedorderxx, on_delete=models.CASCADE)

    rating = models.IntegerField()  # 1–5
    comment = models.TextField()

    image = models.ImageField(upload_to='reviews/images/', null=True, blank=True)
    video = models.FileField(upload_to='reviews/videos/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"









#saller


from django.db import models
from django.contrib.auth.models import User

class SellerProfile(models.Model):
    BUSINESS_TYPES = [
        ('individual', 'Individual'),
        ('proprietorship', 'Proprietorship'),
        ('partnership', 'Partnership'),
        ('llp', 'LLP'),
        ('private_limited', 'Private Limited Company'),
        ('opc', 'One Person Company'),
    ]
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked'),
    )
   
    business_type = models.CharField(
        max_length=30,
        choices=BUSINESS_TYPES,
        default='individual'
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='seller/profile/',blank=True,null=True)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
   
    company_name = models.CharField(max_length=255)

    mobile_number = models.CharField(max_length=15)
    
   
    address = models.TextField()
    
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    

    registered_office_proof = models.FileField(
        upload_to='seller/office/',
        blank=True,
        null=True
    )
    
    
    aadhar_number = models.CharField(max_length=20)
    aadhar_image = models.ImageField(upload_to='seller/aadhar/')

    
    pan_number = models.CharField(max_length=20)
    pan_image = models.ImageField(upload_to='seller/pan/')

 
    

   

    email = models.EmailField(max_length=255, null=True, blank=True)


        # Partner / Director KYC
    partner_kyc_document = models.FileField(
        upload_to='seller/kyc/partners/',
        blank=True,
        null=True
    )

    director_kyc_document = models.FileField(
        upload_to='seller/kyc/directors/',
        blank=True,
        null=True
    )
   
   # 🔐 Security & Lock Fields
    login_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)


    # Security Questions
    wedding_anniversary = models.DateField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    
    verification_status = models.CharField(
        max_length=20,
        choices=BUSINESS_TYPES,
        default='pending'
    )
     # ADMIN STATUS
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # =========================
    # TAX INFORMATION
    # =========================
    gstinnamber = models.CharField(
        max_length=30,
        blank=True
    )

    gst_certificate = models.FileField(
        upload_to='seller/gst/',
        blank=True,
        null=True
    )

    tax_classification = models.CharField(
        max_length=100,
        blank=True
    )

    # =========================
    # LEGAL DOCUMENTS
    # =========================
    incorporation_certificate = models.FileField(
        upload_to='seller/legal/incorporation/',
        blank=True,
        null=True
    )

    partnership_deed = models.FileField(
        upload_to='seller/legal/partnership/',
        blank=True,
        null=True
    )


  

    llp_agreement = models.FileField(
        upload_to='seller/legal/llp/',
        blank=True,
        null=True
    )

    moa_document = models.FileField(
        upload_to='seller/legal/moa/',
        blank=True,
        null=True
    )

    aoa_document = models.FileField(
        upload_to='seller/legal/aoa/',
        blank=True,
        null=True
    )

    udyam_registration = models.FileField(
        upload_to='seller/legal/udyam/',
        blank=True,
        null=True
    )

    shop_establishment_license = models.FileField(
        upload_to='seller/legal/shop_license/',
        blank=True,
        null=True
    )

    trademark_certificate = models.FileField(
        upload_to='seller/legal/trademark/',
        blank=True,
        null=True
    )

    brand_authorization_letter = models.FileField(
        upload_to='seller/legal/authorization/',
        blank=True,
        null=True
    )

    business_license = models.FileField(
        upload_to='seller/legal/license/',
        blank=True,
        null=True
    )

    # =========================
    # AGREEMENTS
    # =========================
    terms_accepted = models.BooleanField(
        default=False
    )

    privacy_policy_accepted = models.BooleanField(
        default=False
    )

    return_policy_accepted = models.BooleanField(
        default=False
    )

    commission_agreement_accepted = models.BooleanField(
        default=False
    )

    # =========================
    # VERIFICATION
    # =========================
    mobile_verified = models.BooleanField(
        default=False
    )

    email_verified = models.BooleanField(
        default=False
    )

    bank_verified = models.BooleanField(
        default=False
    )

    gst_verified = models.BooleanField(
        default=False
    )


    #LOCATION TACK

    latitude = models.DecimalField(
    max_digits=10,
    decimal_places=7,
    null=True,
    blank=True
    )

    longitude = models.DecimalField(
    max_digits=10,
    decimal_places=7,
    null=True,
    blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    live_location = models.CharField(max_length=255, default="unknown")

    rejection_reason = models.TextField(
        blank=True,
        default=''
    )
    account_block_reason = models.TextField(
    blank=True,
    default="",
    verbose_name="Account Block Reason"
)
    liveface_scan = models.ImageField(upload_to="seller_faces/", null=True, blank=True)
    def __str__(self):
        return self.user.username



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SellerPasswordResetToken(models.Model):
    seller = models.ForeignKey(
        "SellerProfile",
        on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )

    token_hash = models.CharField(
        max_length=128,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    used = models.BooleanField(
        default=False
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def is_valid(self):
        return (
            not self.used
            and timezone.now() < self.expires_at
        )

    def mark_used(self):
        self.used = True
        self.used_at = timezone.now()
        self.save(
            update_fields=["used", "used_at"]
        )

    def __str__(self):
        return f"Password reset - {self.seller.user.username}"


    

from django.db import models
from django.contrib.auth.models import User

class SellerLoginHistory(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def duration(self):
        if self.logout_time:
            return self.logout_time - self.login_time
        return None










    

 
 



 


   





   




from django.contrib import admin
from .models import SellerProfile

@admin.register(SellerProfile)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'status')
    list_filter = ('status',)
    actions = ['approve_seller', 'reject_seller', 'block_seller']

    def approve_seller(self, request, queryset):
        queryset.update(status='approved')

    def reject_seller(self, request, queryset):
        queryset.update(status='rejected')

    def block_seller(self, request, queryset):
        queryset.update(status='blocked')








from django.db import models
from django.contrib.auth.models import User

class SellerBankDetailxx(models.Model):
    BANK_STATUS = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )

    seller = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()
    account_number = models.CharField(max_length=20)  # ✅ Add this line
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    bank_code = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=BANK_STATUS, default='pending')
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.username} - {self.bank_name}"
















from django.contrib.auth.models import User
from django.db import models
from datetime import timedelta

class UserProfiles(models.Model):
    ROLE_CHOICES = [
        ('SELLER', 'Seller'),
        ('ADMIN', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='SELLER')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Tickets(models.Model):
    CATEGORY_CHOICES = [
        ('PAYMENT', 'Payment'),
        ('ORDER', 'Order'),
        ('RETURN', 'Return'),
        ('ACCOUNT', 'Account'),
        ('LOGISTICS', 'Logistics'),
        ('TECHNICAL', 'Technical'),
        ('OTHER', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('WAITING', 'Waiting for Seller'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),  # ✅ NEW
    ]



    cancel_reason = models.TextField(blank=True, null=True)  # ✅ NEW
    cancelled_at = models.DateTimeField(blank=True, null=True)  # ✅ NEW
    cancelled_at = models.DateTimeField(blank=True, null=True)

    # Ticket info
    ticket_number = models.CharField(max_length=20, unique=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    email = models.EmailField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    department = models.CharField(max_length=100, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.FileField(upload_to='tickets/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    admin_description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


   # ✅ NEW FIELD (Company system)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets"
    )
    resolved_at = models.DateTimeField(blank=True, null=True)  # ✅ Track resolution time

        # ✅ Auto Ticket Number Generator
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = "TKT-" + uuid.uuid4().hex[:8].upper()

        # If resolved, set resolved time
        if self.status == "RESOLVED" and not self.resolved_at:
            self.resolved_at = timezone.now()
        
                # Auto cancelled time
        if self.status == "CANCELLED" and not self.cancelled_at:
            self.cancelled_at = timezone.now()

        super().save(*args, **kwargs)
   

    def can_cancel(self):
        """Allow cancel only within 24 hours and if not resolved/closed"""
        if self.status in ['RESOLVED', 'CLOSED', 'CANCELLED']:
            return False
        
        return timezone.now() <= self.created_at + timedelta(hours=24)

    
    def __str__(self):
        return f"{self.ticket_number} - {self.title}"




class TicketReply(models.Model):
    ticket = models.ForeignKey(Tickets, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply - {self.ticket.ticket_number}"



















# models.py
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class SellerPasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    otp_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"














import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SellerUnlockOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    otp_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.username} Unlock OTP"














































from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def getFileName(instance, filename):
    """
    Generate a safe upload path for advertisement images.
    """
    return f"advertisements/images/{filename}"


class Advertisementx(models.Model):

    STATUS_CHOICES = (
        ("PENDING_PAYMENT", "Pending Payment"),
        ("PAYMENT_SUCCESS", "Payment Success"),
        ("WAITING_APPROVAL", "Waiting Approval"),
        ("APPROVED", "Approved"),
        ("RUNNING", "Running"),
        ("EXPIRED", "Expired"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    )

    PAYMENT_STATUS = (
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    )

    PAYMENT_METHODS = (
        ("RAZORPAY", "Razorpay"),
        ("STRIPE", "Stripe"),
        ("PAYPAL", "PayPal"),
    )

    PLAN_CHOICES = (
        ("BASIC", "Basic"),
        ("STANDARD", "Standard"),
        ("PREMIUM", "Premium"),
        ("GOLD", "Gold"),
        ("PLATINUM", "Platinum"),
    )

    PLAN_DETAILS = {
        "BASIC": {
            "duration": 1,
            "amount": 500,
        },
        "STANDARD": {
            "duration": 3,
            "amount": 1250,
        },
        "PREMIUM": {
            "duration": 7,
            "amount": 2500,
        },
        "GOLD": {
            "duration": 15,
            "amount": 4500,
        },
        "PLATINUM": {
            "duration": 30,
            "amount": 8000,
        },
    }

    # =========================================================
    # SELLER
    # =========================================================

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="advertisementx_seller",
    )

    # =========================================================
    # PRODUCT
    # =========================================================

    product_image = models.ImageField(
        upload_to=getFileName,
        null=True,
        blank=True,
    )

    # =========================================================
    # SCHEDULE
    # =========================================================

    start_datetime = models.DateTimeField(
        null=True,
        blank=True,
    )

    end_datetime = models.DateTimeField(
        null=True,
        blank=True,
    )

    # =========================================================
    # ADVERTISEMENT DETAILS
    # =========================================================

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    video = models.FileField(
        upload_to="advertisements/videos/",
        blank=True,
        null=True,
    )

    thumbnail = models.ImageField(
        upload_to="advertisements/thumbnails/",
        blank=True,
        null=True,
    )

    # =========================================================
    # PLAN
    # =========================================================

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
    )

    duration = models.PositiveIntegerField(
        default=1,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    # =========================================================
    # DATE ONLY
    # =========================================================

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    # =========================================================
    # STATUS
    # =========================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING_PAYMENT",
    )

    # =========================================================
    # PAYMENT
    # =========================================================

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        blank=True,
    )

    payment_id = models.CharField(
        max_length=200,
        blank=True,
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="PENDING",
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # =========================================================
    # ADMIN APPROVAL
    # =========================================================

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_advertisementx",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rejected_reason = models.TextField(
        blank=True,
        null=True,
    )

    # =========================================================
    # RENEWAL
    # =========================================================

    is_renewed = models.BooleanField(
        default=False,
    )

    renewal_date = models.DateField(
        null=True,
        blank=True,
    )

    renewal_expiry = models.DateField(
        null=True,
        blank=True,
    )

    # =========================================================
    # ANALYTICS
    # =========================================================

    views = models.PositiveIntegerField(
        default=0,
    )

    clicks = models.PositiveIntegerField(
        default=0,
    )

    ctr = models.FloatField(
        default=0,
    )

    featured = models.BooleanField(
        default=False,
    )

    # =========================================================
    # INVOICE
    # =========================================================

    invoice_pdf = models.FileField(
        upload_to="advertisements/invoices/",
        blank=True,
        null=True,
    )

    # =========================================================
    # AUDIT
    # =========================================================

    audit_log = models.JSONField(
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # =========================================================
    # AUTOMATIC STATUS
    # =========================================================

    def update_status(self, save=True):
        """
        Automatically update APPROVED/RUNNING/EXPIRED
        based on start_datetime and end_datetime.

        These statuses are manually controlled:
            PENDING_PAYMENT
            PAYMENT_SUCCESS
            WAITING_APPROVAL
            REJECTED
            CANCELLED
        """

        manual_statuses = {
            "PENDING_PAYMENT",
            "PAYMENT_SUCCESS",
            "WAITING_APPROVAL",
            "REJECTED",
            "CANCELLED",
        }

        if self.status in manual_statuses:
            return self.status

        if not self.start_datetime or not self.end_datetime:
            return self.status

        now = timezone.now()

        if now < self.start_datetime:
            new_status = "APPROVED"

        elif self.start_datetime <= now < self.end_datetime:
            new_status = "RUNNING"

        else:
            new_status = "EXPIRED"

        if self.status != new_status:
            self.status = new_status

            if save:
                self.save(
                    update_fields=["status"]
                )

        return self.status

    # =========================================================
    # CURRENT STATUS
    # =========================================================

    @property
    def current_status(self):
        """
        Calculate current status immediately without waiting
        for a background task.
        """

        manual_statuses = {
            "PENDING_PAYMENT",
            "PAYMENT_SUCCESS",
            "WAITING_APPROVAL",
            "REJECTED",
            "CANCELLED",
        }

        if self.status in manual_statuses:
            return self.status

        if not self.start_datetime or not self.end_datetime:
            return self.status

        now = timezone.now()

        if now < self.start_datetime:
            return "APPROVED"

        elif self.start_datetime <= now < self.end_datetime:
            return "RUNNING"

        return "EXPIRED"

    def __str__(self):
        return self.title









class AdvertisementRenewalx(models.Model):

    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('RUNNING', 'Running'),
        ('EXPIRED', 'Expired'),
        ('REJECTED', 'Rejected'),
    )

    PAYMENT_METHODS = (
        ('RAZORPAY', 'Razorpay'),
        ('STRIPE', 'Stripe'),
        ('PAYPAL', 'PayPal'),
    )


    advertisement = models.ForeignKey(
        Advertisementx,
        on_delete=models.CASCADE,
        related_name="renewals"
    )


    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="advertisement_renewals"
    )


    plan = models.CharField(
        max_length=20
    )


    duration = models.PositiveIntegerField()


    amounts = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="PENDING"
    )


    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        blank=True
    )

    
    payment_id = models.CharField(
        max_length=200,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True
    )


    end_date = models.DateTimeField(
        null=True,
        blank=True
    )


    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    renewed_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:
        ordering = ['-renewed_at']


    def __str__(self):
        return f"{self.advertisement.title} Renewal"
    def update_status(self):

        now = timezone.now()

        if self.start_date and self.end_date:

            if now < self.start_date:
                new_status = "PENDING"

            elif self.start_date <= now <= self.end_date:
                new_status = "RUNNING"

            else:
                new_status = "EXPIRED"

            if self.status != new_status:
                self.status = new_status
                self.save(update_fields=["status"])







































import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class VisitorProfile(models.Model):
    visitor_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="visitor_profiles",
    )
    first_visit = models.DateTimeField(default=timezone.now)
    last_visit = models.DateTimeField(default=timezone.now, db_index=True)
    total_visits = models.PositiveIntegerField(default=0)
    first_seen_path = models.CharField(max_length=500, blank=True)
    is_bot = models.BooleanField(default=False)

    class Meta:
        ordering = ["-last_visit"]

    def __str__(self):
        return str(self.user or self.visitor_id)


class VisitorSession(models.Model):
    class Role(models.TextChoices):
        GUEST = "guest", "Guest"
        CUSTOMER = "customer", "Customer"
        SELLER = "seller", "Seller"
        ADMIN = "admin", "Administrator"
        STAFF = "staff", "Staff"
        BOT = "bot", "Search bot"

    session_key = models.CharField(max_length=100, unique=True)
    visitor = models.ForeignKey(
        VisitorProfile, on_delete=models.CASCADE, related_name="sessions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.GUEST)
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_seen = models.DateTimeField(default=timezone.now, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    current_url = models.CharField(max_length=1000, blank=True)
    current_title = models.CharField(max_length=300, blank=True)
    last_activity = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=30, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    referrer = models.URLField(max_length=1000, blank=True)
    campaign_source = models.CharField(max_length=200, blank=True)
    landing_url = models.CharField(max_length=1000, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    engagement_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-last_seen"]
        indexes = [
            models.Index(fields=["is_active", "last_seen"]),
            models.Index(fields=["role", "started_at"]),
        ]

    @property
    def duration_seconds(self):
        end = self.ended_at or timezone.now()
        return max(0, int((end - self.started_at).total_seconds()))

    def __str__(self):
        return f"{self.role}: {self.session_key}"


class PageVisit(models.Model):
    session = models.ForeignKey(
        VisitorSession, on_delete=models.CASCADE, related_name="page_visits"
    )
    path = models.CharField(max_length=1000, db_index=True)
    title = models.CharField(max_length=300, blank=True)
    entered_at = models.DateTimeField(default=timezone.now, db_index=True)
    exited_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    is_entry = models.BooleanField(default=False)
    is_exit = models.BooleanField(default=False)
    status_code = models.PositiveSmallIntegerField(default=200)

    class Meta:
        ordering = ["-entered_at"]
        indexes = [models.Index(fields=["path", "entered_at"])]

    def __str__(self):
        return self.path


class VisitorEvent(models.Model):
    session = models.ForeignKey(
        VisitorSession, on_delete=models.CASCADE, related_name="events"
    )
    name = models.CharField(max_length=100, db_index=True)
    category = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    path = models.CharField(max_length=1000, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)


class LoginHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    session = models.ForeignKey(
        VisitorSession, null=True, blank=True, on_delete=models.SET_NULL
    )
    event = models.CharField(max_length=40, db_index=True)
    role = models.CharField(max_length=20, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    method = models.CharField(max_length=50, blank=True)
    details = models.JSONField(default=dict, blank=True)


class VisitorDevice(models.Model):
    session = models.OneToOneField(
        VisitorSession, on_delete=models.CASCADE, related_name="device"
    )
    device_type = models.CharField(max_length=30, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    screen_width = models.PositiveIntegerField(null=True, blank=True)
    screen_height = models.PositiveIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class SecurityAuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    session = models.ForeignKey(
        VisitorSession, null=True, blank=True, on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=120, db_index=True)
    severity = models.CharField(max_length=20, default="info")
    target = models.CharField(max_length=300, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)


class TrafficSource(models.Model):
    session = models.OneToOneField(
        VisitorSession, on_delete=models.CASCADE, related_name="traffic_source"
    )
    referrer = models.URLField(max_length=1000, blank=True)
    source = models.CharField(max_length=200, blank=True)
    medium = models.CharField(max_length=200, blank=True)
    campaign = models.CharField(max_length=200, blank=True)
    landing_url = models.CharField(max_length=1000, blank=True)