from django.http import  JsonResponse
from django.shortcuts import redirect, render
from home.forms import CustomUserForm
from . models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import json

from django.utils import timezone

def cookiepolicy (request):
    return render(request,'cookiepolicy.html')
def termsconditions (request):
    return render(request,'termsconditions.html')
def privacypolicy (request):
    return render(request,'privacypolicy.html')

def returnpolicy (request):
    return render(request,'returnpolicy.html')

def shipping(request):
    return render(request,'shipping.html')


def helpcenter(request):
    return render(request,'helpcenter.html')

def contactus(request):
    return render(request,'contactus.html')

def homex(request):
    products = Product.objects.all()
    return render(request,'index.html',{'Producte': products})



from django.shortcuts import render
from django.utils import timezone


def home(request):

    products = Product.objects.all()



    ads = Advertisementx.objects.filter(

        status__in=[
            "APPROVED",
            "RUNNING"
        ],

        payment_status="PAID",

        end_date__gte=timezone.now()

    ).order_by(

        "paid_at"

    )



    return render(

        request,

        "index.html",

        {

        "Producte":products,

        "banners":ads

        }

    )


from django.http import JsonResponse



def ad_view(request,id):

    ad=Advertisementx.objects.get(id=id)

    ad.views +=1

    ad.save(update_fields=[
        "views"
    ])


    return JsonResponse(
        {
        "status":"ok"
        }
    )





def ad_click(request,id):

    ad=Advertisementx.objects.get(id=id)

    ad.clicks +=1

    ad.save(update_fields=[
        "clicks"
    ])


    return JsonResponse(
        {
        "status":"ok"
        }
    )
#register



import io
import os
import uuid
import logging

from PIL import Image, UnidentifiedImageError

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.http import Http404
from django.shortcuts import redirect, render
from django.core.files.base import ContentFile

from .forms import CustomUserForm, CustomerRegistrationForm
from .models import CustomerRegistration

logger = logging.getLogger(__name__)


def register(request):

    # -----------------------------------------
    # Already logged-in users
    # -----------------------------------------
    if request.user.is_authenticated:
        return redirect("/")

    user_form = CustomUserForm()
    customer_form = CustomerRegistrationForm()

    if request.method == "POST":

        user_form = CustomUserForm(request.POST)

        customer_form = CustomerRegistrationForm(
            request.POST,
            request.FILES
        )

        if user_form.is_valid() and customer_form.is_valid():

            try:

                # =========================================
                # CREATE USER
                # =========================================
                user = user_form.save(commit=False)

                user.email = user_form.cleaned_data["email"]

                user.save()

                # =========================================
                # CREATE CUSTOMER
                # =========================================
                customer = customer_form.save(commit=False)

                customer.user = user
                customer.email = user.email

                # =========================================
                # SECURE PROFILE IMAGE PROCESSING
                # =========================================
                uploaded_image = customer_form.cleaned_data.get(
                    "profile_image"
                )

                if uploaded_image:

                    secure_image = secure_profile_image(
                        uploaded_image
                    )

                    customer.profile_image.save(
                        secure_image["name"],
                        secure_image["file"],
                        save=False
                    )

                customer.save()

                # =========================================
                # SEND EMAIL
                # =========================================
                try:

                    send_registration_email(user)

                except Exception as email_error:

                    logger.exception(
                        "Registration email failed: %s",
                        email_error
                    )

                    messages.warning(
                        request,
                        "Registration successful, but email could not be sent."
                    )

                messages.success(
                    request,
                    "Registration Successful! Please Login."
                )

                return redirect("/login")

            except Exception as e:

                logger.exception(
                    "Customer registration failed: %s",
                    e
                )

                raise Http404(
                    "Something went wrong during registration."
                )

    context = {
        "user_form": user_form,
        "customer_form": customer_form,
    }

    return render(
        request,
        "register.html",
        context
    )


def secure_profile_image(uploaded_file):
    """
    Securely process a user-uploaded profile image.

    - Limits size
    - Validates actual image format
    - Loads the complete image
    - Rejects suspicious/unsupported formats
    - Re-encodes the image
    - Generates a random filename
    """

    MAX_SIZE = 5 * 1024 * 1024
    MAX_PIXELS = 20_000_000

    # -----------------------------------------
    # File size
    # -----------------------------------------
    if uploaded_file.size > MAX_SIZE:
        raise ValueError(
            "Profile image is too large."
        )

    try:

        uploaded_file.seek(0)

        image = Image.open(uploaded_file)

        # Verify structure
        image.verify()

        uploaded_file.seek(0)

        # Open again
        image = Image.open(uploaded_file)

        if image.format not in {
            "JPEG",
            "PNG",
            "WEBP"
        }:
            raise ValueError(
                "Unsupported image format."
            )

        # -----------------------------------------
        # Pixel limit
        # -----------------------------------------
        if image.width * image.height > MAX_PIXELS:
            raise ValueError(
                "Image dimensions are too large."
            )

        # -----------------------------------------
        # Fully decode image
        # -----------------------------------------
        image.load()

        # -----------------------------------------
        # Convert to safe RGB/RGBA
        # -----------------------------------------
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        # -----------------------------------------
        # Re-encode image
        #
        # This removes original metadata and
        # embedded non-image data.
        # -----------------------------------------
        output = io.BytesIO()

        if image.mode == "RGBA":

            image.save(
                output,
                format="WEBP",
                quality=88,
                method=6
            )

        else:

            image.save(
                output,
                format="WEBP",
                quality=88,
                method=6
            )

        output.seek(0)

        # -----------------------------------------
        # Random server-side filename
        # -----------------------------------------
        random_name = (
            f"profile_{uuid.uuid4().hex}.webp"
        )

        return {
            "name": random_name,
            "file": ContentFile(
                output.read(),
                name=random_name
            )
        }

    except (
        UnidentifiedImageError,
        OSError,
        ValueError
    ) as error:

        logger.warning(
            "Rejected profile image: %s",
            error
        )

        raise ValueError(
            "The uploaded profile image is invalid."
        )

    finally:

        uploaded_file.seek(0)




def login_page(request):

    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            customer = CustomerRegistration.objects.get(user=user)

            customer.last_login = user.last_login
            customer.login_time = timezone.now()
            customer.is_active = True
            customer.save()

            messages.success(request, "Logged in Successfully")
            return redirect("/")

        else:
            messages.error(request, "Invalid Username or Password")
            return redirect("/login")

    return render(request, "login.html")











from django.utils import timezone

def logout_view(request):
    if request.user.is_authenticated:
        print("Current User:", request.user)

        try:
            customer = CustomerRegistration.objects.get(user=request.user)

            print("Customer Found:", customer)

            customer.logout_time = timezone.now()
            customer.is_active = False
            customer.save()

            print("Saved Logout Time:", customer.logout_time)

        except CustomerRegistration.DoesNotExist:
            print("CustomerRegistration record not found.")

        logout(request)
        messages.success(request, "Logged Out Successfully")

    return redirect("/login")

# product add to card


def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)


def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      #print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)




# card page favvi page 

def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"fav.html",{"fav":fav})
  else:
    return redirect("/")

def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")


def cart_paged(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,"carted.html",{"cart":cart})
  else:
    return redirect("home")


def remove_cart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/carted")





from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Cart, Placedorderxx, Product  # Make sure Product model is imported
from .forms import CheckoutForm
from django.db import transaction




from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import render, redirect

GST_RATE = Decimal("0.03")


def checkouts(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect("home")

    def calculate_totals(cart_items, discount=Decimal("0")):
        net = Decimal("0")

        for item in cart_items:
            net += Decimal(item.product.selling_price) * item.product_qty

        gst = net * GST_RATE
        grand = net + gst - discount

        return net, gst, max(grand, Decimal("0"))

    if request.method == "POST":
        step = request.POST.get("step")

        # ================= STEP 1 =================
        if step == "1":
            form = CheckoutForm(request.POST)

            if form.is_valid():
                request.session["checkout_data"] = form.cleaned_data

                net, gst, grand = calculate_totals(cart_items)

                return render(request, "checkout_confirm.html", {
                    "form_data": form.cleaned_data,
                    "cart_items": cart_items,
                    "net_total": net,
                    "gst_amount": gst,
                    "grand_total": grand,
                    "discount": Decimal("0"),
                    "coupon_message": ""
                })

            return render(request, "checkoutview.html", {"form": form})

        # ================= COUPON STEP =================
        elif step == "coupon":
            coupon_code = request.POST.get("coupon_code", "").strip()

            discount = Decimal("0")
            message = "Invalid Coupon"
            applied = False

            today = timezone.now().date()

            # one-time use check
            already_used = Placedorderxx.objects.filter(
                user=user,
                coupon_code=coupon_code,
                coupon_discount__gt=0
            ).exists()

            if already_used:
                net, gst, grand = calculate_totals(cart_items)

                return render(request, "checkout_confirm.html", {
                    "form_data": request.session.get("checkout_data"),
                    "cart_items": cart_items,
                    "net_total": net,
                    "gst_amount": gst,
                    "grand_total": grand,
                    "discount": Decimal("0"),
                    "coupon_message": "This coupon can be used only once",
                    "applied_coupon": ""
                })

            # check coupon
            for item in cart_items:
                product = item.product

                if product.coupon_code == coupon_code and product.coupon_active:

                    # ================= EXPIRED CHECK =================
                    if product.coupon_expiry and product.coupon_expiry < today:
                        message = "❌ This coupon has expired"
                        applied = False
                        break

                    # ================= VALID COUPON =================
                    if product.coupon_discount > 0:
                        discount = Decimal(str(product.coupon_discount))
                        message = f"Coupon Applied: -₹{discount}"
                        applied = True
                        break

            request.session["applied_coupon"] = coupon_code if applied else ""
            request.session["applied_discount"] = str(discount if applied else 0)

            net, gst, grand = calculate_totals(cart_items, discount if applied else 0)

            return render(request, "checkout_confirm.html", {
                "form_data": request.session.get("checkout_data"),
                "cart_items": cart_items,
                "net_total": net,
                "gst_amount": gst,
                "grand_total": grand,
                "discount": discount if applied else Decimal("0"),
                "coupon_message": message,
                "applied_coupon": coupon_code if applied else ""
            })

        # ================= STEP 2 =================
        elif step == "2":
            checkout_data = request.session.get("checkout_data")
            if not checkout_data:
                return redirect("checkouts")

            discount = Decimal(request.session.get("applied_discount", "0"))
            coupon_code = request.session.get("applied_coupon", "")

            save_coupon = coupon_code if discount > 0 else ""
            save_discount = discount if discount > 0 else Decimal("0")

            try:
                with transaction.atomic():

                    net, gst, grand = calculate_totals(cart_items, save_discount)

                    for item in cart_items:
                        product = item.product

                        if item.product_qty > product.quantity:
                            return render(request, "checkout_confirm.html", {
                                "error": f"Not enough stock for {product.name}",
                                "form_data": checkout_data,
                                "cart_items": cart_items
                            })

                        # final expiry safety check
                        today = timezone.now().date()
                        if product.coupon_expiry and product.coupon_expiry < today:
                            save_coupon = ""
                            save_discount = Decimal("0")

                        Placedorderxx.objects.create(
                            user=user,
                            product=product,
                            product_name=product.name,
                            product_image=product.product_image,
                            product_price=product.selling_price,
                            selling_price=product.original_price,
                            vendor=product.vendor,
                            quantity=item.product_qty,

                            name=checkout_data.get("full_name"),
                            address=checkout_data.get("address_line1"),
                            city=checkout_data.get("city"),
                            state=checkout_data.get("state"),
                            phone=checkout_data.get("phone"),
                            postal_code=checkout_data.get("postal_code"),

                            coupon_code=save_coupon,
                            coupon_discount=save_discount,

                            total_amount=grand
                        )

                        product.quantity -= item.product_qty
                        product.save()

                    cart_items.delete()

                    request.session.pop("checkout_data", None)
                    request.session.pop("applied_coupon", None)
                    request.session.pop("applied_discount", None)

                    return redirect("home")

            except Exception as e:
                return render(request, "checkout_confirm.html", {
                    "error": str(e),
                    "cart_items": cart_items,
                    "form_data": checkout_data
                })

    return render(request, "checkoutview.html", {
        "form": CheckoutForm()
    })




def orderstatus(request):

    if request.user.is_authenticated:
        user = request.user

        orders = Placedorderxx.objects.filter(
            user=user
        ).order_by("-created_at")  # latest first
    else:
        orders = Placedorderxx.objects.none()

    return render(
        request,
        "orderstatus.html",
        {"orders": orders}
    )




from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta

def order_detail(request, pk):
    order = get_object_or_404(Placedorderxx, id=pk, user=request.user)

    # Convert UTC → Local Time
    order.created_at = timezone.localtime(order.created_at)

    # ✅ Return logic
    can_return = False
    if order.status == "Completed" and order.delivered_at:
        delivered_local = timezone.localtime(order.delivered_at)

        if timezone.now() <= delivered_local + timedelta(days=7):
            can_return = True

    return render(request, "order_detail.html", {
        "order": order,
        "can_return": can_return
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import OrderPlacededx  # Adjust model name if needed

def orderdetail(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    order = get_object_or_404(OrderPlacededx, pk=pk, user=request.user)

    if order.status == 'Pending':
        messages.warning(request, "Invoice cannot be downloaded until the order is complete.")

    return render(request, 'orderdetail.html', {'order': order})



def logout_paged(request):
  if request.user.is_authenticated:
    logout(request)
    messages.success(request,"Logged out Successfully")
  return redirect("/home")

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect('home') 



def collections(request):
  catagory=Catagory.objects.filter(status=0)
  return render(request,"collections.html",{"catagory":catagory})

def collectionsview(request,name):
  if(Catagory.objects.filter(name=name,status=0)):
      products=Product.objects.filter(category__name=name)
      return render(request,"products/index.html",{"products":products,"category_name":name})
  else:
    messages.warning(request,"No Such Catagory Found")
    return redirect('collections')







def product_details(request, cname, pname):

    # Check category
    category = Catagory.objects.filter(
        name=cname,
        status=0
    ).first()

    if not category:
        messages.error(request, "No Such Category Found")
        return redirect('collections')

    # Find product inside the selected category
    products = Product.objects.filter(
        category=category,
        name=pname,
        status=0
    ).first()

    if not products:
        messages.error(request, "No Such Product Found")
        return redirect('collections')

    # Get reviews for the exact product
    reviews = Review.objects.filter(
        product=products
    ).order_by('-created_at')

    return render(
        request,
        "products/productdetails.html",
        {
            "products": products,
            "reviews": reviews
        }
    )



# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Review, Placedorderxx

def add_review(request, order_id):
    order = get_object_or_404(Placedorderxx, id=order_id, user=request.user)

    # ✅ Only allow if completed
    if order.status != 'completed':
        messages.error(request, "You can review only after order is completed")
        return redirect('orderdetail', pk=order_id)

    # ✅ Prevent duplicate review
    if Review.objects.filter(order=order).exists():
        messages.error(request, "You already reviewed this product")
        return redirect('orderdetail', pk=order_id)

    # ✅ IMPORTANT FIX
    if not order.product:
        messages.error(request, "Product not available for this order")
        return redirect('orderdetail', pk=order_id)

    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        Review.objects.create(
            user=request.user,
            product=order.product,   # ✅ FIXED HERE
            order=order,
            rating=rating,
            comment=comment,
            image=image,
            video=video
        )

        messages.success(request, "Review submitted successfully")
        return redirect('orderdetail', pk=order_id)
    


from decimal import Decimal

from django.template.loader import get_template
from django.http import HttpResponse

from xhtml2pdf import pisa

from .models import Placedorderxx


def invoice(request, order_id):

    # ---------------------------------------------------------
    # GET ORDER
    # ---------------------------------------------------------

    try:
        order = (
            Placedorderxx.objects
            .select_related("user", "product")
            .get(id=order_id)
        )

    except Placedorderxx.DoesNotExist:
        return HttpResponse(
            "Order not found.",
            status=404
        )

    # ---------------------------------------------------------
    # PRICE CALCULATION
    # ---------------------------------------------------------

    if order.selling_price is not None:
        unit_price = Decimal(str(order.selling_price))

    elif order.product_price is not None:
        unit_price = Decimal(str(order.product_price))

    else:
        unit_price = Decimal("0.00")

    quantity = order.quantity or 1

    subtotal = unit_price * quantity

    discount = Decimal(
        str(order.coupon_discount or 0)
    )

    # Never allow negative discount
    if discount < 0:
        discount = Decimal("0.00")

    # Use stored order total because it represents
    # the final amount saved when the order was created.
    invoice_total = Decimal(
        str(order.total_amount or 0)
    )

    # ---------------------------------------------------------
    # CONTEXT
    # ---------------------------------------------------------

    context = {

        "order": order,

        "unit_price": unit_price,

        "quantity": quantity,

        "subtotal": subtotal,

        "discount": discount,

        "invoice_total": invoice_total,

    }

    # ---------------------------------------------------------
    # LOAD TEMPLATE
    # ---------------------------------------------------------

    template = get_template(
        "abcd.html"
    )

    html = template.render(
        context
    )

    # ---------------------------------------------------------
    # PDF RESPONSE
    # ---------------------------------------------------------

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="Invoice_INV-{order.id}.pdf"'
    )

    # ---------------------------------------------------------
    # GENERATE PDF
    # ---------------------------------------------------------

    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        encoding="UTF-8"
    )

    # ---------------------------------------------------------
    # ERROR
    # ---------------------------------------------------------

    if pisa_status.err:

        return HttpResponse(
            "Error generating invoice PDF.",
            status=500
        )

    return response

from django.shortcuts import render
from django.db.models import Q
from .models import Product

def productsearch(request):
    query = request.GET.get('q')
    products = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(category__name__icontains=query)
        )

    return render(request, 'productsearch.html', {
        'products': products,
        'query': query
    })






from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserForm



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import CustomerRegistration
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
def profile(request):

    profile, created = CustomerRegistration.objects.get_or_create(
        user=request.user,
        defaults={
            "email": request.user.email
        }
    )

    if request.method == "POST":

        # Update profile image anytime
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["profile_image"]

        # Update phone only once
        phone = request.POST.get("phone")

        if phone and not profile.phone_updated:

            profile.phone = phone
            profile.phone_updated = True

            messages.success(
                request,
                "Profile updated successfully."
            )

        else:
            messages.info(
                request,
                "No changes made."
            )

        profile.save()

        return redirect("profile")


    return render(request, "profile.html", {
        "profile": profile
    })



# views.py
import random
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import DatabaseError
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

from .forms import ForgotPasswordForm, OTPVerifyForm
from .models import PasswordResetOTPds


# ----------------------------- FORGOT PASSWORD -----------------------------

def forgotpassword(request):
    try:
        if request.method == 'POST':
            form = ForgotPasswordForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']

                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    messages.error(request, "Email not registered.")
                    return redirect('forgotpassword')

                otp = str(random.randint(100000, 999999))

                # Delete previous OTP
                PasswordResetOTPds.objects.filter(user=user).delete()

                otp_instance = PasswordResetOTPds.objects.create(user=user, otp=otp)

                # Email sending with error protection
                try:
                    send_mail(
                        subject='Your OTP for Password Reset',
                        message=f'Your OTP is: {otp}',
                        from_email='your@example.com',
                        recipient_list=[email],
                    )
                except Exception:
                    return render(request, "404.html", status=404)

                request.session['reset_user_id'] = user.id
                request.session['otp_token'] = str(otp_instance.otp_token)

                return redirect('verify_otp')
        else:
            form = ForgotPasswordForm()

        return render(request, 'forgotpassword.html', {'form': form})

    except Exception:
        return render(request, "404.html", status=404)








# ----------------------------- VERIFY OTP -----------------------------

def verify_otp(request):
    try:
        user_id = request.session.get('reset_user_id')
        token = request.session.get('otp_token')

        # 🔒 Session missing → force restart
        if not user_id or not token:
            messages.error(request, "Session expired. Please request a new OTP.")
            return redirect('forgotpassword')

        user = get_object_or_404(User, id=user_id)
        otp_instance = get_object_or_404(
            PasswordResetOTPds,
            user=user,
            otp_token=token
        )

        # 🔐 BLOCK PAGE REFRESH (GET after first load)
        if request.method == 'GET':
            if request.session.get('otp_page_loaded'):
                # Clear session & force new OTP
                request.session.flush()
                messages.error(
                    request,
                    "OTP page refreshed. Please request a new OTP."
                )
                return redirect('forgotpassword')

            # First valid load
            request.session['otp_page_loaded'] = True

        # 🔑 FORM SUBMISSION
        if request.method == 'POST':
            form = OTPVerifyForm(request.POST)

            if form.is_valid():
                input_otp = form.cleaned_data['otp']

                # ⏱ Expiry check
                if otp_instance.is_expired():
                    request.session.flush()
                    messages.error(request, "OTP expired. Please request a new one.")
                    return redirect('forgotpassword')

                # ✅ OTP match
                if otp_instance.otp == input_otp:
                    otp_instance.is_verified = True
                    otp_instance.save()

                    # Allow reset password page
                    request.session['otp_verified'] = True
                    messages.success(request, "OTP verified successfully.")
                    return redirect('reset_password')

                else:
                    messages.error(request, "Invalid OTP.")

            else:
                messages.error(request, "Invalid OTP input.")

        else:
            form = OTPVerifyForm()

        # ⏳ Timer (always fresh on first load)
        expires_in = (
            otp_instance.created_at + timezone.timedelta(minutes=5)
        ) - timezone.now()
        seconds_left = max(0, int(expires_in.total_seconds()))

        return render(request, 'verify_otp.html', {
            'form': form,
            'seconds_left': seconds_left
        })

    except Exception:
        return render(request, "404.html", status=404)

# ----------------------------- RESEND OTP -----------------------------

def resend_otp(request):
    try:
        user_id = request.session.get('reset_user_id')

        if not user_id:
            messages.error(request, "Session expired.")
            return redirect('forgotpassword')

        user = get_object_or_404(User, id=user_id)

        otp = str(random.randint(100000, 999999))

        PasswordResetOTPds.objects.filter(user=user).delete()
        otp_instance = PasswordResetOTPds.objects.create(user=user, otp=otp)

        try:
            send_mail(
                subject='Your OTP for Password Reset (Resent)',
                message=f'Your new OTP is: {otp}',
                from_email='your@example.com',
                recipient_list=[user.email],
            )
        except Exception:
            return render(request, "404.html", status=404)

        request.session['otp_token'] = str(otp_instance.otp_token)

        messages.success(request, "OTP resent successfully.")
        return redirect('verify_otp')

    except Exception:
        return render(request, "404.html", status=404)


# ----------------------------- RESET PASSWORD -----------------------------

def reset_password(request):
    try:
        user_id = request.session.get('reset_user_id')
        token = request.session.get('otp_token')

        if not user_id or not token:
            messages.error(request, "Session expired.")
            return redirect('forgot_password')

        user = get_object_or_404(User, id=user_id)
        otp_instance = get_object_or_404(PasswordResetOTPds, user=user, otp_token=token)

        if not otp_instance.is_verified:
            messages.error(request, "OTP not verified.")
            return redirect('verify_otp')

        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()

                PasswordResetOTPds.objects.filter(user=user).delete()
                request.session.pop('reset_user_id', None)
                request.session.pop('otp_token', None)

                return render(request, 'password_reset_success.html')

        else:
            form = SetPasswordForm(user)

        return render(request, 'reset_password.html', {'form': form})

    except Exception:
        return render(request, "404.html", status=404)
















































































































from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User




from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from .models import SellerProfile


# ============================================================
# ADMIN CHECK
# ============================================================

def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.is_staff
    )


# ============================================================
# ADMIN UNLOCK SELLER
# ============================================================

@login_required
def admin_unlock_seller(request):

    if request.method == "POST":

        seller_input = request.POST.get("seller_input", "").strip()

        # ----------------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------------
        if not seller_input:
            messages.error(
                request,
                "Please enter Seller ID, username, or email."
            )
            return redirect("admin_unlock_seller")

        seller = None

        # ====================================================
        # 1. NUMERIC SELLER ID
        # ====================================================

        if seller_input.isdigit():

            try:
                seller = SellerProfile.objects.select_related(
                    "user"
                ).get(id=int(seller_input))

            except SellerProfile.DoesNotExist:
                messages.error(
                    request,
                    f"Seller ID '{seller_input}' was not found."
                )
                return redirect("admin_unlock_seller")

        # ====================================================
        # 2. USERNAME OR EMAIL
        # ====================================================

        else:

            user = None

            # ------------------------------------------------
            # Try username first
            # ------------------------------------------------

            try:
                user = User.objects.get(
                    username__iexact=seller_input
                )

            except User.DoesNotExist:

                # --------------------------------------------
                # Try email
                # --------------------------------------------

                try:
                    user = User.objects.get(
                        email__iexact=seller_input
                    )

                except User.DoesNotExist:
                    messages.error(
                        request,
                        f"No seller account was found for '{seller_input}'."
                    )
                    return redirect("admin_unlock_seller")

                except User.MultipleObjectsReturned:
                    messages.error(
                        request,
                        "Multiple accounts use this email address. "
                        "Please use the Seller ID or username."
                    )
                    return redirect("admin_unlock_seller")

            # ------------------------------------------------
            # Find SellerProfile
            # ------------------------------------------------

            try:
                seller = SellerProfile.objects.select_related(
                    "user"
                ).get(user=user)

            except SellerProfile.DoesNotExist:
                messages.error(
                    request,
                    f"User '{seller_input}' does not have a seller profile."
                )
                return redirect("admin_unlock_seller")

            except SellerProfile.MultipleObjectsReturned:
                messages.error(
                    request,
                    "Multiple seller profiles are associated with this user. "
                    "Please use the Seller ID."
                )
                return redirect("admin_unlock_seller")

        # ====================================================
        # SAFETY CHECK
        # ====================================================

        if seller is None:
            messages.error(
                request,
                "Seller account could not be identified."
            )
            return redirect("admin_unlock_seller")

        # ====================================================
        # GET SELLER USERNAME SAFELY
        # ====================================================

        seller_username = seller.user.username

        # ====================================================
        # CHECK CURRENT LOCK STATUS
        # ====================================================

        if seller.is_locked:

            # ------------------------------------------------
            # Account is locked → unlock it
            # ------------------------------------------------

            seller.is_locked = False
            seller.failed_login_attempts = 0
            seller.failed_unlock_attempts = 0

            seller.save(
                update_fields=[
                    "is_locked",
                    "failed_login_attempts",
                    "failed_unlock_attempts",
                ]
            )

            messages.success(
                request,
                f"Seller account '{seller_username}' "
                f"has been successfully unlocked."
            )

        else:

            # ------------------------------------------------
            # Account is already unlocked
            # ------------------------------------------------

            messages.warning(
                request,
                f"Seller account '{seller_username}' "
                f"is already unlocked."
            )

        return redirect("admin_unlock_seller")

    # ========================================================
    # GET REQUEST
    # ========================================================

    return render(
        request,
        "admin/admin_unlock_seller.html"
    )


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.utils.timezone import now
from datetime import timedelta

from .models import (
     Product,
     Catagory,
     Tickets,
     SellerProfile,
     Placedorderxx,
     SiteVisit,
     CustomerLoginLogout,
     AdminProfilez
)


def admin_saller_tickat_dashboard(request):
    tickets = Tickets.objects.all().order_by('-created_at')
    return render(request, 'admin/admin_saller_tickat_dashboard.html', {'tickets': tickets})


# ---------- Admin Update Ticket ----------

def admin_update_ticket(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)
    if request.method == 'POST':
        ticket.status = request.POST['status']
        ticket.admin_description = request.POST['admin_description']
        ticket.save()
        messages.success(request, "Ticket updated successfully!")
        return redirect('admin_saller_tickat_dashboard')
    return render(request, 'admin/admin_update_ticket.html', {'ticket': ticket})





import uuid
from django.utils import timezone

def save(self, *args, **kwargs):
    if not self.ticket_number:
        self.ticket_number = "TKT-" + uuid.uuid4().hex[:8].upper()

    # Auto resolved_at timestamp
    if self.status == "RESOLVED" and not self.resolved_at:
        self.resolved_at = timezone.now()

    super().save(*args, **kwargs)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Tickets, TicketReply


@login_required
def admin_seller_tickets_details(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)

    if request.method == "POST":

        ticket.status = request.POST.get("status")
        ticket.priority = request.POST.get("priority")

        assigned_id = request.POST.get("assigned_to")
        if assigned_id:
            try:
                ticket.assigned_to = User.objects.get(id=assigned_id)
            except User.DoesNotExist:
                ticket.assigned_to = None
        else:
            ticket.assigned_to = None

        ticket.admin_description = request.POST.get("admin_description")

        # ✅ CORRECT RESOLVED LOGIC
        if ticket.status == "RESOLVED":
            if ticket.resolved_at is None:
                ticket.resolved_at = timezone.now()
        else:
            ticket.resolved_at = None

        ticket.save()

        # Reply
        admin_msg = request.POST.get("admin_message")
        if admin_msg:
            TicketReply.objects.create(
                ticket=ticket,
                user=request.user,
                message=admin_msg
            )

        messages.success(request, "Ticket updated successfully!")

        # ✅ VERY IMPORTANT
        return redirect("admin_seller_tickets_details", ticket_id=ticket.id)

    replies = ticket.replies.all().order_by("created_at")
    admins = User.objects.filter(is_staff=True)

    return render(request, "admin/admin_seller_tickets_details.html", {
        "ticket": ticket,
        "replies": replies,
        "admins": admins
    })


from django.shortcuts import render
from .models import Product


def low_stock_products(request):
    products = Product.objects.filter(quantity__lt=5)
    return render(request, 'admin/low_stock.html', {'products': products})


def admin_order_notifications(request):
    orders = Placedorderxx.objects.all()
    return render(request, 'admin/admin_orders.html', {'orders': orders})









import secrets
import string
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .models import AdminProfilez


LOGIN_TEMPLATE = "admin/admin_login.html"
OTP_LENGTH = 7
OTP_TTL = timedelta(minutes=2)
OTP_RESEND_COOLDOWN_SECONDS = 30
MAX_OTP_RESENDS = 3
MAX_OTP_ATTEMPTS = 3
LOCK_STEPS = {
    1: timedelta(minutes=2),
    2: timedelta(minutes=5),
    3: timedelta(hours=24),
}
FINAL_LOCK = timedelta(hours=24)


def get_client_ip(request):
    # REMOTE_ADDR is correct unless your deployment has a trusted proxy.
    # Never blindly trust X-Forwarded-For from arbitrary clients.
    return request.META.get("REMOTE_ADDR", "")


def clear_login_challenge(request):
    for key in (
        "admin_otp_profile_id",
        "admin_otp_challenge_id",
        "admin_otp_username",
        "admin_otp_started_at",
        "admin_otp_expires_at",
        "admin_otp_resends",
    ):
        request.session.pop(key, None)


def send_security_email(profile, subject, body):
    if not profile.admin_email or not profile.email_verified:
        return False
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.admin_email],
            fail_silently=False,
        )
        return True
    except Exception:
        # Configure server-side logging in production; don't expose mail errors.
        return False


def lock_admin(profile, duration, reason):
    profile.locked_until = timezone.now() + duration
    profile.clear_otp()
    profile.save()
    send_security_email(
        profile,
        "ShopKart Admin Security Alert",
        (
            f"Hello {profile.user.username},\n\n"
            "Your ShopKart admin login has been temporarily locked.\n"
            f"Reason: {reason}\n"
            f"Unlock time: {timezone.localtime(profile.locked_until):%Y-%m-%d %H:%M:%S %Z}\n\n"
            "If this was not you, contact your website administrator."
        ),
    )


def lock_seconds(profile):
    if not profile or not profile.locked_until:
        return 0
    return max(0, int((profile.locked_until - timezone.now()).total_seconds()))


def issue_admin_otp(request, profile, force=False):
    if not profile.admin_email or not profile.email_verified:
        return False, "Your admin email is not verified. Contact the website administrator."

    now = timezone.now()
    if not force and profile.otp_hash and profile.otp_expires_at and now < profile.otp_expires_at:
        return True, ""

    alphabet = string.ascii_uppercase + string.digits
    code = "".join(secrets.choice(alphabet) for _ in range(OTP_LENGTH))
    challenge_id = uuid.uuid4().hex

    profile.otp_hash = make_password(code)
    profile.otp_expires_at = now + OTP_TTL
    profile.otp_sent_at = now
    profile.otp_challenge_id = challenge_id
    # Do not reset the OTP failure counter on resend; otherwise resends could
    # be used to bypass the three-attempt verification limit.
    profile.save()

    sent = send_security_email(
        profile,
        "Your ShopKart Admin Login OTP",
        (
            f"Your ShopKart admin login code is: {code}\n\n"
            "This code expires in 2 minutes. A newly requested code invalidates "
            "the previous code. Do not share this code with anyone."
        ),
    )
    if not sent:
        profile.clear_otp()
        profile.save()
        return False, "The OTP email could not be sent. Try again later or contact the administrator."

    request.session["admin_otp_profile_id"] = profile.pk
    request.session["admin_otp_challenge_id"] = challenge_id
    request.session["admin_otp_username"] = profile.user.username
    request.session["admin_otp_started_at"] = now.timestamp()
    request.session["admin_otp_expires_at"] = (now + OTP_TTL).timestamp()
    request.session.setdefault("admin_otp_resends", 0)
    request.session.modified = True
    return True, ""


def login_context(request, show_otp=False, profile=None):
    context = {
        "show_otp": show_otp,
        "lock_seconds": lock_seconds(profile),
        "otp_expires_at": request.session.get("admin_otp_expires_at", 0),
        "otp_resends_left": max(0, MAX_OTP_RESENDS - int(request.session.get("admin_otp_resends", 0))),
        "otp_resend_cooldown": OTP_RESEND_COOLDOWN_SECONDS,
    }
    return context


@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def admin_login(request):
    if request.user.is_authenticated:
        if AdminProfilez.objects.filter(user=request.user).exists():
            return redirect("admin_dashboard")

    show_otp = bool(request.session.get("admin_otp_profile_id"))

    if request.method == "POST":
        action = request.POST.get("action", "password")

        # Optional same-page status check: lets a user see a database-backed
        # lockout timer after entering their username in another browser/device.
        if action == "check_lock":
            username = request.POST.get("username", "").strip()
            profile = AdminProfilez.objects.filter(
                user__username__iexact=username
            ).select_related("user").first()
            seconds = lock_seconds(profile)
            return JsonResponse({
                "locked": seconds > 0,
                "seconds": seconds,
                "message": (
                    f"Account locked. Try again in {max(1, (seconds + 59) // 60)} minute(s)."
                    if seconds > 0 else ""
                ),
            })

        if action == "resend_otp":
            profile_id = request.session.get("admin_otp_profile_id")
            challenge_id = request.session.get("admin_otp_challenge_id")
            profile = AdminProfilez.objects.filter(pk=profile_id).select_related("user").first()
            if not profile or not challenge_id or profile.otp_challenge_id != challenge_id:
                clear_login_challenge(request)
                messages.error(request, "Your OTP session expired. Enter your username and password again.")
                return redirect("admin_login")
            if profile.is_locked():
                clear_login_challenge(request)
                messages.error(request, f"Admin account locked. Try again in about {max(1, (lock_seconds(profile)+59)//60)} minute(s).")
                return redirect("admin_login")

            resends = int(request.session.get("admin_otp_resends", 0))
            if resends >= MAX_OTP_RESENDS:
                messages.error(request, "You have used all 3 OTP resend attempts. Start again after signing in with your password.")
                return render(request, LOGIN_TEMPLATE, login_context(request, True, profile))

            if profile.otp_sent_at and timezone.now() - profile.otp_sent_at < timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS):
                wait = OTP_RESEND_COOLDOWN_SECONDS - int((timezone.now() - profile.otp_sent_at).total_seconds())
                messages.error(request, f"Please wait {max(1, wait)} seconds before requesting another OTP.")
                return render(request, LOGIN_TEMPLATE, login_context(request, True, profile))

            # Count each resend, and invalidate the old OTP by issuing a new challenge.
            request.session["admin_otp_resends"] = resends + 1
            ok, error = issue_admin_otp(request, profile, force=True)
            if not ok:
                messages.error(request, error)
                clear_login_challenge(request)
                return redirect("admin_login")
            messages.success(request, f"A new OTP was sent. It expires in 2 minutes. Resends remaining: {MAX_OTP_RESENDS - resends - 1}.")
            return render(request, LOGIN_TEMPLATE, login_context(request, True, profile))

        if action == "verify_otp":
            profile_id = request.session.get("admin_otp_profile_id")
            challenge_id = request.session.get("admin_otp_challenge_id")
            profile = AdminProfilez.objects.filter(pk=profile_id).select_related("user").first()

            if not profile or not challenge_id:
                clear_login_challenge(request)
                messages.error(request, "Your login session expired. Enter your credentials again.")
                return redirect("admin_login")

            if profile.is_locked():
                seconds = lock_seconds(profile)
                clear_login_challenge(request)
                messages.error(request, f"Admin account locked. Try again in about {max(1, (seconds + 59)//60)} minute(s).")
                return redirect("admin_login")

            if profile.otp_challenge_id != challenge_id or not profile.otp_hash:
                clear_login_challenge(request)
                messages.error(request, "This OTP is no longer valid. Log in again.")
                return redirect("admin_login")

            submitted_code = "".join(request.POST.get(f"otp_{i}", "") for i in range(1, OTP_LENGTH + 1)).strip().upper()
            # Also accept a single hidden field if browser form submission is customized.
            if not submitted_code:
                submitted_code = request.POST.get("otp", "").strip().upper()

            valid_code = (
                profile.otp_expires_at is not None
                and timezone.now() < profile.otp_expires_at
                and len(submitted_code) == OTP_LENGTH
                and all(ch in string.ascii_uppercase + string.digits for ch in submitted_code)
                and check_password(submitted_code, profile.otp_hash)
            )

            if not valid_code:
                profile.otp_attempts += 1
                if profile.otp_attempts >= MAX_OTP_ATTEMPTS:
                    lock_admin(profile, FINAL_LOCK, "Three failed OTP submissions")
                    clear_login_challenge(request)
                    messages.error(request, "Three OTP attempts failed. Your admin account is locked for 24 hours.")
                    return redirect("admin_login")

                expired = profile.otp_expires_at is None or timezone.now() >= profile.otp_expires_at
                if expired:
                    profile.clear_otp()
                    profile.save()
                    clear_login_challenge(request)
                    messages.error(request, "OTP expired. Enter your username and password to request a new code.")
                    return redirect("admin_login")

                profile.save()
                messages.error(request, f"Incorrect OTP. {MAX_OTP_ATTEMPTS - profile.otp_attempts} attempt(s) remaining.")
                return render(request, LOGIN_TEMPLATE, login_context(request, True, profile))

            user = profile.user
            if not user.is_active:
                clear_login_challenge(request)
                messages.error(request, "This admin account is inactive.")
                return redirect("admin_login")

            profile.failed_password_attempts = 0
            profile.otp_attempts = 0
            profile.last_login_ip = get_client_ip(request)
            profile.last_login_at = timezone.now()
            profile.clear_otp()
            profile.save()
            clear_login_challenge(request)
            request.session.flush()
            login(request, user)
            request.session.cycle_key()
            request.session.set_expiry(8 * 60 * 60)
            return redirect("admin_dashboard")

        # STEP 1: username + password
        clear_login_challenge(request)
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            messages.error(request, "Enter both username and password.")
            return render(request, LOGIN_TEMPLATE, {"show_otp": False})

        profile = AdminProfilez.objects.filter(
            user__username__iexact=username
        ).select_related("user").first()

        if profile and profile.is_locked():
            seconds = lock_seconds(profile)
            messages.error(request, f"Admin account locked. Try again in about {max(1, (seconds+59)//60)} minute(s).")
            return render(request, LOGIN_TEMPLATE, login_context(request, False, profile))

        user = authenticate(request, username=username, password=password)
        if not user or not user.is_active or not profile or profile.user_id != user.pk:
            if profile:
                profile.failed_password_attempts += 1
                attempts = profile.failed_password_attempts
                duration = LOCK_STEPS.get(attempts, FINAL_LOCK)
                if attempts >= 3:
                    lock_admin(profile, FINAL_LOCK, f"{attempts} failed password attempts")
                    messages.error(request, "Three failed password attempts. Your admin account is locked for 24 hours.")
                else:
                    profile.locked_until = timezone.now() + duration
                    profile.save()
                    mins = int(duration.total_seconds() // 60)
                    messages.error(request, f"Invalid username or password. Account locked for {mins} minute(s).")
                return render(request, LOGIN_TEMPLATE, login_context(request, False, profile))
            messages.error(request, "Invalid username or password.")
            return render(request, LOGIN_TEMPLATE, {"show_otp": False})

        if not profile.email_verified or not profile.admin_email:
            messages.error(request, "Your admin email is not verified. Contact the website administrator.")
            return render(request, LOGIN_TEMPLATE, {"show_otp": False})

        # A correct password does not bypass an existing active lock; that was checked above.
        profile.failed_password_attempts = 0
        profile.otp_attempts = 0
        profile.save()
        request.session["admin_otp_resends"] = 0
        ok, error = issue_admin_otp(request, profile, force=True)
        if not ok:
            clear_login_challenge(request)
            messages.error(request, error)
            return render(request, LOGIN_TEMPLATE, {"show_otp": False})

        messages.success(request, f"OTP sent to your verified admin email ending in {profile.admin_email[-10:]}. It expires in 2 minutes.")
        return render(request, LOGIN_TEMPLATE, login_context(request, True, profile))

    profile = None
    if request.session.get("admin_otp_profile_id"):
        profile = AdminProfilez.objects.filter(pk=request.session.get("admin_otp_profile_id")).first()
    return render(request, LOGIN_TEMPLATE, login_context(request, show_otp, profile))


def admin_logout(request):
    logout(request)
    request.session.flush()
    messages.success(request, "Admin logged out successfully.")
    return redirect("admin_login")

























import hashlib
import secrets

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .models import AdminProfilez


User = get_user_model()

RESET_TIMEOUT_SECONDS = 600  # 10 minutes


def _token_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _clear_password_reset(profile):
    profile.password_reset_token_hash = ""
    profile.password_reset_expires_at = None
    profile.save(update_fields=[
        "password_reset_token_hash",
        "password_reset_expires_at",
        "updated_at",
    ])


RESET_TIMEOUT_SECONDS = 10 * 60
RESET_REQUEST_LIMIT = 3
RESET_WINDOW_SECONDS = 24 * 60 * 60
RESET_LOCK_SECONDS = 24 * 60 * 60


@require_http_methods(["GET", "POST"])
def admin_forgot_password(request):
    context = {
        "reset_limit": RESET_REQUEST_LIMIT,
    }

    generic_message = (
        "If the account is eligible, password-reset instructions "
        "will be sent to its verified email."
    )

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()

        if not identifier:
            context["error"] = (
                "Enter your admin username or email."
            )
            return render(
                request, "admin/forgot_password.html", context
            )

        # Find only an account associated with an admin profile.
        profile = (
            AdminProfilez.objects
            .select_related("user")
            .filter(
                Q(user__username__iexact=identifier)
                | Q(admin_email__iexact=identifier)
            )
            .order_by("pk")
            .first()
        )

        # Avoid revealing whether an admin account exists.
        if not profile:
            context["success"] = generic_message
            return render(
                request, "admin/forgot_password.html", context
            )

        now = timezone.now()

        # Check the separate password-reset lock.
        if (
            profile.password_reset_locked_until
            and profile.password_reset_locked_until > now
        ):
            remaining = max(
                0,
                int(
                    (
                        profile.password_reset_locked_until - now
                    ).total_seconds()
                ),
            )

            context.update({
                "locked": True,
                "remaining_seconds": remaining,
                "error": (
                    "Password recovery is temporarily locked "
                    "after reaching the request limit."
                ),
                "requests_used": RESET_REQUEST_LIMIT,
                "requests_remaining": 0,
            })

            return render(
                request, "admin/forgot_password.html", context
            )

        # Start a fresh counting window if the previous one expired.
        window_start = profile.password_reset_window_start

        if (
            window_start is None
            or (now - window_start).total_seconds()
            >= RESET_WINDOW_SECONDS
        ):
            profile.password_reset_window_start = now
            profile.password_reset_requests = 0
            profile.password_reset_locked_until = None

        # Clear an expired lock.
        if (
            profile.password_reset_locked_until
            and profile.password_reset_locked_until <= now
        ):
            profile.password_reset_locked_until = None

        # Check any other existing admin lock separately.
        if profile.is_locked():
            remaining = max(
                0,
                int(
                    (
                        profile.locked_until - now
                    ).total_seconds()
                ),
            )

            context.update({
                "locked": True,
                "remaining_seconds": remaining,
                "error": "This admin account is temporarily locked.",
            })

            return render(
                request, "admin/forgot_password.html", context
            )

        # Only send password-reset links to verified admin emails.
        if not profile.email_verified or not profile.admin_email:
            context["success"] = generic_message
            return render(
                request, "admin/forgot_password.html", context
            )

        # Atomically reserve one of the three allowed requests.
        # The row lock prevents simultaneous requests from bypassing
        # the counter on databases that support SELECT FOR UPDATE.
        with transaction.atomic():
            locked_profile = (
                AdminProfilez.objects
                .select_for_update()
                .get(pk=profile.pk)
            )

            now = timezone.now()
            window_start = locked_profile.password_reset_window_start

            if (
                window_start is None
                or (now - window_start).total_seconds()
                >= RESET_WINDOW_SECONDS
            ):
                locked_profile.password_reset_window_start = now
                locked_profile.password_reset_requests = 0
                locked_profile.password_reset_locked_until = None

            if (
                locked_profile.password_reset_locked_until
                and locked_profile.password_reset_locked_until > now
            ):
                remaining = max(
                    0,
                    int(
                        (
                            locked_profile.password_reset_locked_until
                            - now
                        ).total_seconds()
                    ),
                )
                context.update({
                    "locked": True,
                    "remaining_seconds": remaining,
                    "error": (
                        "Password recovery is temporarily locked."
                    ),
                    "requests_used": RESET_REQUEST_LIMIT,
                    "requests_remaining": 0,
                })
                return render(
                    request, "admin/forgot_password.html", context
                )

            # Count this request, including a failed email delivery,
            # so repeated delivery attempts cannot bypass the limit.
            locked_profile.password_reset_requests += 1
            used = locked_profile.password_reset_requests

            # The third request is allowed, but starts a 24-hour lock.
            if used >= RESET_REQUEST_LIMIT:
                locked_profile.password_reset_locked_until = (
                    now + timedelta(seconds=RESET_LOCK_SECONDS)
                )

            locked_profile.save(update_fields=[
                "password_reset_requests",
                "password_reset_window_start",
                "password_reset_locked_until",
            ])

        # Generate a strong, single-use reset token.
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(
            seconds=RESET_TIMEOUT_SECONDS
        )

        profile.password_reset_token_hash = _token_hash(token)
        profile.password_reset_expires_at = expires_at
        profile.save(update_fields=[
            "password_reset_token_hash",
            "password_reset_expires_at",
            "updated_at",
        ])

        reset_path = reverse(
            "admin_forgot_password_reset",
            kwargs={"profile_id": profile.pk},
        )
        reset_url = request.build_absolute_uri(
            f"{reset_path}?token={token}"
        )

        subject = "ShopKart Admin Password Reset"
        body = (
            f"Hello {profile.user.username},\n\n"
            "A password reset was requested for your "
            "ShopKart administrator account.\n\n"
            f"Reset your password using this link:\n{reset_url}\n\n"
            "This link expires in 10 minutes and can be used once.\n\n"
            "You can request password-reset links up to 3 times "
            "in a 24-hour period. After the third request, "
            "password recovery is locked for 24 hours.\n\n"
            "If you did not request this, ignore this email."
        )

        try:
            sent = send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [profile.admin_email],
                fail_silently=False,
            )
        except Exception:
            sent = 0

        if not sent:
            _clear_password_reset(profile)
            context["error"] = (
                "We could not send the email. Please try again later."
            )
        else:
            context["success"] = generic_message

        # Show the request allowance after processing.
        profile.refresh_from_db()

        context["requests_used"] = profile.password_reset_requests
        context["requests_remaining"] = max(
            0,
            RESET_REQUEST_LIMIT - profile.password_reset_requests,
        )

        # If this was request three, show the lock countdown.
        if (
            profile.password_reset_locked_until
            and profile.password_reset_locked_until > timezone.now()
        ):
            context.update({
                "locked": True,
                "remaining_seconds": max(
                    0,
                    int(
                        (
                            profile.password_reset_locked_until
                            - timezone.now()
                        ).total_seconds()
                    ),
                ),
            })

    return render(
        request, "admin/forgot_password.html", context
    )

@require_http_methods(["GET", "POST"])
def admin_forgot_password_reset(request, profile_id):
    profile = (
        AdminProfilez.objects
        .select_related("user")
        .filter(pk=profile_id)
        .first()
    )

    token = (
        request.POST.get("token", "")
        if request.method == "POST"
        else request.GET.get("token", "")
    )

    invalid_message = "This reset link is invalid or expired."

    if not profile:
        return render(
            request,
            "admin/reset_password.html",
            {"error": invalid_message},
        )

    if profile.is_locked():
        remaining = max(
            0,
            int(
                (profile.locked_until - timezone.now()).total_seconds()
            ),
        )
        return render(
            request,
            "admin/reset_password.html",
            {
                "error": "This admin account is temporarily locked.",
                "locked": True,
                "remaining_seconds": remaining,
            },
        )

    expiry = profile.password_reset_expires_at
    expected_hash = profile.password_reset_token_hash

    token_is_valid = (
        bool(token)
        and bool(expected_hash)
        and secrets.compare_digest(
            hashlib.sha256(token.encode("utf-8")).hexdigest(),
            expected_hash,
        )
        and expiry is not None
        and timezone.now() < expiry
        and profile.email_verified
        and bool(profile.admin_email)
    )

    if not token_is_valid:
        return render(
            request,
            "admin/reset_password.html",
            {"error": invalid_message},
        )

    if request.method == "GET":
        return render(
            request,
            "admin/reset_password.html",
            {
                "token": token,
                "expires_at": expiry,
            },
        )

    password1 = request.POST.get("password1", "")
    password2 = request.POST.get("password2", "")

    if password1 != password2:
        return render(
            request,
            "admin/reset_password.html",
            {
                "token": token,
                "expires_at": expiry,
                "error": "The passwords do not match.",
            },
        )

    try:
        validate_password(password1, user=profile.user)
    except ValidationError as exc:
        return render(
            request,
            "admin/reset_password.html",
            {
                "token": token,
                "expires_at": expiry,
                "errors": exc.messages,
            },
        )

    # Change the password.
    profile.user.set_password(password1)
    profile.user.save(update_fields=["password"])

    # Invalidate the reset token immediately after successful use.
    profile.password_reset_token_hash = ""
    profile.password_reset_expires_at = None
    profile.save(update_fields=[
        "password_reset_token_hash",
        "password_reset_expires_at",
        "updated_at",
    ])

    messages.success(
        request,
        "Your password has been changed successfully. Please log in.",
    )

    return redirect("admin_login")




























import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import (
    AdminProfilez,
    CustomerRegistration,
    SellerProfile,
    Product,
    Catagory,
    Placedorderxx,
    ReturnRequested,
    Tickets,
    Notification,
    VisitorProfile,
    VisitorSession,
    PageVisit,
    VisitorEvent,
    LoginHistory,
    SecurityAuditLog,
)

def dashboard_money(value):
    """Format numeric values for the dashboard."""
    try:
        return float(value or 0)
    except (TypeError, ValueError, Decimal):
        return 0.0


def dashboard_record(title, subtitle, details, kind, record_id=None):
    """Build a JSON-safe object for the detail modal."""
    return {
        "title": str(title or "Record"),
        "subtitle": str(subtitle or ""),
        "kind": kind,
        "record_id": record_id,
        "details": [
            {"label": str(key), "value": str(value if value not in (None, "") else "—")}
            for key, value in details.items()
        ],
        "details_json": json.dumps({
            "title": str(title or "Record"),
            "subtitle": str(subtitle or ""),
            "kind": kind,
            "details": [
                {
                    "label": str(key),
                    "value": str(value if value not in (None, "") else "—"),
                }
                for key, value in details.items()
            ],
        }),
    }


def dashboard_image(field):
    try:
        return field.url if field else ""
    except (ValueError, AttributeError):
        return ""


@login_required
def admin_dashboard(request):
    # --------------------------------------------------
    # ADMIN AUTHENTICATION
    # --------------------------------------------------
    if not AdminProfilez.objects.filter(user=request.user).exists():
        return redirect("admin_login")

    now = timezone.now()
    today = timezone.localdate()

    # --------------------------------------------------
    # BASE QUERYSETS
    # --------------------------------------------------
    customers_qs = CustomerRegistration.objects.select_related("user").order_by("-created_at")
    sellers_qs = SellerProfile.objects.select_related("user").order_by("-created_at")
    products_qs = Product.objects.select_related("category").order_by("-created_at")
    orders_qs = Placedorderxx.objects.select_related("user", "product").order_by("-created_at")
    returns_qs = ReturnRequested.objects.select_related("user", "order").order_by("-created_at")
    tickets_qs = Tickets.objects.select_related("seller", "assigned_to").order_by("-created_at")
    sessions_qs = VisitorSession.objects.select_related("visitor", "user").order_by("-last_seen")

    # --------------------------------------------------
    # DASHBOARD COUNTERS
    # --------------------------------------------------
    completed_orders = orders_qs.filter(status="completed")

    revenue = completed_orders.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    today_orders = orders_qs.filter(created_at__date=today)
    today_revenue = today_orders.filter(status="completed").aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    metrics = {
        "customers": CustomerRegistration.objects.count(),
        "sellers": SellerProfile.objects.count(),
        "approved_sellers": SellerProfile.objects.filter(status="approved").count(),
        "pending_sellers": SellerProfile.objects.filter(status="pending").count(),
        "products": Product.objects.count(),
        "visible_products": Product.objects.filter(status=True).count(),
        "orders": orders_qs.count(),
        "today_orders": today_orders.count(),
        "pending_orders": orders_qs.filter(status="pending").count(),
        "processing_orders": orders_qs.filter(status="processing").count(),
        "shipped_orders": orders_qs.filter(status="shipped").count(),
        "delivered_orders": orders_qs.filter(status="delivered").count(),
        "completed_orders": completed_orders.count(),
        "revenue": dashboard_money(revenue),
        "today_revenue": dashboard_money(today_revenue),
        "returns": returns_qs.exclude(status__in=["refunded", "rejected"]).count(),
        "open_tickets": tickets_qs.filter(
            status__in=["OPEN", "IN_PROGRESS", "WAITING"]
        ).count(),
        "active_visitors": sessions_qs.filter(
            is_active=True, last_seen__gte=now - timezone.timedelta(minutes=30)
        ).count(),
        "visitor_profiles": VisitorProfile.objects.count(),
        "page_visits": PageVisit.objects.count(),
        "security_events": SecurityAuditLog.objects.filter(
            created_at__date=today
        ).count(),
        "unread_notifications": Notification.objects.filter(
            is_read=False
        ).count(),
    }

    # --------------------------------------------------
    # PRODUCT STOCK
    # Assumes quantity <= 0 is out of stock and
    # quantity <= 10 is low stock.
    # --------------------------------------------------
    out_of_stock_qs = products_qs.filter(quantity__lte=0)
    low_stock_qs = products_qs.filter(quantity__gt=0, quantity__lte=10)

    metrics["out_of_stock"] = out_of_stock_qs.count()
    metrics["low_stock"] = low_stock_qs.count()

    # --------------------------------------------------
    # CLICKABLE TABLE DATA
    # --------------------------------------------------
    customers = []
    for obj in customers_qs[:10]:
        customers.append(dashboard_record(
            obj.user.username,
            obj.email,
            {
                "Username": obj.user.username,
                "Email": obj.email,
                "Phone": obj.phone,
                "Address": obj.address,
                "Active": "Yes" if obj.is_active else "No",
                "Registered": obj.created_at,
                "Last login": obj.last_login,
                "Last logout": obj.logout_time,
                "Profile image": dashboard_image(obj.profile_image),
            },
            "customer",
            obj.pk,
        ))

    sellers = []
    for obj in sellers_qs[:10]:
        sellers.append(dashboard_record(
            obj.company_name,
            obj.user.username,
            {
                "Username": obj.user.username,
                "Company": obj.company_name,
                "Email": obj.email or obj.user.email,
                "Mobile": obj.mobile_number,
                "Business type": obj.get_business_type_display(),
                "Status": obj.get_status_display(),
                "City": obj.city,
                "State": obj.state,
                "Country": obj.country,
                "Registered": obj.created_at,
                "GST verified": obj.gst_verified,
                "Email verified": obj.email_verified,
                "Bank verified": obj.bank_verified,
                "Profile image": dashboard_image(obj.profile_photo),
                "Rejection reason": obj.rejection_reason,
            },
            "seller",
            obj.pk,
        ))

    products = []
    for obj in products_qs[:10]:
        products.append(dashboard_record(
            obj.name,
            f"₹{obj.selling_price} · Stock {obj.quantity}",
            {
                "Product": obj.name,
                "Category": obj.category.name if obj.category_id else "—",
                "Seller": obj.vendor,
                "Size": obj.get_size_display(),
                "Quantity": obj.quantity,
                "Original price": f"₹{obj.original_price}",
                "Selling price": f"₹{obj.selling_price}",
                "Final coupon price": f"₹{obj.final_price}",
                "Coupon": obj.coupon_code,
                "Coupon discount": f"₹{obj.coupon_discount}",
                "Coupon expiry": obj.coupon_expiry,
                "Visible": obj.status,
                "Trending": obj.trending,
                "Created": obj.created_at,
                "Image": dashboard_image(obj.product_image),
            },
            "product",
            obj.pk,
        ))

    orders = []
    for obj in orders_qs[:12]:
        orders.append(dashboard_record(
            f"Order #{obj.pk}",
            obj.product_name or (obj.product.name if obj.product_id else "Product removed"),
            {
                "Order ID": obj.pk,
                "Customer": obj.user.username,
                "Customer email": obj.user.email,
                "Product": obj.product_name or (
                    obj.product.name if obj.product_id else "Deleted product"
                ),
                "Seller": obj.vendor,
                "Quantity": obj.quantity,
                "Unit selling price": obj.selling_price,
                "Total amount": f"₹{obj.total_amount}",
                "Status": obj.get_status_display(),
                "Ordered": obj.ordered_date,
                "Last updated": obj.updated_by_admin,
                "Delivery date": obj.delivered_date,
                "Recipient": obj.name,
                "Phone": obj.phone,
                "Address": obj.address,
                "City": obj.city,
                "State": obj.state,
                "Postal code": obj.postal_code,
                "Coupon": obj.coupon_code,
                "Coupon discount": obj.coupon_discount,
                "Snapshot image": dashboard_image(obj.product_image),
            },
            "order",
            obj.pk,
        ))

    returns = []
    for obj in returns_qs[:10]:
        returns.append(dashboard_record(
            f"Return #{obj.pk}",
            obj.product_name or f"Order #{obj.order_id}",
            {
                "Return ID": obj.pk,
                "Order ID": obj.order_id,
                "Customer": obj.user.username,
                "Seller": obj.vendor,
                "Product": obj.product_name,
                "Quantity": obj.quantity,
                "Status": obj.get_status_display(),
                "Reason": obj.get_reason_display(),
                "Description": obj.description,
                "Refund amount": obj.refund_amount,
                "Refund method": obj.refund_method,
                "Transaction ID": obj.transaction_id,
                "Pickup address": obj.pickup_address,
                "Pickup date": obj.pickup_date,
                "Tracking ID": obj.pickup_tracking_id,
                "Created": obj.created_at,
            },
            "return",
            obj.pk,
        ))

    tickets = []
    for obj in tickets_qs[:10]:
        tickets.append(dashboard_record(
            obj.ticket_number,
            obj.title,
            {
                "Ticket number": obj.ticket_number,
                "Seller": obj.seller.username,
                "Assigned to": obj.assigned_to.username if obj.assigned_to_id else "Unassigned",
                "Title": obj.title,
                "Description": obj.description,
                "Category": obj.get_category_display(),
                "Priority": obj.get_priority_display(),
                "Status": obj.get_status_display(),
                "Department": obj.department,
                "Due date": obj.due_date,
                "Created": obj.created_at,
                "Updated": obj.updated_at,
                "Admin response": obj.admin_description,
            },
            "ticket",
            obj.pk,
        ))

    stock_records = []
    for obj in products_qs.filter(quantity__lte=10)[:15]:
        stock_records.append(dashboard_record(
            obj.name,
            "Out of stock" if obj.quantity <= 0 else "Low stock",
            {
                "Product": obj.name,
                "Product ID": obj.pk,
                "Seller": obj.vendor,
                "Category": obj.category.name if obj.category_id else "—",
                "Remaining quantity": obj.quantity,
                "Selling price": f"₹{obj.selling_price}",
                "Stock condition": "Out of stock" if obj.quantity <= 0 else "Low stock",
                "Product image": dashboard_image(obj.product_image),
            },
            "stock",
            obj.pk,
        ))

    visitors = []
    for obj in sessions_qs[:10]:
        visitors.append(dashboard_record(
            obj.user.username if obj.user_id else str(obj.visitor.visitor_id),
            obj.current_url or obj.landing_url or "Visitor session",
            {
                "Role": obj.get_role_display(),
                "Username": obj.user.username if obj.user_id else "Guest",
                "Visitor ID": obj.visitor.visitor_id,
                "Current URL": obj.current_url,
                "Page title": obj.current_title,
                "Device": obj.device_type,
                "Browser": obj.browser,
                "Operating system": obj.operating_system,
                "Country": obj.country,
                "City": obj.city,
                "IP address": obj.ip_address,
                "Started": obj.started_at,
                "Last seen": obj.last_seen,
                "Duration seconds": obj.duration_seconds,
                "Engagement seconds": obj.engagement_seconds,
                "Active": obj.is_active,
                "Referrer": obj.referrer,
            },
            "visitor",
            obj.pk,
        ))

    # --------------------------------------------------
    # NOTIFICATIONS: BUILD FROM ACTUAL DATABASE RECORDS
    # --------------------------------------------------
    notifications = []

    def add_notification(date, title, message, category, record):
        notifications.append({
            "date": date,
            "title": title,
            "message": message,
            "category": category,
            "record": record,
        })

    for obj in orders_qs[:8]:
        record = dashboard_record(
            f"Order #{obj.pk}",
            obj.product_name or (obj.product.name if obj.product_id else "Product removed"),
            {
                "Order ID": obj.pk,
                "Customer": obj.user.username,
                "Product": obj.product_name or (
                    obj.product.name if obj.product_id else "Deleted product"
                ),
                "Quantity": obj.quantity,
                "Amount": f"₹{obj.total_amount}",
                "Status": obj.get_status_display(),
                "Order date": obj.ordered_date,
                "Address": obj.address,
            },
            "order",
            obj.pk,
        )
        add_notification(
            obj.created_at, "New order", f"Order #{obj.pk} · {obj.user.username}",
            "order", record
        )

    for obj in customers_qs[:5]:
        record = next((x for x in customers if x["record_id"] == obj.pk), None)
        if record is None:
            record = dashboard_record(
                obj.user.username, obj.email,
                {"Username": obj.user.username, "Email": obj.email, "Phone": obj.phone,
                 "Registered": obj.created_at, "Address": obj.address},
                "customer", obj.pk
            )
        add_notification(
            obj.created_at, "Customer registered", obj.user.username, "customer", record
        )

    for obj in sellers_qs[:5]:
        record = next((x for x in sellers if x["record_id"] == obj.pk), None)
        if record is None:
            record = dashboard_record(
                obj.company_name, obj.user.username,
                {"Company": obj.company_name, "Username": obj.user.username,
                 "Email": obj.email or obj.user.email, "Mobile": obj.mobile_number,
                 "Status": obj.status, "City": obj.city},
                "seller", obj.pk
            )
        add_notification(
            obj.created_at, "Seller registered", obj.company_name, "seller", record
        )

    for obj in out_of_stock_qs[:10]:
        record = next((x for x in stock_records if x["record_id"] == obj.pk), None)
        if record:
            add_notification(
                now, "Out of stock", obj.name, "stock", record
            )

    for obj in low_stock_qs[:10]:
        record = next((x for x in stock_records if x["record_id"] == obj.pk), None)
        if record:
            add_notification(
                now, "Low stock alert", f"{obj.name} · {obj.quantity} remaining",
                "stock", record
            )

    for obj in returns_qs.exclude(status__in=["refunded", "rejected"])[:5]:
        record = next((x for x in returns if x["record_id"] == obj.pk), None)
        if record:
            add_notification(
                obj.created_at, "Return request", f"Return #{obj.pk} · {obj.status}",
                "return", record
            )

    for obj in tickets_qs.filter(
        status__in=["OPEN", "IN_PROGRESS", "WAITING"]
    )[:5]:
        record = next((x for x in tickets if x["record_id"] == obj.pk), None)
        if record:
            add_notification(
                obj.created_at, "Support ticket", obj.ticket_number, "ticket", record
            )

    notifications.sort(key=lambda item: item["date"], reverse=True)
    notifications = notifications[:30]

    # --------------------------------------------------
    # ORDER STATUS CHART
    # --------------------------------------------------
    status_rows = list(
        orders_qs.values("status").annotate(total=Count("id")).order_by("status")
    )
    status_labels = [row["status"].title() for row in status_rows]
    status_values = [row["total"] for row in status_rows]

    # --------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------
    context = {
        "metrics": metrics,
        "customers": customers,
        "sellers": sellers,
        "products": products,
        "orders": orders,
        "returns": returns,
        "tickets": tickets,
        "stock_records": stock_records,
        "visitors": visitors,
        "notifications": notifications,
        "status_labels_json": json.dumps(status_labels),
        "status_values_json": json.dumps(status_values),
        "generated_at": now,
    }

    return render(request, "admin/admin_dashboard.html", context)




from django.contrib.auth import logout
from django.shortcuts import redirect

def admin_logout(request):
    logout(request)
    return redirect('admin_login')  # or wherever you want to send them










from django.shortcuts import render, redirect, get_object_or_404
from .models import Catagory, Product, Placedorderxx
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

# ------------------ ADMIN DASHBOARD ------------------

# ------------------ CATEGORY ------------------

def category_list(request):
    categories = Catagory.objects.all()
    return render(request, "admin/category_list.html", {"categories": categories})


def category_add(request):
    if request.method == "POST":
        Catagory.objects.create(
            name=request.POST["name"],
            description=request.POST["description"],
            image=request.FILES.get("image"),
            status=request.POST.get("status") == "on"
        )
        return redirect("category_list")
    return render(request, "admin/category_form.html")




def category_edit(request, id):
    category = get_object_or_404(Catagory, id=id)

    # 🔒 Check if any product in this category is ordered
    if Placedorderxx.objects.filter(product__category=category).exists():
        messages.error(
            request,
            "This category contains products that have been ordered and cannot be edited."
        )
        return redirect("category_list")

    if request.method == "POST":
        category.name = request.POST["name"]
        category.description = request.POST["description"]
        category.status = request.POST.get("status") == "on"

        if request.FILES.get("image"):
            category.image = request.FILES["image"]

        category.save()
        messages.success(request, "Category updated successfully.")
        return redirect("category_list")

    return render(request, "admin/category_form.html", {"category": category})

def category_delete(request, id):
    category = get_object_or_404(Catagory, id=id)

    # 🔒 Check if any product in this category is ordered
    if Placedorderxx.objects.filter(product__category=category).exists():
        messages.error(
            request,
            "This category contains products that have been ordered and cannot be deleted."
        )
    else:
        category.delete()
        messages.success(request, "Category deleted successfully.")

    return redirect("category_list")


# ------------------ PRODUCT ------------------

def product_list(request):
    products = Product.objects.select_related("category")
    return render(request, "admin/product_list.html", {"products": products})



from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.dateparse import parse_date

from .models import Product, Catagory


def product_add(request):
    categories = Catagory.objects.all()

    if request.method == "POST":

        # -----------------------------
        # BASIC PRODUCT DETAILS
        # -----------------------------
        category_id = request.POST.get("category")
        name = request.POST.get("name", "").strip()
        vendor = request.POST.get("vendor", "").strip()
        quantity = request.POST.get("quantity", "").strip()

        original_price = request.POST.get("original_price", "").strip()
        selling_price = request.POST.get("selling_price", "").strip()

        description = request.POST.get("description", "").strip()

        # -----------------------------
        # SIZE
        # -----------------------------
        size = request.POST.get("size", "").strip()

        # If no size selected, use model default
        if not size:
            size = "M"

        # -----------------------------
        # SIZE PRICES
        # -----------------------------
        price_s = request.POST.get("price_s", "").strip()
        price_m = request.POST.get("price_m", "").strip()
        price_l = request.POST.get("price_l", "").strip()
        price_xl = request.POST.get("price_xl", "").strip()
        price_xxl = request.POST.get("price_xxl", "").strip()

        # If empty, use 0 instead of causing NOT NULL error
        price_s = float(price_s) if price_s else 0
        price_m = float(price_m) if price_m else 0
        price_l = float(price_l) if price_l else 0
        price_xl = float(price_xl) if price_xl else 0
        price_xxl = float(price_xxl) if price_xxl else 0

        # -----------------------------
        # COUPON DETAILS
        # -----------------------------
        coupon_code = request.POST.get("coupon_code", "").strip()

        coupon_discount = request.POST.get(
            "coupon_discount", ""
        ).strip()

        coupon_discount = (
            float(coupon_discount)
            if coupon_discount
            else 0
        )

        coupon_expiry = request.POST.get(
            "coupon_expiry", ""
        ).strip()

        coupon_expiry = (
            parse_date(coupon_expiry)
            if coupon_expiry
            else None
        )

        # Checkbox handling
        coupon_active = (
            request.POST.get("coupon_active") == "on"
        )

        coupon_used = (
            request.POST.get("coupon_used") == "on"
        )

        # -----------------------------
        # PRODUCT STATUS
        # -----------------------------
        status = (
            request.POST.get("status") == "on"
        )

        trending = (
            request.POST.get("trending") == "on"
        )

        # -----------------------------
        # VALIDATION
        # -----------------------------
        if not category_id:
            messages.error(request, "Please select a category.")
            return render(
                request,
                "admin/product_form.html",
                {"categories": categories}
            )

        if not name:
            messages.error(request, "Product name is required.")
            return render(
                request,
                "admin/product_form.html",
                {"categories": categories}
            )

        if not vendor:
            messages.error(request, "Vendor is required.")
            return render(
                request,
                "admin/product_form.html",
                {"categories": categories}
            )

        if not quantity:
            messages.error(request, "Quantity is required.")
            return render(
                request,
                "admin/product_form.html",
                {"categories": categories}
            )

        if not original_price:
            messages.error(
                request,
                "Original price is required."
            )
            return render(
                request,
                "admin/product_form.html",
                {"categories": categories}
            )

        if not selling_price:
            messages.error(
                request,
                "Selling price is required."
            )
            return render(
                request,
                "admin/product_form.html",
                {"categories": categories}
            )

        if not description:
            messages.error(
                request,
                "Product description is required."
            )
            return render(
                request,
                "admin/product_form.html",
                {"categories": categories}
            )

        # -----------------------------
        # CREATE PRODUCT
        # -----------------------------
        Product.objects.create(

            # Basic details
            category_id=category_id,
            name=name,
            vendor=vendor,
            quantity=quantity,

            original_price=original_price,
            selling_price=selling_price,

            description=description,

            # Main image
            product_image=request.FILES.get(
                "product_image"
            ),

            # Additional images
            product_image2=request.FILES.get(
                "product_image2"
            ),

            product_image3=request.FILES.get(
                "product_image3"
            ),

            product_image4=request.FILES.get(
                "product_image4"
            ),

            # Size
            size=size,

            # Coupon
            coupon_code=coupon_code or None,
            coupon_discount=coupon_discount,
            coupon_expiry=coupon_expiry,
            coupon_active=coupon_active,
            coupon_used=coupon_used,

            # Product visibility
            status=status,
            trending=trending,

            # Size prices
            price_s=price_s,
            price_m=price_m,
            price_l=price_l,
            price_xl=price_xl,
            price_xxl=price_xxl,
        )

        messages.success(
            request,
            "Product added successfully."
        )

        return redirect("product_list")

    return render(
        request,
        "admin/product_form.html",
        {
            "categories": categories,
        }
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.dateparse import parse_date

from .models import Product, Catagory, Placedorderxx


def product_edit(request, id):

    # Get product
    product = get_object_or_404(Product, id=id)

    # Get categories
    categories = Catagory.objects.all()

    # -------------------------------------------------
    # CHECK IF PRODUCT HAS ALREADY BEEN ORDERED
    # -------------------------------------------------
    if Placedorderxx.objects.filter(product=product).exists():
        messages.error(
            request,
            "This product has been ordered by customers and cannot be edited."
        )
        return redirect("product_list")

    # -------------------------------------------------
    # POST
    # -------------------------------------------------
    if request.method == "POST":

        # =============================================
        # BASIC PRODUCT DETAILS
        # =============================================

        product.name = request.POST.get("name", "").strip()

        product.vendor = request.POST.get(
            "vendor",
            ""
        ).strip()

        quantity = request.POST.get(
            "quantity",
            ""
        ).strip()

        original_price = request.POST.get(
            "original_price",
            ""
        ).strip()

        selling_price = request.POST.get(
            "selling_price",
            ""
        ).strip()

        product.description = request.POST.get(
            "description",
            ""
        ).strip()

        product.category_id = request.POST.get(
            "category"
        )

        # =============================================
        # VALIDATION
        # =============================================

        if not product.name:
            messages.error(
                request,
                "Product name is required."
            )
            return render(
                request,
                "admin/product_form.html",
                {
                    "product": product,
                    "categories": categories
                }
            )

        if not product.vendor:
            messages.error(
                request,
                "Vendor is required."
            )
            return render(
                request,
                "admin/product_form.html",
                {
                    "product": product,
                    "categories": categories
                }
            )

        if not quantity:
            messages.error(
                request,
                "Quantity is required."
            )
            return render(
                request,
                "admin/product_form.html",
                {
                    "product": product,
                    "categories": categories
                }
            )

        if not original_price:
            messages.error(
                request,
                "Original price is required."
            )
            return render(
                request,
                "admin/product_form.html",
                {
                    "product": product,
                    "categories": categories
                }
            )

        if not selling_price:
            messages.error(
                request,
                "Selling price is required."
            )
            return render(
                request,
                "admin/product_form.html",
                {
                    "product": product,
                    "categories": categories
                }
            )

        if not product.description:
            messages.error(
                request,
                "Product description is required."
            )
            return render(
                request,
                "admin/product_form.html",
                {
                    "product": product,
                    "categories": categories
                }
            )

        # =============================================
        # SAVE BASIC NUMERIC VALUES
        # =============================================

        product.quantity = int(quantity)

        product.original_price = float(
            original_price
        )

        product.selling_price = float(
            selling_price
        )

        # =============================================
        # PRODUCT SIZE
        # =============================================

        size = request.POST.get(
            "size",
            ""
        ).strip()

        if size:
            product.size = size
        else:
            product.size = "M"

        # =============================================
        # ADDITIONAL IMAGES
        # =============================================

        if request.FILES.get("product_image"):
            product.product_image = request.FILES[
                "product_image"
            ]

        if request.FILES.get("product_image2"):
            product.product_image2 = request.FILES[
                "product_image2"
            ]

        if request.FILES.get("product_image3"):
            product.product_image3 = request.FILES[
                "product_image3"
            ]

        if request.FILES.get("product_image4"):
            product.product_image4 = request.FILES[
                "product_image4"
            ]

        # =============================================
        # COUPON CODE
        # =============================================

        coupon_code = request.POST.get(
            "coupon_code",
            ""
        ).strip()

        if coupon_code:
            product.coupon_code = coupon_code
        else:
            product.coupon_code = None

        # =============================================
        # COUPON DISCOUNT
        # =============================================

        coupon_discount = request.POST.get(
            "coupon_discount",
            ""
        ).strip()

        if coupon_discount:
            try:
                product.coupon_discount = float(
                    coupon_discount
                )
            except ValueError:
                messages.error(
                    request,
                    "Invalid coupon discount."
                )
                return render(
                    request,
                    "admin/product_form.html",
                    {
                        "product": product,
                        "categories": categories
                    }
                )
        else:
            product.coupon_discount = 0

        # =============================================
        # COUPON EXPIRY
        # =============================================

        coupon_expiry = request.POST.get(
            "coupon_expiry",
            ""
        ).strip()

        if coupon_expiry:
            product.coupon_expiry = parse_date(
                coupon_expiry
            )

            if product.coupon_expiry is None:
                messages.error(
                    request,
                    "Invalid coupon expiry date."
                )
                return render(
                    request,
                    "admin/product_form.html",
                    {
                        "product": product,
                        "categories": categories
                    }
                )
        else:
            product.coupon_expiry = None

        # =============================================
        # COUPON ACTIVE
        # =============================================

        product.coupon_active = (
            request.POST.get("coupon_active") == "on"
        )

        # =============================================
        # COUPON USED
        # =============================================

        product.coupon_used = (
            request.POST.get("coupon_used") == "on"
        )

        # =============================================
        # PRODUCT STATUS
        # =============================================

        product.status = (
            request.POST.get("status") == "on"
        )

        # =============================================
        # TRENDING
        # =============================================

        product.trending = (
            request.POST.get("trending") == "on"
        )

        # =============================================
        # SIZE PRICES
        # =============================================

        price_fields = [
            "price_s",
            "price_m",
            "price_l",
            "price_xl",
            "price_xxl",
        ]

        for field_name in price_fields:

            value = request.POST.get(
                field_name,
                ""
            ).strip()

            if value:

                try:
                    setattr(
                        product,
                        field_name,
                        float(value)
                    )

                except ValueError:

                    messages.error(
                        request,
                        f"Invalid value for {field_name.replace('_', ' ').upper()}."
                    )

                    return render(
                        request,
                        "admin/product_form.html",
                        {
                            "product": product,
                            "categories": categories
                        }
                    )

            else:
                # Keep existing database value
                # instead of saving NULL
                current_value = getattr(
                    product,
                    field_name
                )

                if current_value is None:
                    setattr(
                        product,
                        field_name,
                        0
                    )

        # =============================================
        # SAVE PRODUCT
        # =============================================

        product.save()

        messages.success(
            request,
            "Product updated successfully."
        )

        return redirect("product_list")

    # -------------------------------------------------
    # GET
    # -------------------------------------------------

    return render(
        request,
        "admin/product_form.html",
        {
            "product": product,
            "categories": categories
        }
    )







from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

def admin_product_delete(request, id):
    """
    Admin can delete any product.
    Seller ownership restriction is NOT applied here.
    """

    # Get product without restricting vendor
    product = get_object_or_404(Product, id=id)

    # Only allow POST deletion
    if request.method != "POST":
        messages.error(
            request,
            "Invalid request. Product was not deleted."
        )
        return redirect("product_list")

    product_name = product.name

    # -----------------------------------------
    # OPTIONAL: Prevent deletion if ordered
    # -----------------------------------------
    is_ordered = Placedorderxx.objects.filter(
        product=product
    ).exists()

    if is_ordered:
        messages.error(
            request,
            f'"{product_name}" cannot be deleted because it has already been ordered.'
        )
        return redirect("product_list")

    # -----------------------------------------
    # DELETE PRODUCT
    # -----------------------------------------
    product.delete()

    messages.success(
        request,
        f'"{product_name}" deleted successfully.'
    )

    return redirect("product_list")




from django.shortcuts import render, get_object_or_404

def order_list(request):

    orders = (
        Placedorderxx.objects
        .select_related("user", "product")
        .order_by("created_at")
    )

    if request.method == "POST":

        order_id = request.POST.get("order_id")

        lock_seller = (
            request.POST.get("lock_seller") == "on"
        )

        order = get_object_or_404(
            Placedorderxx,
            id=order_id
        )

        # Update status only when supplied
        status = request.POST.get("status")

        if status:
            order.status = status

        # Lock / unlock seller access
        order.updated_by_admin = lock_seller

        order.save()

        # Prevent form resubmission
        return redirect("order_list")

    return render(
        request,
        "admin/order_list.html",
        {
            "orders": orders
        }
    )




def update_order_status(request, id):
    order = get_object_or_404(Placedorderxx, id=id)
    if request.method == "POST":
        order.status = request.POST["status"]
        order.save()
    return redirect("order_list")


def customer_address(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "admin/customer_address.html", {"user": user})


def product_detailz(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "admin/product_detailz.html", {"product": product})

# ------------------ CUSTOMER ORDERS ------------------

def customer_orders(request):
    orders = Placedorderxx.objects.filter(user=request.user)
    return render(request, "admin/my_orders.html", {"orders": orders})






from django.shortcuts import render
from .models import SiteVisit

def visit_list(request):
    visits = SiteVisit.objects.all().order_by('-start_time')
    return render(request, 'admin/visit_list.html', {'visits': visits})

















from django.shortcuts import render
from .models import CustomerLoginLogout

def customer_activity_view(request):
    records = CustomerLoginLogout.objects.select_related('customer').all().order_by('-login_time')
    context = {
        'records': records
    }
    return render(request, 'admin/customer_activity.html', context)









from datetime import timedelta

from django.db.models import (
    F,
    Sum,
    Value,
    DecimalField,
    ExpressionWrapper,
    CharField,
)
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils.timezone import now

from .models import Placedorderxx


def sales_report(request):

    today = now().date()

    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)


    revenue_expression = ExpressionWrapper(
        F('total_amount'),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2
        )
    )


    daily_sales = (
        Placedorderxx.objects
        .filter(
            ordered_date__date=today,
            status='completed'
        )
        .select_related('product')
        .order_by('-ordered_date')
    )

    daily_total_quantity = (
        daily_sales.aggregate(
            total_qty=Sum('quantity')
        )['total_qty'] or 0
    )

    daily_revenue = (
        daily_sales.aggregate(
            total_revenue=Sum(revenue_expression)
        )['total_revenue'] or 0
    )

 
    weekly_sales = (
        Placedorderxx.objects
        .filter(
            ordered_date__date__gte=week_ago,
            status='completed'
        )
        .select_related('product')
        .order_by('-ordered_date')
    )

    weekly_total_quantity = (
        weekly_sales.aggregate(
            total_qty=Sum('quantity')
        )['total_qty'] or 0
    )

    weekly_revenue = (
        weekly_sales.aggregate(
            total_revenue=Sum(revenue_expression)
        )['total_revenue'] or 0
    )


    monthly_sales = (
        Placedorderxx.objects
        .filter(
            ordered_date__date__gte=month_ago,
            status='completed'
        )
        .select_related('product')
        .order_by('-ordered_date')
    )

    monthly_total_quantity = (
        monthly_sales.aggregate(
            total_qty=Sum('quantity')
        )['total_qty'] or 0
    )

    monthly_revenue = (
        monthly_sales.aggregate(
            total_revenue=Sum(revenue_expression)
        )['total_revenue'] or 0
    )

  
    yearly_sales = (
        Placedorderxx.objects
        .filter(
            ordered_date__date__gte=year_ago,
            status='completed'
        )
        .select_related('product')
        .order_by('-ordered_date')
    )

    yearly_total_quantity = (
        yearly_sales.aggregate(
            total_qty=Sum('quantity')
        )['total_qty'] or 0
    )

    yearly_revenue = (
        yearly_sales.aggregate(
            total_revenue=Sum(revenue_expression)
        )['total_revenue'] or 0
    )

    product_summary = (
        Placedorderxx.objects
        .filter(
            status='completed'
        )
        .values(
            'product_name'
        )
        .annotate(
            total_quantity=Sum('quantity'),
            total_price=Sum('total_amount')
        )
        .order_by('-total_quantity')
    )


    context = {

        # Sales QuerySets
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,

        # Quantities
        'daily_total_quantity': daily_total_quantity,
        'weekly_total_quantity': weekly_total_quantity,
        'monthly_total_quantity': monthly_total_quantity,
        'yearly_total_quantity': yearly_total_quantity,

        # Revenue
        'daily_revenue': daily_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'yearly_revenue': yearly_revenue,

        # Product summary
        'product_summary': product_summary,
    }

    return render(
        request,
        'admin/sales_report.html',
        context
    )


from django.shortcuts import render
from django.contrib.auth.models import User
from .models import UserLoginHistory

def user_login_history_view(request):
    # Fetch all users
    users = User.objects.all()
    
    # Prepare data
    data = []
    for user in users:
        for history in user.login_history.all().order_by('-login_time'):
            data.append({
                'username': user.username,
                'email': user.email,
                'login_time': history.login_time,
                'logout_time': history.logout_time,
            })

    return render(request, 'admin/user_login_history.html', {'data': data})




from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.models import User

from .models import Placedorderxx, SellerProfile


def top_selling_products(request):

    # ---------------------------------------------------------
    # TOP 5 SELLING PRODUCTS
    # ---------------------------------------------------------
    sales = (
        Placedorderxx.objects
        .filter(
            status__in=['delivered', 'completed'],
            product__isnull=False
        )
        .values(
            'product_id',
            'product__name',
            'product__vendor'
        )
        .annotate(
            total_sold=Sum('quantity')
        )
        .order_by('-total_sold')[:5]
    )

    labels = []
    data = []
    products_data = []

    # ---------------------------------------------------------
    # LOAD SELLER PROFILES
    # ---------------------------------------------------------
    seller_usernames = [
        item['product__vendor']
        for item in sales
        if item['product__vendor']
    ]

    seller_profiles = (
        SellerProfile.objects
        .select_related('user')
        .filter(user__username__in=seller_usernames)
    )

    seller_map = {
        profile.user.username: profile
        for profile in seller_profiles
    }

    # ---------------------------------------------------------
    # HELPER
    # ---------------------------------------------------------
    def get_field_value(obj, field_name, default=""):
        """
        Safely retrieve SellerProfile field values.
        This prevents the page from breaking if an optional
        field is not present or is empty.
        """

        try:
            value = getattr(obj, field_name, default)

            if value is None:
                return default

            return value
        except Exception:
            return default

    # ---------------------------------------------------------
    # BUILD PRODUCT + SELLER DATA
    # ---------------------------------------------------------
    for item in sales:

        product_name = item['product__name'] or 'Unknown Product'
        vendor = item['product__vendor'] or 'Unknown Seller'
        total_sold = item['total_sold'] or 0

        labels.append(product_name)
        data.append(total_sold)

        profile = seller_map.get(vendor)

        seller = {
            "username": vendor,
            "email": "",
            "first_name": "",
            "last_name": "",
            "full_name": vendor,
            "company": "",
            "mobile": "",
            "phone": "",
            "address": "",
            "state": "",
            "city": "",
            "pincode": "",
            "country": "",
            "business_type": "",
            "gst_number": "",
            "pan_number": "",
            "aadhar_number": "",
            "profile_photo": "",
            "seller_id": "",
            "status": "",
        }

        # -----------------------------------------------------
        # USER DETAILS
        # -----------------------------------------------------
        if profile and profile.user:

            user = profile.user

            seller["username"] = user.username or vendor
            seller["email"] = user.email or ""
            seller["first_name"] = user.first_name or ""
            seller["last_name"] = user.last_name or ""

            full_name = (
                f"{user.first_name} {user.last_name}"
            ).strip()

            seller["full_name"] = (
                full_name
                if full_name
                else user.username
            )

            seller["status"] = (
                "Active"
                if user.is_active
                else "Inactive"
            )

        # -----------------------------------------------------
        # SELLER PROFILE DETAILS
        # -----------------------------------------------------
        if profile:

            seller["seller_id"] = str(
                get_field_value(profile, "id", "")
            )

            seller["company"] = str(
                get_field_value(profile, "company", "")
            )

            seller["mobile"] = str(
                get_field_value(profile, "mobile", "")
            )

            seller["phone"] = str(
                get_field_value(profile, "phone", "")
            )

            seller["address"] = str(
                get_field_value(profile, "address", "")
            )

            seller["state"] = str(
                get_field_value(profile, "state", "")
            )

            seller["city"] = str(
                get_field_value(profile, "city", "")
            )

            seller["pincode"] = str(
                get_field_value(profile, "pincode", "")
            )

            seller["country"] = str(
                get_field_value(profile, "country", "")
            )

            seller["business_type"] = str(
                get_field_value(profile, "business_type", "")
            )

            seller["gst_number"] = str(
                get_field_value(profile, "gst_number", "")
            )

            seller["pan_number"] = str(
                get_field_value(profile, "pan_number", "")
            )

            seller["aadhar_number"] = str(
                get_field_value(profile, "aadhar_number", "")
            )

            # -------------------------------------------------
            # PROFILE PHOTO
            # -------------------------------------------------
            profile_photo = get_field_value(
                profile,
                "profile_photo",
                ""
            )

            try:
                if profile_photo:
                    seller["profile_photo"] = profile_photo.url
            except Exception:
                seller["profile_photo"] = ""

        # -----------------------------------------------------
        # PRODUCT INFORMATION
        # -----------------------------------------------------
        products_data.append({
            "product_id": item["product_id"],
            "name": product_name,
            "vendor": vendor,
            "units": int(total_sold),
            "seller": seller,
        })

    # ---------------------------------------------------------
    # TOP SELLER
    # ---------------------------------------------------------
    seller_sales = {}

    for item in products_data:

        seller_name = (
            item["seller"].get("company")
            or item["seller"].get("full_name")
            or item["vendor"]
        )

        seller_sales[seller_name] = (
            seller_sales.get(seller_name, 0)
            + item["units"]
        )

    top_seller = "—"

    if seller_sales:
        top_seller = max(
            seller_sales,
            key=seller_sales.get
        )

    # ---------------------------------------------------------
    # CONTEXT
    # ---------------------------------------------------------
    context = {
        "labels": labels,
        "data": data,
        "products_data": products_data,
        "top_seller": top_seller,
    }

    return render(
        request,
        "admin/top_selling_products.html",
        context
    )


# views.py
from django.shortcuts import render
from django.db.models import Count
from .models import Placedorderxx

def order_status_chart(request):
    orders = (
        Placedorderxx.objects
        .values('status')
        .annotate(total=Count('id'))
    )

    labels = [o['status'].capitalize() for o in orders]
    data = [o['total'] for o in orders]

    return render(request, 'admin/order_status_chart.html', {
        'labels': labels,
        'data': data
    })




from datetime import timedelta

from django.shortcuts import render
from django.db.models import (
    Sum,
    F,
    DecimalField,
    ExpressionWrapper,
)
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import Placedorderxx, SellerProfile


def admin_line_sales(request):

    today = timezone.now().date()

    start_date = today - timedelta(days=6)

    revenue_expression = ExpressionWrapper(
        F("quantity") * F("selling_price"),
        output_field=DecimalField(
            max_digits=14,
            decimal_places=2
        )
    )

    base_sales = (
        Placedorderxx.objects
        .filter(
            status__in=[
                "delivered",
                "completed"
            ],
            created_at__date__gte=start_date,
            created_at__date__lte=today
        )
        .annotate(
            day=TruncDate("created_at"),
            revenue=revenue_expression
        )
    )

    daily_sales = (
        base_sales
        .values("day")
        .annotate(
            total=Sum("revenue")
        )
        .order_by("day")
    )


    daily_sales_map = {
        item["day"]: float(
            item["total"] or 0
        )
        for item in daily_sales
    }


    labels = []

    data = []

    full_dates = []


    for i in range(7):

        day = start_date + timedelta(days=i)

        full_dates.append(day)

        labels.append(
            day.strftime("%a")
        )

        data.append(
            daily_sales_map.get(
                day,
                0
            )
        )


    seller_daily_sales = (
        base_sales
        .values(
            "day",
            "vendor"
        )
        .annotate(
            total=Sum("revenue"),
            units=Sum("quantity")
        )
        .order_by(
            "day",
            "-total"
        )
    )

    seller_totals = (
        base_sales
        .values("vendor")
        .annotate(
            total_revenue=Sum("revenue"),
            total_units=Sum("quantity")
        )
        .order_by("-total_revenue")
    )

    seller_usernames = list(
        seller_totals.values_list(
            "vendor",
            flat=True
        )
    )


    seller_profiles = (
        SellerProfile.objects
        .select_related("user")
        .filter(
            user__username__in=seller_usernames
        )
    )


    seller_profile_map = {
        profile.user.username: profile
        for profile in seller_profiles
    }

    def get_field(
        obj,
        field,
        default=""
    ):

        try:

            value = getattr(
                obj,
                field,
                default
            )

            if value is None:
                return default

            return str(value)

        except Exception:

            return default

    sellers_data = []


    for seller_item in seller_totals:

        username = (
            seller_item["vendor"]
            or "Unknown Seller"
        )


        profile = seller_profile_map.get(
            username
        )


        seller = {

            "username":
                username,

            "full_name":
                username,

            "email":
                "",

            "company":
                "",

            "mobile":
                "",

            "phone":
                "",

            "address":
                "",

            "city":
                "",

            "state":
                "",

            "pincode":
                "",

            "country":
                "",

            "business_type":
                "",

            "gst_number":
                "",

            "pan_number":
                "",

            "aadhar_number":
                "",

            "profile_photo":
                "",

            "seller_id":
                "",

            "status":
                "Unknown",

            "total_revenue":
                float(
                    seller_item[
                        "total_revenue"
                    ] or 0
                ),

            "total_units":
                int(
                    seller_item[
                        "total_units"
                    ] or 0
                ),

            "daily_revenue": {},

        }


        # -----------------------------------------------------
        # USER DETAILS
        # -----------------------------------------------------

        if profile and profile.user:

            user = profile.user


            seller["username"] = (
                user.username
                or username
            )


            seller["email"] = (
                user.email
                or ""
            )


            full_name = (
                f"{user.first_name} "
                f"{user.last_name}"
            ).strip()


            seller["full_name"] = (
                full_name
                if full_name
                else user.username
            )


            seller["status"] = (
                "Active"
                if user.is_active
                else "Inactive"
            )

        if profile:

            seller["seller_id"] = get_field(
                profile,
                "id"
            )


            seller["company"] = get_field(
                profile,
                "company"
            )


            seller["mobile"] = get_field(
                profile,
                "mobile"
            )


            seller["phone"] = get_field(
                profile,
                "phone"
            )


            seller["address"] = get_field(
                profile,
                "address"
            )


            seller["city"] = get_field(
                profile,
                "city"
            )


            seller["state"] = get_field(
                profile,
                "state"
            )


            seller["pincode"] = get_field(
                profile,
                "pincode"
            )


            seller["country"] = get_field(
                profile,
                "country"
            )


            seller["business_type"] = get_field(
                profile,
                "business_type"
            )


            seller["gst_number"] = get_field(
                profile,
                "gst_number"
            )


            seller["pan_number"] = get_field(
                profile,
                "pan_number"
            )


            seller["aadhar_number"] = get_field(
                profile,
                "aadhar_number"
            )


            # -------------------------------------------------
            # PROFILE PHOTO
            # -------------------------------------------------

            try:

                if profile.profile_photo:

                    seller["profile_photo"] = (
                        profile.profile_photo.url
                    )

            except Exception:

                seller["profile_photo"] = ""


        # -----------------------------------------------------
        # SELLER DAILY REVENUE
        # -----------------------------------------------------

        seller_days = (
            seller_daily_sales
            .filter(
                vendor=username
            )
        )


        for day_item in seller_days:

            day_key = day_item["day"].isoformat()

            seller["daily_revenue"][
                day_key
            ] = float(
                day_item["total"] or 0
            )


        sellers_data.append(
            seller
        )
    product_totals = (
        base_sales
        .values(
            "product_id",
            "product_name",
            "vendor"
        )
        .annotate(
            total_revenue=Sum("revenue"),
            total_units=Sum("quantity")
        )
        .order_by(
            "-total_revenue"
        )
    )


    products_data = []


    for product in product_totals:

        product_name = (
            product["product_name"]
            or "Unknown Product"
        )


        vendor = (
            product["vendor"]
            or "Unknown Seller"
        )


        product_daily = (
            base_sales
            .filter(
                product_id=
                    product["product_id"]
            )
            .values("day")
            .annotate(
                total=Sum("revenue")
            )
            .order_by("day")
        )


        product_daily_map = {
            item["day"].isoformat():
                float(
                    item["total"] or 0
                )
            for item in product_daily
        }


        products_data.append({

            "id":
                product["product_id"],

            "name":
                product_name,

            "vendor":
                vendor,

            "total_revenue":
                float(
                    product[
                        "total_revenue"
                    ] or 0
                ),

            "total_units":
                int(
                    product[
                        "total_units"
                    ] or 0
                ),

            "daily_revenue":
                product_daily_map,

        })


    top_seller = (
        sellers_data[0]
        if sellers_data
        else None
    )


    top_product = (
        products_data[0]
        if products_data
        else None
    )


    total_revenue = sum(data)

    average_revenue = (
        total_revenue / 7
        if total_revenue
        else 0
    )


    highest_revenue = (
        max(data)
        if data
        else 0
    )


    highest_index = (
        data.index(highest_revenue)
        if data and highest_revenue
        else -1
    )


    highest_day = (
        labels[highest_index]
        if highest_index >= 0
        else "—"
    )


    total_units = sum(
        seller["total_units"]
        for seller in sellers_data
    )

    context = {

        # Total daily chart
        "labels":
            labels,

        "data":
            data,

        "full_dates":
            [
                day.isoformat()
                for day in full_dates
            ],


        # Seller information
        "sellers_data":
            sellers_data,


        # Product information
        "products_data":
            products_data,


        # Summary
        "total_revenue":
            total_revenue,

        "average_revenue":
            average_revenue,

        "highest_revenue":
            highest_revenue,

        "highest_day":
            highest_day,

        "total_units":
            total_units,


        # Top performers
        "top_seller":
            top_seller,

        "top_product":
            top_product,
    }


    return render(
        request,
        "admin/admin_line_sales.html",
        context
    )





from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import SellerProfile

# 🔹 List all sellers
def admin_contoll_seller_details(request):
    sellers = SellerProfile.objects.select_related('user').all()
    return render(request, 'admin/admin_contoll_seller_details.html', {'sellers': sellers})

# 🔹 Update seller status (approve/reject/block)
def admin_seller_update_status(request, id):
    seller = get_object_or_404(SellerProfile, id=id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(SellerProfile.STATUS_CHOICES).keys():
            seller.status = new_status
            seller.save()
            messages.success(request, f"Seller '{seller.user.username}' status updated to '{new_status}'.")
        else:
            messages.error(request, "Invalid status selected.")
        return redirect('admin_contoll_seller_details')
    
    return render(request, 'admin/seller_update_status.html', {'seller': seller})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import SellerProfile
from django.contrib.auth.models import User

# 🔹 List all sellers
def admin_contoll_seller_details(request):
    sellers = SellerProfile.objects.select_related('user').all()
    return render(request, 'admin/admin_contoll_seller_details.html', {'sellers': sellers})







from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect

from .models import SellerProfile


def send_seller_email(subject, message, seller):
    """
    Send email to seller.

    Priority:
    1. SellerProfile.email
    2. User.email
    """

    recipient = (
        seller.email
        or getattr(seller.user, "email", "")
    )

    if not recipient:
        return False

    try:

        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(
                settings,
                "DEFAULT_FROM_EMAIL",
                None
            ),
            recipient_list=[recipient],
            fail_silently=False,
        )

        return True

    except Exception as e:

        print(
            f"Seller email failed for seller "
            f"{seller.id}: {e}"
        )

        return False


def admin_seller_detail(request, id):

    seller = get_object_or_404(
        SellerProfile.objects.select_related("user"),
        id=id
    )


    if request.method == "POST":

        old_status = seller.status

        old_is_locked = seller.is_locked

        old_block_reason = (
            seller.account_block_reason or ""
        )

        seller.email = request.POST.get(
            "email",
            seller.email or ""
        ).strip()

        seller.mobile_number = request.POST.get(
            "mobile_number",
            seller.mobile_number or ""
        ).strip()

        seller.gender = request.POST.get(
            "gender",
            seller.gender or ""
        )

        date_of_birth = request.POST.get(
            "date_of_birth"
        )

        if date_of_birth:
            seller.date_of_birth = date_of_birth
        else:
            seller.date_of_birth = None


        wedding_anniversary = request.POST.get(
            "wedding_anniversary"
        )

        if wedding_anniversary:
            seller.wedding_anniversary = (
                wedding_anniversary
            )
        else:
            seller.wedding_anniversary = None


        seller.business_type = request.POST.get(
            "business_type",
            seller.business_type
        )

        seller.company_name = request.POST.get(
            "company_name",
            seller.company_name or ""
        ).strip()

        seller.gstinnamber = request.POST.get(
            "gstinnamber",
            seller.gstinnamber or ""
        ).strip()

        seller.tax_classification = request.POST.get(
            "tax_classification",
            seller.tax_classification or ""
        ).strip()

        seller.address = request.POST.get(
            "address",
            seller.address or ""
        )

        seller.country = request.POST.get(
            "country",
            seller.country or ""
        )

        seller.state = request.POST.get(
            "state",
            seller.state or ""
        )

        seller.city = request.POST.get(
            "city",
            seller.city or ""
        )

        seller.pincode = request.POST.get(
            "pincode",
            seller.pincode or ""
        )

        new_status = request.POST.get(
            "status",
            seller.status
        )

        valid_statuses = dict(
            SellerProfile.STATUS_CHOICES
        ).keys()

        if new_status in valid_statuses:
            seller.status = new_status
        else:
            seller.status = old_status

        rejection_reason = request.POST.get(
            "rejection_reason",
            ""
        ).strip()


        if seller.status == "rejected":

            if not rejection_reason:

                messages.error(
                    request,
                    "Please enter a rejection reason."
                )

                return render(
                    request,
                    "admin/admin_seller_detail.html",
                    {
                        "seller": seller,
                        "status_choices":
                            SellerProfile.STATUS_CHOICES,
                        "business_types":
                            SellerProfile.BUSINESS_TYPES,
                    }
                )

            seller.rejection_reason = (
                rejection_reason
            )


        login_attempts = request.POST.get(
            "login_attempts",
            "0"
        )

        try:

            seller.login_attempts = max(
                0,
                int(login_attempts)
            )

        except (ValueError, TypeError):

            seller.login_attempts = 0


        new_is_locked = (
            request.POST.get("is_locked") == "True"
        )

        seller.is_locked = new_is_locked

        account_block_reason = request.POST.get(
            "account_block_reason",
            ""
        ).strip()


        if new_is_locked:

            if not account_block_reason:

                messages.error(
                    request,
                    "Please enter an account block reason."
                )

                return render(
                    request,
                    "admin/admin_seller_detail.html",
                    {
                        "seller": seller,
                        "status_choices":
                            SellerProfile.STATUS_CHOICES,
                        "business_types":
                            SellerProfile.BUSINESS_TYPES,
                    }
                )

            seller.account_block_reason = (
                account_block_reason
            )

        else:

            # Clear block reason after account is unlocked.
            seller.account_block_reason = ""

        seller.terms_accepted = (
            request.POST.get(
                "terms_accepted"
            ) == "on"
        )

        seller.privacy_policy_accepted = (
            request.POST.get(
                "privacy_policy_accepted"
            ) == "on"
        )

        seller.return_policy_accepted = (
            request.POST.get(
                "return_policy_accepted"
            ) == "on"
        )

        seller.commission_agreement_accepted = (
            request.POST.get(
                "commission_agreement_accepted"
            ) == "on"
        )


        seller.mobile_verified = (
            request.POST.get(
                "mobile_verified"
            ) == "on"
        )

        seller.email_verified = (
            request.POST.get(
                "email_verified"
            ) == "on"
        )

        seller.bank_verified = (
            request.POST.get(
                "bank_verified"
            ) == "on"
        )

        seller.gst_verified = (
            request.POST.get(
                "gst_verified"
            ) == "on"
        )

        latitude = request.POST.get(
            "latitude"
        )

        if latitude:
            seller.latitude = latitude
        else:
            seller.latitude = None


        longitude = request.POST.get(
            "longitude"
        )

        if longitude:
            seller.longitude = longitude
        else:
            seller.longitude = None


        seller.live_location = request.POST.get(
            "live_location",
            seller.live_location or "unknown"
        )

        if request.FILES.get("profile_photo"):

            seller.profile_photo = (
                request.FILES["profile_photo"]
            )


        if request.FILES.get("aadhar_image"):

            seller.aadhar_image = (
                request.FILES["aadhar_image"]
            )


        seller.aadhar_number = request.POST.get(
            "aadhar_number",
            seller.aadhar_number or ""
        ).strip()


        if request.FILES.get("pan_image"):

            seller.pan_image = (
                request.FILES["pan_image"]
            )


        seller.pan_number = request.POST.get(
            "pan_number",
            seller.pan_number or ""
        ).strip()


        if request.FILES.get(
            "partner_kyc_document"
        ):

            seller.partner_kyc_document = (
                request.FILES[
                    "partner_kyc_document"
                ]
            )


        if request.FILES.get(
            "director_kyc_document"
        ):

            seller.director_kyc_document = (
                request.FILES[
                    "director_kyc_document"
                ]
            )


        file_fields = [

            "registered_office_proof",

            "gst_certificate",

            "incorporation_certificate",

            "partnership_deed",

            "llp_agreement",

            "moa_document",

            "aoa_document",

            "udyam_registration",

            "shop_establishment_license",

            "trademark_certificate",

            "brand_authorization_letter",

            "business_license",

        ]


        for field_name in file_fields:

            uploaded_file = request.FILES.get(
                field_name
            )

            if uploaded_file:

                setattr(
                    seller,
                    field_name,
                    uploaded_file
                )

        if request.FILES.get(
            "liveface_scan"
        ):

            seller.liveface_scan = (
                request.FILES[
                    "liveface_scan"
                ]
            )

        seller.save()

        if (
            old_status != "rejected"
            and seller.status == "rejected"
        ):

            subject = (
                "Seller Application Rejected"
            )

            message = f"""
Dear {seller.company_name or seller.user.username},

Your seller account/application has been rejected by the administrator.

Reason for rejection:
{seller.rejection_reason}

Seller ID: {seller.id}

Please review the above reason and contact the administrator if you require further clarification.

Regards,
Admin Team
"""

            send_seller_email(
                subject,
                message,
                seller
            )


        elif (
            old_status != "approved"
            and seller.status == "approved"
        ):

            subject = (
                "Seller Account Approved"
            )

            message = f"""
Dear {seller.company_name or seller.user.username},

Congratulations!

Your seller account has been approved by the administrator.

Seller ID: {seller.id}
Company: {seller.company_name}

You can now access your seller account and use the available seller features.

Regards,
Admin Team
"""

            send_seller_email(
                subject,
                message,
                seller
            )

        if (
            old_is_locked is False
            and seller.is_locked is True
        ):

            subject = (
                "Seller Account Blocked"
            )

            message = f"""
Dear {seller.company_name or seller.user.username},

Your seller account has been blocked by the administrator.

Seller ID: {seller.id}
Company: {seller.company_name or "-"}

Reason for blocking:
{seller.account_block_reason}

You will not be able to access your seller account while it is blocked.

If you believe this action was taken in error, please contact the administrator/support team.

Regards,
Admin Team
"""

            send_seller_email(
                subject,
                message,
                seller
            )


        elif (
            old_is_locked is True
            and seller.is_locked is False
        ):

            subject = (
                "Seller Account Unlocked"
            )

            message = f"""
Dear {seller.company_name or seller.user.username},

Your seller account has been unlocked by the administrator.

Seller ID: {seller.id}
Company: {seller.company_name or "-"}

You can now log in to your seller account normally.

Regards,
Admin Team
"""

            send_seller_email(
                subject,
                message,
                seller
            )

        messages.success(
            request,
            "Seller details updated successfully."
        )


        return redirect(
            "admin_contoll_seller_details"
        )

    return render(
        request,
        "admin/admin_seller_detail.html",
        {
            "seller": seller,

            "status_choices":
                SellerProfile.STATUS_CHOICES,

            "business_types":
                SellerProfile.BUSINESS_TYPES,
        }
    )




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import SellerBankDetailxx
from .forms import SellerBankFormxx


def admin_seller_bank_list(request):
    banks = SellerBankDetailxx.objects.select_related('seller')
    return render(
        request,
        'admin/admin_seller_bank_list.html',
        {'banks': banks}
    )


def admin_seller_bank_by_seller(request, seller_id):
    banks = SellerBankDetailxx.objects.filter(
        seller_id=seller_id
    ).select_related('seller')

    return render(
        request,
        'admin/admin_seller_bank_by_seller.html',
        {'banks': banks}
    )




from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .forms import SellerBankFormxx
from .models import SellerBankDetailxx
import requests

def admin_seller_bank_edit(request, bank_id):
    bank = get_object_or_404(SellerBankDetailxx, id=bank_id)

    if request.method == 'POST':
        form = SellerBankFormxx(request.POST, instance=bank)
        if form.is_valid():
            ifsc = form.cleaned_data.get('ifsc_code', '').strip()

            # Server-side IFSC validation using Razorpay API
            try:
                response = requests.get(f'https://ifsc.razorpay.com/{ifsc}', timeout=5)
                if response.status_code != 200:
                    messages.error(request, 'Invalid IFSC code. Please enter a correct one.')
                    return render(request, 'admin/admin_seller_bank_edit.html', {'form': form, 'bank': bank})
                
                data = response.json()
                bank_name = data.get('BANK')
                branch = data.get('BRANCH')
                bank_code = data.get('CENTRE') or data.get('MICR') or ''

            except requests.RequestException:
                messages.error(request, 'Error validating IFSC code. Try again.')
                return render(request, 'admin/admin_seller_bank_edit.html', {'form': form, 'bank': bank})

            # Save form and update auto-filled fields
            bank = form.save(commit=False)
            bank.bank_name = bank_name
            bank.bank_branch = branch
            bank.bank_code = bank_code

            # Admin-controlled fields
            bank.status = request.POST.get('status', bank.status)
            bank.verified = 'verified' in request.POST
            if bank.verified:
                bank.status = 'verified'

            bank.save()
            messages.success(request, 'Bank details updated successfully.')
            return redirect('admin_seller_bank_list')
    else:
        form = SellerBankFormxx(instance=bank)

    return render(request, 'admin/admin_seller_bank_edit.html', {'form': form, 'bank': bank})





# ---------------- BANK VERIFICATION (MOCK) ----------------


from django.shortcuts import render, redirect
from .forms import SellerBankForm
from .models import SellerBankDetailxx
import requests
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Function to get bank details from IFSC
def get_bank_details_from_ifsc(ifsc_code):
    url = f"https://ifsc.razorpay.com/{ifsc_code}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'bank_name': data.get('BANK'),
                'bank_branch': data.get('BRANCH'),
                'bank_code': data.get('BANKCODE')
            }
    except Exception as e:
        print("IFSC lookup failed:", e)
    return None

































































































# Page 2: View seller bank details
@login_required
def seller_bank_view(request):
    try:
        bank_details = SellerBankDetailxx.objects.get(seller=request.user)
    except SellerBankDetailxx.DoesNotExist:
        bank_details = None

    return render(request, 'saller/seller_bank_view.html', {'bank_details': bank_details})











from django.shortcuts import render, redirect
from .forms import SellerBankForm
from .models import SellerBankDetailxx
import requests
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Function to get bank details from IFSC
def get_bank_details_from_ifsc(ifsc_code):
    url = f"https://ifsc.razorpay.com/{ifsc_code}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'bank_name': data.get('BANK'),
                'bank_branch': data.get('BRANCH'),
                'bank_code': data.get('BANKCODE')
            }
    except Exception as e:
        print("IFSC lookup failed:", e)
    return None

# Seller Bank Form: Add or View (read-only if exists)
@login_required
def seller_bank_form(request):
    # Check if the seller already has bank details
    try:
        bank_details = SellerBankDetailxx.objects.get(seller=request.user)
        bank_exists = True
    except SellerBankDetailxx.DoesNotExist:
        bank_details = None
        bank_exists = False

    if request.method == 'POST':
        if bank_exists:
            # Prevent resubmission
            messages.error(request, "You cannot modify your bank details after submission.")
            return redirect('seller_bank_view')

        form = SellerBankForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.seller = request.user

            # IFSC verification
            ifsc = form.cleaned_data['ifsc_code']
            bank_data = get_bank_details_from_ifsc(ifsc)
            if bank_data:
                obj.bank_name = bank_data['bank_name']
                obj.bank_branch = bank_data['bank_branch']
                obj.bank_code = bank_data['bank_code']
                obj.status = 'verified'
                obj.verified = True
                messages.success(request, "Bank details verified successfully!")
            else:
                obj.status = 'rejected'
                obj.verified = False
                messages.error(request, "Invalid IFSC code. Bank details could not be verified.")

            obj.save()
            return redirect('seller_bank_view')
    else:
        form = SellerBankForm(instance=bank_details)

    return render(request, 'saller/seller_bank_form.html', {
        'form': form,
        'bank_exists': bank_exists  # To disable form fields in template
    })




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SellerProfile
from .forms import SellerProfileForm

@login_required
def seller_profile(request):
    profile = get_object_or_404(SellerProfile, user=request.user)
    is_locked = profile.status in ['approved', 'blocked']

    if request.method == 'POST':
        if is_locked:
            return redirect('seller-profile')  # Prevent updates
        form = SellerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('seller-profile')
    else:
        form = SellerProfileForm(instance=profile)

    # Disable fields if locked
    if is_locked:
        for field in form.fields.values():
            field.disabled = True

    return render(request, 'saller/seller_profile.html', {
        'profile': profile,
        'form': form,
        'is_locked': is_locked,
    })









from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product, Placedorderxx


def saller_low_stock(request):
    """
    Display all products with quantity less than 5 for the logged-in seller.
    """
    seller_username = request.user.username  # Assuming vendor stores username
    products = Product.objects.filter(vendor=seller_username, quantity__lt=5)
    return render(request, 'saller/saller_low_stock.html', {'products': products})



def seller_neworders(request):
    """
    Display all orders for the logged-in seller's products.
    """
    seller_username = request.user.username
    orders = Placedorderxx.objects.filter(product__vendor=seller_username).select_related('product', 'user')

    return render(request, 'saller/seller_neworders.html', {'orders': orders})






from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import SellerProfile

def seller_register(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        company_name = request.POST.get('company_name').strip()
        mobile = request.POST.get('mobile').strip()
        address = request.POST.get('address').strip()
        state = request.POST.get('state').strip()
        city = request.POST.get('city').strip()
        pincode = request.POST.get('pincode').strip()
        country = request.POST.get('country').strip()
        aadhar = request.POST.get('aadhar').strip()
        pan = request.POST.get('pan').strip()

        # ---------- VALIDATIONS ----------

        # Username unique
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('seller_register')

        # Email unique
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('seller_register')

        # Mobile unique
        if SellerProfile.objects.filter(mobile_number=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return redirect('seller_register')

        # Aadhar unique
        if SellerProfile.objects.filter(aadhar_number=aadhar).exists():
            messages.error(request, "Aadhar number already registered.")
            return redirect('seller_register')

        # PAN unique
        if SellerProfile.objects.filter(pan_number=pan).exists():
            messages.error(request, "PAN number already registered.")
            return redirect('seller_register')

        # ---------- CREATE USER & PROFILE ----------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        SellerProfile.objects.create(
            user=user,
            email=email,
            company_name=company_name,
            mobile_number=mobile,
            address=address,
            state=state,
            city=city,
            pincode=pincode,
            country=country,
            aadhar_number=aadhar,
            aadhar_image=request.FILES.get('aadhar_image'),
            pan_number=pan,
            pan_image=request.FILES.get('pan_image'),

            gstinnamber=request.POST.get("gstinnamber"),

            profile_photo=request.FILES.get('profile_photo'),

            gst_certificate=request.FILES.get('gst_certificate'),
            incorporation_certificate=request.FILES.get('incorporation_certificate'),
            partnership_deed=request.FILES.get('partnership_deed'),
            trademark_certificate=request.FILES.get('trademark_certificate'),
            brand_authorization_letter=request.FILES.get('pan_image'),
            business_license=request.FILES.get('business_license'),


            llp_agreement=request.FILES.get('llp_agreement'),
            moa_document=request.FILES.get('moa_document'),
            aoa_document=request.FILES.get('gst_certificate'),
            udyam_registration=request.FILES.get('udyam_registration'),
            shop_establishment_license=request.FILES.get('shop_establishment_license'),

            

            terms_accepted=True if request.POST.get("terms_accepted") else False,
            privacy_policy_accepted=True if request.POST.get("privacy_policy_accepted") else False,
            return_policy_accepted=True if request.POST.get("return_policy_accepted") else False,
            commission_agreement_accepted=True if request.POST.get("commission_agreement_accepted") else False,

            
        )

        messages.success(request, "Registration submitted successfully! Admin approval required.")
        return redirect('seller_login')

    return render(request, 'saller/seller_register.html')
























from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import transaction
from django.views.decorators.cache import never_cache

from .models import SellerProfile

MAX_IMAGE_SIZE = 5 * 1024 * 1024       # 5 MB
MAX_PDF_SIZE = 10 * 1024 * 1024        # 10 MB


def validate_registration_file(uploaded_file, field_name="document"):

    if not uploaded_file:
        return None


    filename = uploaded_file.name.lower()

    allowed_extensions = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
    }

    extension = None

    for ext in allowed_extensions:
        if filename.endswith(ext):
            extension = ext
            break


    if extension is None:

        raise ValueError(
            f"{field_name}: Only PDF, JPG, JPEG or PNG files are allowed."
        )

    if extension == ".pdf":

        if uploaded_file.size > MAX_PDF_SIZE:

            raise ValueError(
                f"{field_name}: PDF file must be 10 MB or smaller."
            )

    else:

        if uploaded_file.size > MAX_IMAGE_SIZE:

            raise ValueError(
                f"{field_name}: Image must be 5 MB or smaller."
            )


    uploaded_file.seek(0)

    header = uploaded_file.read(16)

    uploaded_file.seek(0)

    if extension == ".pdf":

        if not header.startswith(b"%PDF"):

            raise ValueError(
                f"{field_name}: Invalid PDF file."
            )

    else:

        valid_image = False


        # JPEG
        if header.startswith(b"\xff\xd8\xff"):
            valid_image = True


        # PNG
        elif header.startswith(b"\x89PNG\r\n\x1a\n"):
            valid_image = True


        if not valid_image:

            raise ValueError(
                f"{field_name}: Invalid image file."
            )


    return uploaded_file

@never_cache
def seller_register_step1(request):

    # =====================================================
    # PREVENT REOPENING COMPLETED STEP 1
    # =====================================================

    if request.session.get("seller_step1_completed"):

        seller_id = request.session.get("seller_id")

        if seller_id:

            return redirect(
                "seller_register_step2",
                seller_id=seller_id
            )

        request.session.pop(
            "seller_step1_completed",
            None
        )

        request.session.pop(
            "seller_id",
            None
        )

    if request.method == "POST":

        try:

            business_type = (
                request.POST.get(
                    "business_type",
                    ""
                ).strip().lower()
            )


            allowed_business_types = {
                "individual",
                "proprietorship",
                "partnership",
                "llp",
                "private_limited",
                "opc",
            }


            if business_type not in allowed_business_types:

                raise ValueError(
                    "Please select a valid Business Type."
                )


            terms_accepted = (
                request.POST.get("terms_accepted") == "1"
            )

            privacy_policy_accepted = (
                request.POST.get(
                    "privacy_policy_accepted"
                ) == "1"
            )

            return_policy_accepted = (
                request.POST.get(
                    "return_policy_accepted"
                ) == "1"
            )

            commission_agreement_accepted = (
                request.POST.get(
                    "commission_agreement_accepted"
                ) == "1"
            )

            if not terms_accepted:

                raise ValueError(
                    "You must accept the Terms & Conditions."
                )


            if not privacy_policy_accepted:

                raise ValueError(
                    "You must accept the Privacy Policy."
                )


            if not return_policy_accepted:

                raise ValueError(
                    "You must accept the Return Policy."
                )


            if not commission_agreement_accepted:

                raise ValueError(
                    "You must accept the Seller Agreement."
                )


            profile_photo = request.FILES.get(
                "profile_photo"
            )

            gst_certificate = request.FILES.get(
                "gst_certificate"
            )

            incorporation_certificate = request.FILES.get(
                "incorporation_certificate"
            )

            partnership_deed = request.FILES.get(
                "partnership_deed"
            )

            trademark_certificate = request.FILES.get(
                "trademark_certificate"
            )

            pan_image = request.FILES.get(
                "pan_image"
            )

            business_license = request.FILES.get(
                "business_license"
            )

            llp_agreement = request.FILES.get(
                "llp_agreement"
            )

            moa_document = request.FILES.get(
                "moa_document"
            )

            aoa_document = request.FILES.get(
                "aoa_document"
            )

            udyam_registration = request.FILES.get(
                "udyam_registration"
            )

            shop_establishment_license = request.FILES.get(
                "shop_establishment_license"
            )

            if profile_photo:

                validate_registration_file(
                    profile_photo,
                    "Profile Photo"
                )

            files_to_validate = [

                (
                    gst_certificate,
                    "GST Certificate"
                ),

                (
                    incorporation_certificate,
                    "Incorporation Certificate"
                ),

                (
                    partnership_deed,
                    "Partnership Deed"
                ),

                (
                    trademark_certificate,
                    "Trademark Certificate"
                ),

                (
                    pan_image,
                    "PAN Image"
                ),

                (
                    business_license,
                    "Business License"
                ),

                (
                    llp_agreement,
                    "LLP Agreement"
                ),

                (
                    moa_document,
                    "MOA Document"
                ),

                (
                    aoa_document,
                    "AOA Document"
                ),

                (
                    udyam_registration,
                    "Udyam Registration"
                ),

                (
                    shop_establishment_license,
                    "Shop Establishment License"
                ),
            ]


            for uploaded_file, field_name in files_to_validate:

                if uploaded_file:

                    validate_registration_file(
                        uploaded_file,
                        field_name
                    )

            with transaction.atomic():

               
                user = User.objects.create_user(

                    username=request.POST.get(
                        "username"
                    ),

                    email=request.POST.get(
                        "email"
                    ),

                    password=request.POST.get(
                        "password"
                    )
                )


              
                seller = SellerProfile.objects.create(

                    user=user,

                    business_type=business_type,

                    wedding_anniversary=(
                        request.POST.get(
                            "wedding_anniversary"
                        )
                    ),

                    date_of_birth=(
                        request.POST.get(
                            "date_of_birth"
                        )
                    ),

                    gender=(
                        request.POST.get(
                            "gender"
                        )
                    ),

                    email=(
                        request.POST.get(
                            "email"
                        )
                    ),

                    company_name=(
                        request.POST.get(
                            "company_name"
                        )
                    ),

                    mobile_number=(
                        request.POST.get(
                            "mobile"
                        )
                    ),

                    address=(
                        request.POST.get(
                            "address"
                        )
                    ),

                    state=(
                        request.POST.get(
                            "state"
                        )
                    ),

                    city=(
                        request.POST.get(
                            "city"
                        )
                    ),

                    pincode=(
                        request.POST.get(
                            "pincode"
                        )
                    ),

                    country=(
                        request.POST.get(
                            "country"
                        )
                    ),
                    profile_photo=profile_photo,

                    gst_certificate=gst_certificate,

                    incorporation_certificate=(
                        incorporation_certificate
                    ),

                    partnership_deed=(
                        partnership_deed
                    ),

                    trademark_certificate=(
                        trademark_certificate
                    ),

                    brand_authorization_letter=(
                        pan_image
                    ),

                    business_license=(
                        business_license
                    ),

                    llp_agreement=(
                        llp_agreement
                    ),

                    moa_document=(
                        moa_document
                    ),

                    aoa_document=(
                        aoa_document
                    ),

                    udyam_registration=(
                        udyam_registration
                    ),

                    shop_establishment_license=(
                        shop_establishment_license
                    ),

                    terms_accepted=(
                        terms_accepted
                    ),

                    privacy_policy_accepted=(
                        privacy_policy_accepted
                    ),

                    return_policy_accepted=(
                        return_policy_accepted
                    ),

                    commission_agreement_accepted=(
                        commission_agreement_accepted
                    ),
                )
                request.session[
                    "seller_step1_completed"
                ] = True

                request.session[
                    "seller_id"
                ] = seller.id

                request.session.modified = True

                return redirect(
                    "seller_register_step2",
                    seller_id=seller.id
                )


        except Exception as e:

            print(
                "Seller Registration Error:",
                e
            )


            return render(
                request,
                "saller/step1.html",
                {
                    "step": 1,
                    "error": str(e)
                }
            )

    response = render(
        request,
        "saller/step1.html",
        {
            "step": 1
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0, private"
    )

    response["Pragma"] = "no-cache"

    response["Expires"] = "0"


    return response







from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from .models import SellerProfile

@never_cache
def seller_register_step2(request, seller_id):

    if not request.session.get("seller_step1_completed"):
        return redirect("seller_register_step1")

    session_seller_id = request.session.get("seller_id")

    if not session_seller_id:
        return redirect("seller_register_step1")


    if int(session_seller_id) != int(seller_id):
        return redirect("seller_register_step1")

    seller = get_object_or_404(
        SellerProfile,
        id=seller_id
    )

    if request.session.get("seller_step2_completed"):

        completed_seller_id = request.session.get(
            "seller_step2_seller_id"
        )

        if completed_seller_id == seller_id:

            return redirect(
                "seller_register_step3",
                seller.id
            )

        return redirect("seller_register_step1")

    if request.method == "POST":

        seller.aadhar_number = request.POST.get(
            "aadhar_number"
        )

        seller.pan_number = request.POST.get(
            "pan_number"
        )

        seller.aadhar_image = request.FILES.get(
            "aadhar_image"
        )

        seller.pan_image = request.FILES.get(
            "pan_image"
        )

        seller.gst_certificate = request.FILES.get(
            "gst_certificate"
        )

        seller.save()

        request.session["seller_step2_completed"] = True

        request.session["seller_step2_seller_id"] = seller.id

        request.session.modified = True

        return redirect(
            "seller_register_step3",
            seller.id
        )

    response = render(
        request,
        "saller/step2.html",
        {
            "step": 2,
            "seller": seller
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0, private"
    )

    response["Pragma"] = "no-cache"

    response["Expires"] = "0"


    return response



from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from .models import SellerProfile

@never_cache
def seller_register_step3(request, seller_id):

 
    if not request.session.get("seller_step2_completed"):
        return redirect("seller_register_step2", seller_id=seller_id)

    session_seller_id = request.session.get("seller_id")

    if not session_seller_id:
        return redirect("seller_register_step1")


    if int(session_seller_id) != int(seller_id):
        return redirect("seller_register_step1")

    seller = get_object_or_404(
        SellerProfile,
        id=seller_id
    )

    if request.session.get("seller_step3_completed"):

        completed_seller_id = request.session.get(
            "seller_step3_seller_id"
        )

        if completed_seller_id == seller.id:

            return redirect(
                "registration_complete"
            )

        return redirect("seller_register_step1")

    if request.method == "POST":

        liveface_scan = request.FILES.get(
            "liveface_scan"
        )

        if liveface_scan:
            seller.liveface_scan = liveface_scan

        seller.latitude = (
            request.POST.get("latitude")
            or None
        )

        seller.longitude = (
            request.POST.get("longitude")
            or None
        )

        seller.live_location = (
            request.POST.get(
                "live_location",
                ""
            ).strip()
        )

        seller.save()

        request.session["seller_step3_completed"] = True

        request.session["seller_step3_seller_id"] = seller.id

        request.session.modified = True

        return redirect(
            "registration_complete"
        )

    response = render(
        request,
        "saller/step3.html",
        {
            "step": 3,
            "seller": seller
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0, private"
    )

    response["Pragma"] = "no-cache"

    response["Expires"] = "0"


    return response

# STEP 4
def registration_completex(request):
    return render(request, "saller/step4.html", {"step": 4})


from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def registration_complete(request):

    request.session.pop("seller_step1_completed", None)
    request.session.pop("seller_step2_completed", None)
    request.session.pop("seller_step2_seller_id", None)
    request.session.pop("seller_step3_completed", None)
    request.session.pop("seller_step3_seller_id", None)
    request.session.pop("seller_id", None)

    request.session.modified = True

    response = render(
        request,
        "saller/step4.html",
        {
            "step": 4
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0, private"
    )

    response["Pragma"] = "no-cache"
    response["Expires"] = "0"


    return response












from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import SellerProfile

@never_cache
def seller_register(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        company_name = request.POST.get('company_name').strip()
        mobile = request.POST.get('mobile').strip()
        address = request.POST.get('address').strip()
        state = request.POST.get('state').strip()
        city = request.POST.get('city').strip()
        pincode = request.POST.get('pincode').strip()
        country = request.POST.get('country').strip()
        aadhar = request.POST.get('aadhar').strip()
        pan = request.POST.get('pan').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('seller_register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('seller_register')

        if SellerProfile.objects.filter(mobile_number=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return redirect('seller_register')

        if SellerProfile.objects.filter(aadhar_number=aadhar).exists():
            messages.error(request, "Aadhar number already registered.")
            return redirect('seller_register')

        if SellerProfile.objects.filter(pan_number=pan).exists():
            messages.error(request, "PAN number already registered.")
            return redirect('seller_register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        SellerProfile.objects.create(
            user=user,
            email=email,
            company_name=company_name,
            mobile_number=mobile,
            address=address,
            state=state,
            city=city,
            pincode=pincode,
            country=country,
            aadhar_number=aadhar,
            aadhar_image=request.FILES.get('aadhar_image'),
            pan_number=pan,
            pan_image=request.FILES.get('pan_image'),
            gstinnamber=request.POST.get("gstinnamber"),
            profile_photo=request.FILES.get('profile_photo'),
            gst_certificate=request.FILES.get('gst_certificate'),
            incorporation_certificate=request.FILES.get('incorporation_certificate'),
            partnership_deed=request.FILES.get('partnership_deed'),
            trademark_certificate=request.FILES.get('trademark_certificate'),
            brand_authorization_letter=request.FILES.get('pan_image'),
            business_license=request.FILES.get('business_license'),
            llp_agreement=request.FILES.get('llp_agreement'),
            moa_document=request.FILES.get('moa_document'),
            aoa_document=request.FILES.get('gst_certificate'),
            udyam_registration=request.FILES.get('udyam_registration'),
            shop_establishment_license=request.FILES.get('shop_establishment_license'),
            terms_accepted=True if request.POST.get("terms_accepted") else False,
            privacy_policy_accepted=True if request.POST.get("privacy_policy_accepted") else False,
            return_policy_accepted=True if request.POST.get("return_policy_accepted") else False,
            commission_agreement_accepted=True if request.POST.get("commission_agreement_accepted") else False,
        )

        messages.success(request, "Registration submitted successfully! Admin approval required.")
        return redirect('seller_login')

    return render(request, 'saller/seller_register.html')









from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import SellerProfile
import random
def seller_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            try:
                seller = SellerProfile.objects.get(user=user)
            except SellerProfile.DoesNotExist:
                messages.error(request, "You are not registered as a seller.")
                return redirect('seller_login')

            if seller.is_locked:
                messages.error(request, "Your account is locked. Contact admin.")
                return redirect('seller_login')

            if seller.status == 'approved':
                seller.login_attempts = 0
                seller.save()
                login(request, user)
                return redirect('seller_dashboard')
            elif seller.status == 'pending':
                messages.error(request, "Your account is pending approval.")
            elif seller.status == 'rejected':
                messages.error(request, "Your account registration was rejected.")
            elif seller.status == 'blocked':
                messages.error(request, "Your account is blocked. Contact admin.")

        else:
            try:
                seller = SellerProfile.objects.get(user__username=username)
                seller.login_attempts += 1
                if seller.login_attempts >= 3:
                    seller.is_locked = True
                    messages.error(request, "Account locked after 3 failed attempts. Contact admin.")
                else:
                    messages.error(request, "Invalid username or password.")
                seller.save()
            except SellerProfile.DoesNotExist:
                messages.error(request, "Invalid username or password.")

    return render(request, 'saller/seller_login.html')






from django.shortcuts import render, redirect
from django.contrib import messages
#from .models import SellerProfile
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SellerProfile

def unlock_username(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()

        if not username:
            messages.error(request, "Please enter username.")
            return render(request, 'unlock_username.html')

        try:
            seller = SellerProfile.objects.get(user__username=username)

            # ✅ Check seller status
            if seller.status != 'approved':
                messages.error(request, "Seller account is not approved.")
                return render(request, 'unlock_username.html')

            # ✅ Check if account is locked
            if seller.is_locked:
                request.session['unlock_user'] = username
                messages.success(request, "Account is locked. Please answer security questions.")
                return redirect('seller_unlock_questions')
            else:
                messages.info(request, "Your account is already unlocked.")

        except SellerProfile.DoesNotExist:
            messages.error(request, "Seller account not found.")

    return render(request, 'saller/unlock_username.html')



import random
from django.shortcuts import render, redirect
from django.contrib import messages


MAX_ATTEMPTS = 5

def seller_unlock_questionsx(request):
    username = request.session.get('unlock_user')

    if not username:
        return redirect('seller_unlock_username')

    try:
        seller = SellerProfile.objects.get(user__username=username)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Seller not found.")
        return redirect('seller_unlock_username')

    # Initialize attempt counter
    if 'unlock_attempts' not in request.session:
        request.session['unlock_attempts'] = 0

    # If attempts exceeded
    if request.session['unlock_attempts'] >= MAX_ATTEMPTS:
        messages.error(request, "Maximum attempts exceeded. Please contact admin to unlock your account.")
        return render(request, 'unlock_questions.html', {
            'username': username,
            'captcha': None,
            'blocked': True
        })

    # Generate CAPTCHA
    if 'captcha' not in request.session:
        request.session['captcha'] = random.randint(1000, 9999)

    if request.method == "POST":
        wedding = request.POST.get('wedding')
        dob = request.POST.get('dob')
        captcha_input = request.POST.get('captcha')

        # Validate CAPTCHA
        if str(request.session['captcha']) != captcha_input:
            request.session['unlock_attempts'] += 1
            remaining = MAX_ATTEMPTS - request.session['unlock_attempts']
            messages.error(request, f"Invalid CAPTCHA. {remaining} attempts remaining.")
            request.session['captcha'] = random.randint(1000, 9999)
            return redirect('seller_unlock_questions')

        # First Time Save
        if not seller.wedding_anniversary and not seller.date_of_birth:
            seller.wedding_anniversary = wedding
            seller.date_of_birth = dob
            seller.save()
        else:
            # Validate Answers
            if str(seller.wedding_anniversary) != wedding or str(seller.date_of_birth) != dob:
                request.session['unlock_attempts'] += 1
                remaining = MAX_ATTEMPTS - request.session['unlock_attempts']
                messages.error(request, f"Incorrect answers. {remaining} attempts remaining.")
                return redirect('seller_unlock_questions')

        # Success → Reset attempts
        request.session.pop('unlock_attempts', None)
        request.session.pop('captcha', None)

        return redirect('seller_unlock_confirm')

    context = {
        'username': username,
        'captcha': request.session.get('captcha'),
        'remaining': MAX_ATTEMPTS - request.session['unlock_attempts'],
        'blocked': False
    }

    return render(request, 'saller/unlock_questions.html', context)







import hashlib
import secrets

from datetime import timedelta


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import SellerProfile, SellerPasswordResetToken
from .forms import (
    SellerForgotPasswordForm,
    SellerResetPasswordForm,
)


@never_cache
def seller_forgot_password(request):

    if request.method == "POST":

        form = SellerForgotPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"].strip().lower()

            seller = (
                SellerProfile.objects
                .select_related("user")
                .filter(email__iexact=email)
                .first()
            )

            if not seller:

                seller = (
                    SellerProfile.objects
                    .select_related("user")
                    .filter(user__email__iexact=email)
                    .first()
                )

            if not seller:

                messages.error(
                    request,
                    "This email address is not registered with a ShopKart Seller account."
                )

                return redirect(
                    "seller_forgot_password"
                )

            SellerPasswordResetToken.objects.filter(
                seller=seller,
                used=False
            ).update(
                used=True,
                used_at=timezone.now()
            )

            raw_token = secrets.token_urlsafe(64)

            token_hash = hashlib.sha512(
                raw_token.encode("utf-8")
            ).hexdigest()

            expires_at = (
                timezone.now()
                + timedelta(minutes=15)
            )

            SellerPasswordResetToken.objects.create(
                seller=seller,
                token_hash=token_hash,
                expires_at=expires_at,
                used=False
            )

            site_url = getattr(
                settings,
                "SITE_URL",
                "http://127.0.0.1:8000"
            ).rstrip("/")

            reset_url = (
                f"{site_url}"
                f"/seller/password-reset/"
                f"{raw_token}/"
            )

            username = seller.user.username

            subject = "ShopKart Seller Password Reset"

            text_message = f"""
Hello {username},

We received a request to reset your ShopKart Seller account password.

Click the link below to create a new password:

{reset_url}

This link:

- Expires in 15 minutes
- Can be used only once
- Becomes invalid after your password is changed
- Cannot be reused

If you did not request this password reset, please ignore this email.

Regards,
ShopKart Seller Security Team
"""

            html_message = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>ShopKart Password Reset</title>

</head>

<body style="
    margin:0;
    padding:0;
    background:#f4f7fb;
    font-family:Arial,Helvetica,sans-serif;
">

<div style="
    max-width:620px;
    margin:40px auto;
    background:#ffffff;
    border-radius:16px;
    overflow:hidden;
    box-shadow:0 10px 35px rgba(0,0,0,.08);
">

    <div style="
        background:#2563eb;
        color:#ffffff;
        padding:28px;
        text-align:center;
    ">

        <h1 style="margin:0;">
            ShopKart
        </h1>

        <p style="margin:8px 0 0;">
            Seller Account Security
        </p>

    </div>

    <div style="
        padding:35px;
        color:#1f2937;
    ">

        <h2>
            Password Reset Request
        </h2>

        <p>
            Hello <strong>{username}</strong>,
        </p>

        <p>
            We received a request to reset your
            ShopKart Seller account password.
        </p>

        <div style="
            text-align:center;
            margin:30px 0;
        ">

            <a
                href="{reset_url}"
                style="
                    display:inline-block;
                    padding:14px 28px;
                    background:#2563eb;
                    color:#ffffff;
                    text-decoration:none;
                    border-radius:10px;
                    font-weight:bold;
                "
            >
                Reset Password
            </a>

        </div>

        <div style="
            background:#f8fafc;
            border-left:4px solid #2563eb;
            padding:16px;
            border-radius:8px;
        ">

            <strong>Security information</strong>

            <ul>

                <li>
                    Link expires in 15 minutes.
                </li>

                <li>
                    Link can be used only once.
                </li>

                <li>
                    Link becomes invalid after password change.
                </li>

                <li>
                    Do not share this link.
                </li>

            </ul>

        </div>

        <p style="
            margin-top:25px;
            color:#64748b;
            font-size:14px;
        ">

            If you did not request this password reset,
            you can safely ignore this email.

        </p>

    </div>

    <div style="
        padding:20px;
        text-align:center;
        background:#f8fafc;
        color:#64748b;
        font-size:13px;
    ">

        ShopKart Seller Security Team

    </div>

</div>

</body>

</html>
"""

            # =====================================================
            # SEND EMAIL
            # =====================================================

            try:

                email_message = EmailMultiAlternatives(
                    subject=subject,
                    body=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )

                email_message.attach_alternative(
                    html_message,
                    "text/html"
                )

                email_message.send(
                    fail_silently=False
                )

            except Exception:

                messages.error(
                    request,
                    "Unable to send the reset email. Please try again later."
                )

                return redirect(
                    "seller_forgot_password"
                )

            # =====================================================
            # SUCCESS
            # =====================================================

            messages.success(
                request,
                "Your email is registered. A password reset link has been sent to your email."
            )

            return redirect(
                "seller_forgot_password"
            )

    else:

        form = SellerForgotPasswordForm()

    response = render(
        request,
        "saller/seller_forgot_password.html",
        {
            "form": form
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )

    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response

@never_cache
def seller_password_reset(request, token):

    if not token or len(token) < 50:

        return render(
            request,
            "saller/password_reset_invalid.html",
            status=400
        )

    token_hash = hashlib.sha512(
        token.encode("utf-8")
    ).hexdigest()

    reset_token = (
        SellerPasswordResetToken.objects
        .select_related(
            "seller",
            "seller__user"
        )
        .filter(
            token_hash=token_hash
        )
        .first()
    )

    if not reset_token:

        return render(
            request,
            "saller/password_reset_invalid.html",
            status=404
        )

    if reset_token.used:

        return render(
            request,
            "saller/password_reset_invalid.html",
            {
                "reason": "used"
            },
            status=410
        )

    if timezone.now() >= reset_token.expires_at:

        reset_token.used = True
        reset_token.used_at = timezone.now()

        reset_token.save(
            update_fields=[
                "used",
                "used_at"
            ]
        )

        return render(
            request,
            "saller/password_reset_invalid.html",
            {
                "reason": "expired"
            },
            status=410
        )

    if request.method == "POST":

        form = SellerResetPasswordForm(
            request.POST
        )

        if form.is_valid():

            new_password = form.cleaned_data[
                "new_password"
            ]

            with transaction.atomic():

                current_token = (
                    SellerPasswordResetToken.objects
                    .select_for_update()
                    .select_related(
                        "seller",
                        "seller__user"
                    )
                    .filter(
                        id=reset_token.id
                    )
                    .first()
                )

                if not current_token:

                    return render(
                        request,
                        "saller/password_reset_invalid.html",
                        status=404
                    )

                if current_token.used:

                    return render(
                        request,
                        "saller/password_reset_invalid.html",
                        {
                            "reason": "used"
                        },
                        status=410
                    )

                if timezone.now() >= current_token.expires_at:

                    current_token.used = True
                    current_token.used_at = timezone.now()

                    current_token.save(
                        update_fields=[
                            "used",
                            "used_at"
                        ]
                    )

                    return render(
                        request,
                        "saller/password_reset_invalid.html",
                        {
                            "reason": "expired"
                        },
                        status=410
                    )

                seller = current_token.seller
                user = seller.user

                user.set_password(
                    new_password
                )

                user.save(
                    update_fields=[
                        "password"
                    ]
                )

                current_token.mark_used()

                SellerPasswordResetToken.objects.filter(
                    seller=seller,
                    used=False
                ).exclude(
                    id=current_token.id
                ).update(
                    used=True,
                    used_at=timezone.now()
                )

            return render(
                request,
                "saller/password_reset_success.html"
            )

    else:

        form = SellerResetPasswordForm()

    response = render(
        request,
        "saller/seller_password_reset.html",
        {
            "form": form,
            "expires_at": reset_token.expires_at,
        }
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response












import random

from django.shortcuts import render, redirect
from django.contrib import messages

from .models import SellerProfile


MAX_ATTEMPTS = 5

import random

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator

from .models import SellerProfile


MAX_ATTEMPTS = 5


def generate_unlock_captcha(request):
    """
    Generate a new 4-digit CAPTCHA.
    """
    request.session['captcha'] = random.randint(1000, 9999)
    request.session.modified = True


# =========================================================
# SELLER UNLOCK QUESTIONS
# =========================================================

@never_cache
@require_http_methods(["GET", "POST"])
def seller_unlock_questions(request):

    username = request.session.get('unlock_user')

    if not username:
        messages.error(
            request,
            "Access denied. Please start the unlock process again."
        )
        return redirect('seller_unlock_username')

    try:
        seller = SellerProfile.objects.get(
            user__username=username
        )

    except SellerProfile.DoesNotExist:
        request.session.flush()

        messages.error(
            request,
            "Seller not found."
        )

        return redirect('seller_unlock_username')

    if not seller.is_locked:

        request.session.pop('unlock_user', None)
        request.session.pop('captcha', None)
        request.session.pop('unlock_attempts', None)

        messages.info(
            request,
            "Account is already unlocked."
        )

        return redirect('seller_login')

    attempts = request.session.get(
        'unlock_attempts',
        0
    )

    if attempts >= MAX_ATTEMPTS:

        request.session.pop(
            'captcha',
            None
        )

        return render(
            request,
            'saller/unlock_questions.html',
            {
                'username': username,
                'blocked': True,
                'captcha': None,
                'remaining': 0,
            }
        )

    if 'captcha' not in request.session:
        generate_unlock_captcha(request)


    if request.method == "POST":

        wedding = request.POST.get(
            'wedding',
            ''
        ).strip()

        dob = request.POST.get(
            'dob',
            ''
        ).strip()

        captcha_input = request.POST.get(
            'captcha',
            ''
        ).strip()

        session_captcha = str(
            request.session.get(
                'captcha',
                ''
            )
        )


        if captcha_input != session_captcha:

            attempts += 1

            request.session['unlock_attempts'] = attempts

            # Destroy old CAPTCHA
            request.session.pop(
                'captcha',
                None
            )

            if attempts < MAX_ATTEMPTS:
                generate_unlock_captcha(request)

            remaining = MAX_ATTEMPTS - attempts

            if remaining > 0:

                messages.error(
                    request,
                    f"Invalid CAPTCHA. "
                    f"{remaining} attempts remaining."
                )

            else:

                messages.error(
                    request,
                    "Maximum attempts reached. "
                    "Account unlock is blocked."
                )

            return redirect(
                'seller_unlock_questions'
            )

        request.session.pop(
            'captcha',
            None
        )

        if (
            not seller.wedding_anniversary
            and not seller.date_of_birth
        ):

            seller.wedding_anniversary = wedding
            seller.date_of_birth = dob

            seller.save()

        else:

            stored_wedding = str(
                seller.wedding_anniversary
            )

            stored_dob = str(
                seller.date_of_birth
            )

            if (
                stored_wedding != wedding
                or
                stored_dob != dob
            ):

                attempts += 1

                request.session['unlock_attempts'] = attempts

                # Generate NEW CAPTCHA
                if attempts < MAX_ATTEMPTS:
                    generate_unlock_captcha(request)

                remaining = MAX_ATTEMPTS - attempts

                if remaining > 0:

                    messages.error(
                        request,
                        f"Incorrect answers. "
                        f"{remaining} attempts remaining."
                    )

                else:

                    messages.error(
                        request,
                        "Maximum attempts reached. "
                        "Account unlock is blocked."
                    )

                return redirect(
                    'seller_unlock_questions'
                )

        request.session.pop(
            'unlock_attempts',
            None
        )

        request.session.pop(
            'captcha',
            None
        )

        return redirect(
            'seller_unlock_confirm'
        )

    context = {
        'username': username,
        'captcha': request.session.get('captcha'),
        'remaining': MAX_ATTEMPTS - attempts,
        'blocked': False,
    }

    return render(
        request,
        'saller/unlock_questions.html',
        context
    )


@never_cache
@require_http_methods(["GET", "POST"])
def seller_unlock_confirm(request):

    username = request.session.get(
        'unlock_user'
    )

    if not username:

        messages.error(
            request,
            "Access denied. Unlock session expired."
        )

        return redirect(
            'seller_unlock_username'
        )

    try:

        seller = SellerProfile.objects.get(
            user__username=username
        )

    except SellerProfile.DoesNotExist:

        request.session.flush()

        messages.error(
            request,
            "Seller not found."
        )

        return redirect(
            'seller_unlock_username'
        )

    if not seller.is_locked:

        request.session.pop(
            'unlock_user',
            None
        )

        request.session.pop(
            'captcha',
            None
        )

        request.session.pop(
            'unlock_attempts',
            None
        )

        messages.info(
            request,
            "Account is already unlocked."
        )

        return redirect(
            'seller_login'
        )

    if request.method == "POST":

        seller.is_locked = False
        seller.login_attempts = 0

        seller.save()

        request.session.pop(
            'unlock_user',
            None
        )

        request.session.pop(
            'captcha',
            None
        )

        request.session.pop(
            'unlock_attempts',
            None
        )

        messages.success(
            request,
            "Account successfully unlocked."
        )

        return redirect(
            'seller_login'
        )

    return render(
        request,
        'saller/unlock_confirm.html',
        {
            'username': username
        }
    )


from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache

@never_cache
def seller_unlock_confirm(request):
    username = request.session.get('unlock_user')

    if not username:
        return redirect('seller_unlock_username')

    try:
        seller = SellerProfile.objects.get(user__username=username)
    except SellerProfile.DoesNotExist:
        return redirect('seller_unlock_username')

    if not seller.is_locked:
        messages.info(request, "Account is already unlocked.")
        return redirect('seller_login')

    if request.method == "POST":
        seller.is_locked = False
        seller.login_attempts = 0
        seller.save()

        # Clear unlock session safely
        request.session.pop('unlock_user', None)
        request.session.pop('captcha', None)
        request.session.pop('unlock_attempts', None)

        messages.success(request, "Account successfully unlocked.")
        return redirect('seller_login')

    return render(request, 'saller/unlock_confirm.html', {'username': username})



from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

@login_required
def seller_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('seller_login')



from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import (
    F,
    Sum,
    DecimalField,
    ExpressionWrapper,
    Value,
)
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from .models import (
    SellerProfile,
    Product,
    Placedorderxx,
    CustomerRegistration,
    SellerLoginHistory,
)




@login_required
def seller_dashboard(request):

    user = request.user

    seller = SellerProfile.objects.get(user=user)

    seller_username = user.username

    products = Product.objects.filter(
        vendor=seller_username
    )

    total_products = products.count()

    orders = (
        Placedorderxx.objects
        .filter(
            product__vendor=seller_username
        )
        .select_related(
            "user",
            "product"
        )
        .order_by("-id")
    )

    total_orders = orders.count()

    revenue_expression = ExpressionWrapper(
        (
            F("quantity") * F("product__selling_price")
        )
        - Coalesce(
            F("coupon_discount"),
            Value(0.0)
        ),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2
        )
    )

    total_revenue = (
        orders
        .filter(
            status__in=[
                "Delivered",
                "Completed",
                "delivered",
                "completed"
            ]
        )
        .aggregate(
            total=Sum(revenue_expression)
        )["total"] or 0
    )
    if total_revenue < 0:
        total_revenue = 0


    paginator = Paginator(
        orders,
        3
    )

    page_number = request.GET.get("page")

    recent_orders = paginator.get_page(
        page_number
    )

    new_order_time = date.today() - timedelta(
        days=2
    )

    for order in recent_orders:
        product_price = order.product.selling_price or 0

        quantity = order.quantity or 0

        coupon_discount = order.coupon_discount or 0


        gross_amount = (
            quantity * product_price
        )

        net_amount = (
            gross_amount - coupon_discount
        )

        if net_amount < 0:
            net_amount = 0

        order.gross_amount = gross_amount
        order.coupon_discount_amount = coupon_discount
        order.total = int(net_amount)

        order.is_new = (
            order.created_at.date() >= new_order_time
        )

    customers = (
        CustomerRegistration.objects
        .filter(
            user__placedorderxx__product__vendor=seller_username
        )
        .distinct()
    )

    total_customers = customers.count()

    history = (
        SellerLoginHistory.objects
        .filter(
            seller=user
        )
        .order_by(
            "-login_time"
        )
        .first()
    )

    login_time = None
    logout_time = None
    last_login = user.last_login
    spent_hours = ""

    if history:

        login_time = history.login_time

        logout_time = history.logout_time

        if logout_time:

            spent = (
                logout_time - login_time
            )

        else:

            spent = (
                timezone.now() - login_time
            )

        total_seconds = int(
            spent.total_seconds()
        )

        hours = total_seconds // 3600

        minutes = (
            total_seconds % 3600
        ) // 60

        spent_hours = (
            f"{hours} Hour {minutes} Minute"
        )

    context = {

        # Seller
        "seller": seller,

        # Products
        "products": products,

        # Orders
        "recent_orders": recent_orders,
        "orders": orders,

        # Counts
        "total_products": total_products,
        "total_orders": total_orders,
        "total_customers": total_customers,

        # Revenue AFTER coupon discount
        "total_revenue": total_revenue,

        # Date
        "today": date.today(),

        # Login history
        "login_time": login_time,
        "logout_time": logout_time,
        "last_login": last_login,
        "spent_hours": spent_hours,
    }

    return render(
        request,
        "saller/seller_dashboard.html",
        context
    )





from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Product, Catagory


@login_required
def saller_product_add(request):
    categories = Catagory.objects.all()

    if request.method == "POST":

        quantity = request.POST.get("quantity") or 0
        original_price = request.POST.get("original_price") or 0
        selling_price = request.POST.get("selling_price") or 0

        price_s = request.POST.get("price_s") or 0
        price_m = request.POST.get("price_m") or 0
        price_l = request.POST.get("price_l") or 0
        price_xl = request.POST.get("price_xl") or 0
        price_xxl = request.POST.get("price_xxl") or 0

        coupon_discount = request.POST.get("coupon_discount") or 0

        category = request.POST.get("category")
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        size = request.POST.get("size", "").strip()
        coupon_code = request.POST.get("coupon_code", "").strip()

        Product.objects.create(
            vendor=request.user.username,

            category_id=category,

            name=name,
            quantity=quantity,

            original_price=original_price,
            selling_price=selling_price,

            description=description,
            size=size,

            price_s=price_s,
            price_m=price_m,
            price_l=price_l,
            price_xl=price_xl,
            price_xxl=price_xxl,

            coupon_code=coupon_code,
            coupon_discount=coupon_discount,

            product_image=request.FILES.get("product_image"),
            product_image2=request.FILES.get("product_image2"),
            product_image3=request.FILES.get("product_image3"),
            product_image4=request.FILES.get("product_image4"),
        )

        return redirect("saller_product_list")

    return render(
        request,
        "saller/saller_product_form.html",
        {
            "categories": categories
        }
    )




@login_required
def saller_product_list(request):
    products = Product.objects.filter(vendor=request.user)

    return render(request, "saller/saller_product_list.html", {
        "products": products
    })








from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, id=pk, vendor=request.user.username)

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.quantity = request.POST.get('quantity')
        product.original_price = request.POST.get('original_price')
        product.selling_price = request.POST.get('selling_price')
        product.description = request.POST.get('description')

        if 'product_image' in request.FILES:
            product.product_image = request.FILES['product_image']

        product.save()
        return redirect('saller_product_list')

    return render(request, "saller/edit_product.html", {"product": product})




@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk, vendor=request.user.username)

    is_ordered = Placedorderxx.objects.filter(product=product).exists()

    if request.method == "POST":
        if is_ordered:
            messages.error(request, "This product cannot be deleted (already ordered).")
            return redirect('saller_product_list')

        reason = request.POST.get("delete_reason")

        # Optional: save reason somewhere (log model or print)
        print(f"Deleted Product: {product.name}, Reason: {reason}")

        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('saller_product_list')

    return render(request, "saller/delete_product.html", {
        "product": product,
        "is_ordered": is_ordered
    })
  
from django.shortcuts import get_object_or_404, redirect
from .models import Placedorderxx

@login_required
def seller_update_order_status(request, order_id):
    order = get_object_or_404(
        Placedorderxx,
        id=order_id,
        product__vendor=request.user.username
    )

    if request.method == "POST":
        order.status = request.POST["status"]
        order.save()

    return redirect("saller_customer_orders")




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Placedorderxx

@login_required
def saller_customer_orders(request):
    # ✅ Filter orders by snapshot vendor field
    orders = Placedorderxx.objects.filter(vendor=request.user.username).select_related("user")

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")

        try:
            order = Placedorderxx.objects.get(id=order_id)

            # ✅ Only allow seller to update their own orders
            if order.vendor != request.user.username:
                return redirect("saller_customer_orders")

        except Placedorderxx.DoesNotExist:
            return redirect("saller_customer_orders")

        # Prevent admin-locked orders
        if order.updated_by_admin:
            return redirect("saller_customer_orders")

        # ✅ Update order status safely
        order.status = status
        order.save()

    return render(request, "saller/saller_customer_orders.html", {"orders": orders})




from datetime import timedelta
from decimal import Decimal

from django.db.models import F, Sum, DecimalField, ExpressionWrapper, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils.timezone import now

from .models import Placedorderxx


def saller_sales_reportx(request):

    today = now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)

    revenue_expression = ExpressionWrapper(
        (
            F('product__selling_price') * F('quantity')
        ) - Coalesce(
            F('coupon_discount'),
            Value(0.0)
        ),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2
        )
    )

    seller_filter = {
        'product__vendor': request.user.username,
        'status': 'completed'
    }

    daily_sales = (
        Placedorderxx.objects
        .filter(
            ordered_date__date=today,
            **seller_filter
        )
        .select_related('product')
    )

    weekly_sales = (
        Placedorderxx.objects
        .filter(
            ordered_date__date__gte=week_ago,
            **seller_filter
        )
        .select_related('product')
    )

    monthly_sales = (
        Placedorderxx.objects
        .filter(
            ordered_date__date__gte=month_ago,
            **seller_filter
        )
        .select_related('product')
    )

    yearly_sales = (
        Placedorderxx.objects
        .filter(
            ordered_date__date__gte=year_ago,
            **seller_filter
        )
        .select_related('product')
    )

    for qs in [
        daily_sales,
        weekly_sales,
        monthly_sales,
        yearly_sales
    ]:

        for order in qs:

            product_price = Decimal(
                str(order.product.selling_price or 0)
            )

            quantity = Decimal(
                str(order.quantity or 0)
            )

            coupon_discount = Decimal(
                str(order.coupon_discount or 0)
            )

            # Gross amount
            gross_amount = product_price * quantity

            # Net amount after coupon discount
            net_amount = gross_amount - coupon_discount

            # Prevent negative revenue
            if net_amount < 0:
                net_amount = Decimal('0.00')

            order.gross_amount = gross_amount
            order.revenue = net_amount

    daily_total_quantity = (
        daily_sales.aggregate(
            total_qty=Sum('quantity')
        )['total_qty'] or 0
    )

    weekly_total_quantity = (
        weekly_sales.aggregate(
            total_qty=Sum('quantity')
        )['total_qty'] or 0
    )

    monthly_total_quantity = (
        monthly_sales.aggregate(
            total_qty=Sum('quantity')
        )['total_qty'] or 0
    )

    yearly_total_quantity = (
        yearly_sales.aggregate(
            total_qty=Sum('quantity')
        )['total_qty'] or 0
    )

    daily_coupon_discount = (
        daily_sales.aggregate(
            total_discount=Sum('coupon_discount')
        )['total_discount'] or 0
    )

    weekly_coupon_discount = (
        weekly_sales.aggregate(
            total_discount=Sum('coupon_discount')
        )['total_discount'] or 0
    )

    monthly_coupon_discount = (
        monthly_sales.aggregate(
            total_discount=Sum('coupon_discount')
        )['total_discount'] or 0
    )

    yearly_coupon_discount = (
        yearly_sales.aggregate(
            total_discount=Sum('coupon_discount')
        )['total_discount'] or 0
    )

    daily_revenue = (
        daily_sales.aggregate(
            total_revenue=Sum(revenue_expression)
        )['total_revenue'] or 0
    )

    weekly_revenue = (
        weekly_sales.aggregate(
            total_revenue=Sum(revenue_expression)
        )['total_revenue'] or 0
    )

    monthly_revenue = (
        monthly_sales.aggregate(
            total_revenue=Sum(revenue_expression)
        )['total_revenue'] or 0
    )

    yearly_revenue = (
        yearly_sales.aggregate(
            total_revenue=Sum(revenue_expression)
        )['total_revenue'] or 0
    )

    daily_revenue = int(daily_revenue)
    weekly_revenue = int(weekly_revenue)
    monthly_revenue = int(monthly_revenue)
    yearly_revenue = int(yearly_revenue)

    context = {

        # Sales
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,

        # Quantity
        'daily_total_quantity': daily_total_quantity,
        'weekly_total_quantity': weekly_total_quantity,
        'monthly_total_quantity': monthly_total_quantity,
        'yearly_total_quantity': yearly_total_quantity,

        # Revenue after coupon discount
        'daily_revenue': daily_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'yearly_revenue': yearly_revenue,

        # Coupon discount
        'daily_coupon_discount': daily_coupon_discount,
        'weekly_coupon_discount': weekly_coupon_discount,
        'monthly_coupon_discount': monthly_coupon_discount,
        'yearly_coupon_discount': yearly_coupon_discount,
    }

    return render(
        request,
        'saller/saller_sales_report.html',
        context
    )


from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from .models import Placedorderxx


ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def money(value):
    """Return a monetary value rounded to two decimal places."""
    return Decimal(str(value or 0)).quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


@login_required
def saller_sales_report(request):
    today = timezone.localdate()

    # Calendar reporting periods.
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    # Completed orders for the logged-in seller only.
    seller_filter = {
        "product__vendor": request.user.username,
        "status__iexact": "completed",
    }

    def get_sales(start_date, end_date):
        return list(
            Placedorderxx.objects.filter(
                **seller_filter,
                ordered_date__date__gte=start_date,
                ordered_date__date__lte=end_date,
            )
            .select_related("product")
            .order_by("-ordered_date")
        )

    # Fetch orders for each period.
    daily_sales = get_sales(today, today)
    weekly_sales = get_sales(week_start, today)
    monthly_sales = get_sales(month_start, today)
    yearly_sales = get_sales(year_start, today)

    def calculate_sales(orders):
        total_quantity = 0
        total_selling_price = ZERO
        total_coupon_discount = ZERO
        total_final_amount = ZERO

        for order in orders:
            quantity = max(int(order.quantity or 0), 0)
            product = order.product

            # Unit selling price and total before discount.
            unit_price = money(product.selling_price)
            selling_price_total = money(unit_price * quantity)

            # First use the discount saved on the order.
            saved_discount = getattr(order, "coupon_discount", None)

            if (
                saved_discount is not None
                and money(saved_discount) > ZERO
            ):
                coupon_discount_total = money(saved_discount)

            else:
                # Fallback to the product coupon discount.
                # Adjust these field names if your Product model
                # uses different names.
                product_discount = money(
                    getattr(product, "coupon_discount", 0)
                )

                coupon_active = getattr(
                    product, "coupon_active", True
                )
                coupon_expiry = getattr(
                    product, "coupon_expiry", None
                )

                coupon_valid = (
                    coupon_active
                    and (
                        coupon_expiry is None
                        or coupon_expiry >= today
                    )
                )

                if coupon_valid:
                    coupon_discount_total = money(
                        product_discount * quantity
                    )
                else:
                    coupon_discount_total = ZERO

            # Keep discount within the selling-price amount.
            coupon_discount_total = min(
                max(coupon_discount_total, ZERO),
                selling_price_total,
            )

            # Final total after discount.
            final_total = money(
                selling_price_total - coupon_discount_total
            )

            # IMPORTANT: names used by your HTML template.
            order.selling_price_unit = unit_price
            order.selling_price_total = selling_price_total
            order.coupon_discount_total = coupon_discount_total

            # Your HTML uses order.total_amount.
            order.total_amount = final_total

            # Keep this alias if another template uses it.
            order.final_total = final_total

            total_quantity += quantity
            total_selling_price += selling_price_total
            total_coupon_discount += coupon_discount_total
            total_final_amount += final_total

        return {
            "total_quantity": total_quantity,
            "selling_price": money(total_selling_price),
            "coupon_discount": money(total_coupon_discount),
            "revenue": money(total_final_amount),
        }

    # Calculate totals for each reporting period.
    daily_totals = calculate_sales(daily_sales)
    weekly_totals = calculate_sales(weekly_sales)
    monthly_totals = calculate_sales(monthly_sales)
    yearly_totals = calculate_sales(yearly_sales)

    context = {
        # Order lists.
        "daily_sales": daily_sales,
        "weekly_sales": weekly_sales,
        "monthly_sales": monthly_sales,
        "yearly_sales": yearly_sales,

        # Quantities.
        "daily_total_quantity": daily_totals["total_quantity"],
        "weekly_total_quantity": weekly_totals["total_quantity"],
        "monthly_total_quantity": monthly_totals["total_quantity"],
        "yearly_total_quantity": yearly_totals["total_quantity"],

        # Selling price before discounts.
        "daily_selling_price": daily_totals["selling_price"],
        "weekly_selling_price": weekly_totals["selling_price"],
        "monthly_selling_price": monthly_totals["selling_price"],
        "yearly_selling_price": yearly_totals["selling_price"],

        # Coupon discounts.
        "daily_coupon_discount": daily_totals["coupon_discount"],
        "weekly_coupon_discount": weekly_totals["coupon_discount"],
        "monthly_coupon_discount": monthly_totals["coupon_discount"],
        "yearly_coupon_discount": yearly_totals["coupon_discount"],

        # Final amount after discounts.
        "daily_revenue": daily_totals["revenue"],
        "weekly_revenue": weekly_totals["revenue"],
        "monthly_revenue": monthly_totals["revenue"],
        "yearly_revenue": yearly_totals["revenue"],

        # IMPORTANT: variable names required by your HTML.
        "daily_total_amount": daily_totals["revenue"],
        "weekly_total_amount": weekly_totals["revenue"],
        "monthly_total_amount": monthly_totals["revenue"],
        "yearly_total_amount": yearly_totals["revenue"],
    }

    return render(
        request,
        "saller/saller_sales_report.html",
        context,
    )


@login_required
def seller_order_status(request):
    seller_name = request.user.username

    orders = Placedorderxx.objects.filter(
        product__vendor=seller_name
    )

    status_counts = orders.values("status").annotate(
        total=Count("status")
    )

    data = {
        "pending": 0,
        "processing": 0,
        "shipped": 0,
        "delivered": 0,
        "completed": 0,
    }

    for item in status_counts:
        status = (item["status"] or "").lower()

        if status in data:
            data[status] = item["total"]

    context = {
        "labels": list(data.keys()),
        "values": list(data.values()),
    }

    return render(
        request,
        "saller/seller_order_status.html",
        context,
    )



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Placedorderxx

@login_required
def seller_top_selling_products(request):
    seller_name = request.user.username

    # Only completed / delivered orders (real sales)
    orders = (
        Placedorderxx.objects
        .filter(
            product__vendor=seller_name,
            status__in=['delivered', 'completed']
        )
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]  # Top 5 products
    )

    labels = [item['product__name'] for item in orders]
    values = [item['total_sold'] for item in orders]

    context = {
        'labels': labels,
        'values': values,
    }

    return render(request, 'saller/seller_top_selling_products.html', context)






























from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Tickets
from django.contrib.auth.models import User
import uuid

# ---------- Helper ----------
def generate_ticket_number():
    return f"TCK-{uuid.uuid4().hex[:8].upper()}"


# ---------- Seller Dashboard ----------
@login_required
def seller_ticket_dashboard(request):
    tickets = Tickets.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'saller/seller_ticket_dashboard.html', {'tickets': tickets})


# ---------- Create Ticket ----------
@login_required
def create_tickets(request):
    if request.method == 'POST':
        ticket = Tickets.objects.create(
            ticket_number=generate_ticket_number(),
            seller=request.user,
            name=request.POST['name'],
            mobile=request.POST['mobile'],
            email=request.POST['email'],
            title=request.POST['title'],
            description=request.POST['description'],
            category=request.POST['category'],
            priority=request.POST['priority'],
            department=request.POST.get('department'),
            due_date=request.POST.get('due_date') or None,
            location=request.POST.get('location'),
            attachment=request.FILES.get('attachment')
        )
        messages.success(request, f"Ticket {ticket.ticket_number} created successfully!")
        return redirect('ticket_detail', ticket.id)
    return render(request, 'saller/create_ticket.html')

@login_required
def create_ticket(request):
    if request.method == 'POST':
        ticket = Tickets.objects.create(
            ticket_number=generate_ticket_number(),
            seller=request.user,
            name=request.POST['name'],
            mobile=request.POST['mobile'],
            email=request.POST['email'],
            title=request.POST['title'],
            description=request.POST['description'],
            category=request.POST['category'],
            priority=request.POST['priority'],
            department=request.POST.get('department'),
            due_date=request.POST.get('due_date') or None,
            location=request.POST.get('location'),
            attachment=request.FILES.get('attachment')
        )

        # redirect to success page with ticket number
        return redirect('ticket_success', ticket_number=ticket.ticket_number)

    return render(request, 'saller/create_ticket.html')

@login_required
def ticket_success(request, ticket_number):
    return render(request, 'saller/ticket_success.html', {
        'ticket_number': ticket_number
    })

# ---------- Ticket Detail ----------



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Tickets, TicketReply


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)

    # ✅ SELLER REPLY
    if request.method == "POST" and not request.user.is_staff:

        # 🔒 Block if resolved or closed
        if ticket.status in ["RESOLVED", "CLOSED"]:
            messages.error(request, "This ticket is closed. You cannot reply.")
            return redirect("ticket_detail", ticket_id=ticket.id)

        message = request.POST.get("message")
        if message:
            TicketReply.objects.create(
                ticket=ticket,
                user=request.user,
                message=message
            )
            messages.success(request, "Reply sent successfully.")
            return redirect("ticket_detail", ticket_id=ticket.id)

    # ✅ ADMIN UPDATE
    if request.method == "POST" and request.user.is_staff:

        ticket.status = request.POST.get("status")
        ticket.priority = request.POST.get("priority")

        assigned_id = request.POST.get("assigned_to")
        if assigned_id:
            try:
                ticket.assigned_to = User.objects.get(id=assigned_id)
            except User.DoesNotExist:
                ticket.assigned_to = None
        else:
            ticket.assigned_to = None

        ticket.admin_description = request.POST.get("admin_description")

        # ✅ Correct resolved logic
        if ticket.status == "RESOLVED":
            if ticket.resolved_at is None:
                ticket.resolved_at = timezone.now()
        else:
            ticket.resolved_at = None

        ticket.save()

        admin_msg = request.POST.get("admin_message")
        if admin_msg:
            TicketReply.objects.create(
                ticket=ticket,
                user=request.user,
                message=admin_msg
            )

        messages.success(request, "Ticket updated successfully!")
        return redirect("ticket_detail", ticket_id=ticket.id)

    replies = ticket.replies.all().order_by("created_at")
    admins = User.objects.filter(is_staff=True)

    return render(request, "saller/ticket_detail.html", {
        "ticket": ticket,
        "replies": replies,
        "admins": admins
    })




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone


# 🔎 Ticket Search
def ticket_search(request):

    if request.method == "POST":

        ticket_number = request.POST.get("ticket_number", "").strip()

        # Validate input
        if not ticket_number:
            messages.error(request, "Please enter a ticket number.")
            return render(request, "ticket_search.html")

        # Find ticket
        ticket = Tickets.objects.filter(
            ticket_number=ticket_number
        ).first()

        # Ticket not found
        if ticket is None:
            messages.error(
                request,
                "Ticket number not found."
            )
            return render(request, "ticket_search.html")

        # ✅ IMPORTANT:
        # URL expects ticket_number, not ticket_id
        return redirect(
            "ticket_detailabcd",
            ticket_number=ticket.ticket_number
        )

    return render(request, "ticket_search.html")


def ticket_detailabcd(request, ticket_number):

    ticket = get_object_or_404(
        Tickets,
        ticket_number=ticket_number,
        seller=request.user
    )

    can_cancel = ticket.can_cancel()

    return render(
        request,
        "ticket_detailabcd.html",
        {
            "ticket": ticket,
            "can_cancel": can_cancel,
        }
    )


def ticket_cancel(request, ticket_number):

    ticket = get_object_or_404(
        Tickets,
        ticket_number=ticket_number,
        seller=request.user
    )

    # Check cancellation time
    if not ticket.can_cancel():
        messages.error(
            request,
            "❌ You can only cancel within 24 hours."
        )
        return redirect(
            "ticket_detailabcd",
            ticket_number=ticket.ticket_number
        )

    if request.method == "POST":

        reason = request.POST.get("reason", "").strip()

        ticket.status = "CANCELLED"
        ticket.cancel_reason = reason
        ticket.cancelled_at = timezone.now()
        ticket.save()

        messages.success(
            request,
            "✅ Ticket cancelled successfully."
        )

        return redirect(
            "ticket_detailabcd",
            ticket_number=ticket.ticket_number
        )

    return render(
        request,
        "ticket_cancel.html",
        {
            "ticket": ticket
        }
    )

def customer_order_detail(request, pk):
    order = get_object_or_404(Placedorderxx, pk=pk)
    return render(request, 'saller/customer_order_detail.html', {'order': order})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import ReturnRequestForm
from .models import ReturnRequested, Placedorderxx


@login_required
def create_return_request(request, order_id):

    order = get_object_or_404(
        Placedorderxx,
        id=order_id,
        user=request.user
    )


    # prevent duplicate return

    already_exists = ReturnRequested.objects.filter(
        order=order
    ).exists()


    if already_exists:
        messages.warning(
            request,
            "Return request already submitted."
        )

        return redirect(
            "customer_return_list"
        )



    if request.method == "POST":

        form = ReturnRequestForm(
            request.POST,
            request.FILES
        )


        if form.is_valid():

            return_obj = form.save(
                commit=False
            )


            return_obj.order = order

            return_obj.user = request.user


            # IMPORTANT
            # seller ownership

            return_obj.vendor = order.vendor



            # product details

            return_obj.product_name = order.product_name

            return_obj.product_image = order.product_image

            return_obj.selling_price = order.selling_price

            return_obj.quantity = order.quantity



            # customer details

            return_obj.name = order.name

            return_obj.address = order.address

            return_obj.phone = order.phone

            return_obj.postal_code = order.postal_code

            return_obj.city = order.city 

            return_obj.coupon_discount = order.coupon_discount

            return_obj.city = order.city

            return_obj.status = "requested"


            return_obj.save()



            messages.success(
                request,
                "Return request submitted successfully."
            )


            return redirect(
                "customer_return_list"
            )


    else:

        form = ReturnRequestForm()



    return render(
        request,
        "return_form.html",
        {
            "form":form,
            "order":order
        }
    )




@login_required
def customer_return_list(request):

    returns = ReturnRequested.objects.filter(
        user=request.user
    ).order_by('-id')

    return render(request, "customer_return_list.html", {
        "returns": returns
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ReturnRequested


@login_required
def return_detail(request, pk):

    return_request = get_object_or_404(
        ReturnRequested,
        id=pk,
        user=request.user
    )

    if request.method == "POST":

        if return_request.status == "pickup_scheduled":

            return_request.pickup_address = request.POST.get('pickup_address')
            return_request.pickup_date = request.POST.get('pickup_date')
            return_request.pickup_time_slot = request.POST.get('pickup_time_slot')
            return_request.pickup_reason = request.POST.get('pickup_reason')

            return_request.save()

        else:

            return_request.resubmit_reason = request.POST.get("resubmit_reason")
            return_request.resubmit_description = request.POST.get("resubmit_description")

            # image upload
            if request.FILES.get("resubmit_image"):
                return_request.resubmit_image = request.FILES["resubmit_image"]

            # video upload
            if request.FILES.get("resubmit_video"):
                return_request.resubmit_video = request.FILES["resubmit_video"]

            # change status
            return_request.status = "Resubmitted"

            return_request.save()

        return redirect("return_detail", pk=return_request.id)

    return render(request, "return_detail.html", {
        "return_request": return_request
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import ReturnRequested
@login_required
def seller_return_list(request):


    returns = ReturnRequested.objects.filter(
        vendor=request.user.username
    ).order_by(
        "-requested_at"
    )


    return render(
        request,
        "seller_return_list.html",
        {
            "returns":returns
        }
    )

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ReturnRequested


@login_required
def seller_return_detail1(request, pk):

    return_request = get_object_or_404(
        ReturnRequested,
        id=pk
    )

    if request.method == "POST":

        return_request.status = request.POST.get('status')

        return_request.reject_reason = request.POST.get(
            'reject_reason'
        )

        return_request.pickup_date = request.POST.get(
            'pickup_date'
        )

        return_request.pickup_time = request.POST.get(
            'pickup_time'
        )

        return_request.pickup_address = request.POST.get(
            'pickup_address'
        )

        if return_request.status.lower() == "refunded":

            if not return_request.refund_amount:

                return_request.refund_amount = request.POST.get(
                    'refund_amount'
                )

                return_request.refund_method = request.POST.get(
                    'refund_method'
                )

                return_request.transaction_id = request.POST.get(
                    'transaction_id'
                )

                return_request.refund_date = request.POST.get(
                    'refund_date'
                )

                return_request.seller_name = request.POST.get(
                    'seller_name'
                )

                return_request.seller_email = request.POST.get(
                    'seller_email'
                )

                return_request.refund_approved_by = request.POST.get(
                    'refund_approved_by'
                )

        return_request.save()

        return redirect(
            'seller_return_detail',
            pk=return_request.id
        )

    return render(
        request,
        'seller_return_detail.html',
        {
            'return_request': return_request
        }
    )


    from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import (
    login_required
)

from .models import ReturnRequested

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ReturnRequested


@login_required
def seller_return_list(request):

    seller = request.user
    returns = ReturnRequested.objects.filter(
        vendor=seller.username
    ).order_by('-id')

    return render(
        request,
        'seller_return_list.html',
        {
            'returns': returns
        }
    )

@login_required
def seller_return_detail(request, pk):

    return_request = get_object_or_404(
        ReturnRequested,
        id=pk
    )

    if request.method == "POST":

        return_request.status = request.POST.get(
            'status'
        )
        return_request.reject_reason = request.POST.get(
            'reject_reason'
        )

        return_request.pickup_date = request.POST.get(
            'pickup_date'
        )

        return_request.pickup_time = request.POST.get(
            'pickup_time'
        )

        return_request.pickup_address = request.POST.get(
            'pickup_address'
        )

        if (
            return_request.status.lower() == "refunded"
            and not return_request.refund_amount
        ):

            return_request.refund_amount = request.POST.get(
                'refund_amount'
            )

            return_request.refund_method = request.POST.get(
                'refund_method'
            )

            return_request.transaction_id = request.POST.get(
                'transaction_id'
            )

            return_request.refund_date = request.POST.get(
                'refund_date'
            )

            return_request.seller_name = request.POST.get(
                'seller_name'
            )

            return_request.seller_email = request.POST.get(
                'seller_email'
            )

            return_request.refund_approved_by = request.POST.get(
                'refund_approved_by'
            )
        return_request.save()

        return redirect(
            'seller_return_list'
        )

    return render(
        request,
        'seller_return_detail.html',
        {
            'return_request': return_request
        }
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import ReturnRequested
from django.utils import timezone


def admin_return_list(request):

    returns = ReturnRequested.objects.all().order_by('-created_at')

    context = {
        'returns': returns
    }

    return render(request,
                  'admin/return_list.html',context)


def admin_return_detail(request, id):

    return_request = get_object_or_404(ReturnRequested, id=id)

    context = {
        'return_request': return_request
    }

    return render(request,
                  'admin/return_detail.html',
                  context)



def admin_return_edit(request, id):

    return_request = get_object_or_404(ReturnRequested, id=id)

    if request.method == 'POST':

        return_request.status = request.POST.get('status')
        return_request.reject_reason = request.POST.get('reject_reason')

        return_request.pickup_address = request.POST.get('pickup_address')
        return_request.pickup_date = request.POST.get('pickup_date')
        return_request.pickup_time_slot = request.POST.get('pickup_time_slot')
        return_request.pickup_reason = request.POST.get('pickup_reason')

        return_request.pickup_partner = request.POST.get('pickup_partner')
        return_request.pickup_tracking_id = request.POST.get('pickup_tracking_id')

        return_request.refund_amount = request.POST.get('refund_amount') or None
        return_request.refund_method = request.POST.get('refund_method')
        return_request.transaction_id = request.POST.get('transaction_id')
        return_request.refund_date = request.POST.get('refund_date')
        return_request.seller_name = request.POST.get('seller_name')
        return_request.seller_email = request.POST.get('seller_email')
        return_request.refund_approved_by = request.POST.get('refund_approved_by')



        if request.POST.get('refund_date'):
            return_request.refund_date = request.POST.get('refund_date')

        return_request.refund_approved_by = request.user.username

        return_request.updated_at = timezone.now()

        return_request.save()

        messages.success(request, 'Return request updated successfully.')

        return redirect('admin_return_detail', id=return_request.id)

    context = {
        'return_request': return_request,
        'status_choices': ReturnRequested.STATUS_CHOICES
    }

    return render(request,
                  'admin/return_edit.html',
                  context)

def admin_return_delete(request, id):

    return_request = get_object_or_404(ReturnRequested, id=id)

    if request.method == 'POST':

        return_request.delete()

        messages.success(request, 'Return request deleted successfully.')

        return redirect('admin_return_list')

    context = {
        'return_request': return_request
    }

    return render(request,
                  'admin/return_delete.html',
                  context)


from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .forms import AdvertisementForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


@login_required
def saller_advertisements(request):

    ads = Advertisementx.objects.filter(
        seller=request.user
    )

    total_ads = ads.count()

    active_ads = ads.filter(
        status="RUNNING"
    ).count()

    pending_ads = ads.filter(
        status="WAITING_APPROVAL"
    ).count()

    expired_ads = ads.filter(
        status="EXPIRED"
    ).count()

    total_spending = ads.aggregate(
        total=Sum("amount")
    )["total"] or 0

    context = {

        "total_ads": total_ads,
        "active_ads": active_ads,
        "pending_ads": pending_ads,
        "expired_ads": expired_ads,
        "total_spending": total_spending,
        "ads": ads

    }

    return render(
        request,
        "saller/advertisements.html",
        context
    )

@login_required
def create_advertisement(request):

    if request.method == "POST":

        form = AdvertisementForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            ad = form.save(commit=False)

            ad.seller = request.user
            ad.status = "PENDING_PAYMENT"
            ad.payment_status = "PENDING"

            plan_prices = {
                "BASIC": 500,
                "STANDARD": 1250,
                "PREMIUM": 2500,
                "GOLD": 4500,
                "PLATINUM": 8000,
            }

            plan = request.POST.get("plan")
            amount = plan_prices.get(plan)

            if amount is None:
                form.add_error("plan", "Please select a valid advertisement plan.")
            else:
                ad.plan = plan
                ad.amount = amount
                ad.save()

                return redirect(
                    "advertisement_payment",
                    ad.id
                )

    else:
        form = AdvertisementForm()

    return render(
        request,
        "saller/create_advertisement.html",
        {
            "form": form
        }
    )

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .forms import AdvertisementForm


@login_required
def advertisement_detail(request, pk):

    advertisement = get_object_or_404(
        Advertisementx,
        id=pk,
        seller=request.user
    )

    can_edit = advertisement.status in [
        "PENDING_PAYMENT",
        "WAITING_APPROVAL",
        "REJECTED",
    ]

    can_delete = can_edit

    can_pay = advertisement.payment_status == "PENDING"

    can_renew = advertisement.status == "EXPIRED"

    context = {

        "advertisement": advertisement,
        "can_edit": can_edit,
        "can_delete": can_delete,
        "can_pay": can_pay,
        "can_renew": can_renew,

    }

    return render(
        request,
        "saller/advertisement_detail.html",
        context
    )



@login_required
def edit_advertisement(request, pk):

    advertisement = get_object_or_404(
        Advertisementx,
        id=pk,
        seller=request.user
    )

    if advertisement.status not in [
        "PENDING_PAYMENT",
        "WAITING_APPROVAL",
        "REJECTED",
    ]:

        messages.error(
            request,
            "Approved or Running advertisements cannot be edited."
        )

        return redirect(
            "advertisement_detail",
            pk=pk
        )

    if request.method == "POST":

        form = AdvertisementForm(
            request.POST,
            request.FILES,
            instance=advertisement
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Advertisement updated successfully."
            )

            return redirect(
                "advertisement_detail",
                pk=pk
            )

    else:

        form = AdvertisementForm(
            instance=advertisement
        )

    return render(
        request,
        "saller/edit_advertisement.html",
        {
            "form": form
        }
    )





@login_required
def delete_advertisement(request, pk):

    advertisement = get_object_or_404(
        Advertisementx,
        id=pk,
        seller=request.user
    )

    if advertisement.status not in [
        "PENDING_PAYMENT",
        "WAITING_APPROVAL",
        "REJECTED",
    ]:

        messages.error(
            request,
            "This advertisement cannot be deleted."
        )

        return redirect(
            "advertisement_detail",
            pk=pk
        )

    if request.method == "POST":

        advertisement.delete()

        messages.success(
            request,
            "Advertisement deleted successfully."
        )

        return redirect(
            "seller_dashboard"
        )

    return render(
        request,
        "saller/delete_advertisement.html",
        {
            "advertisement": advertisement
        }
    )


from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone




@login_required
def create_renewal(request,id):

    ad=get_object_or_404(
        Advertisementx,
        id=id,
        seller=request.user
    )


    if request.method=="POST":


        plan=request.POST.get("plan")


        renewal=AdvertisementRenewalx.objects.create(

            advertisement=ad,

            seller=request.user,

            plan=plan,

            payment_status="PENDING",

            renewal_start=timezone.now().date()

        )



        return redirect(
            "renewal_detail",
            id=ad.id
        )



    return render(
        request,
        "saller/create_renewal.html",
        {
            "ad":ad
        }
    )


from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from .models import AdvertisementRenewalx


@login_required
def renew_advertisement(request, id):

    advertisement = get_object_or_404(
        Advertisementx,
        id=id,
        seller=request.user
    )

    if request.method == "POST":

        plan = request.POST.get("plan")

        details = Advertisementx.PLAN_DETAILS[plan]

        duration = details["duration"]
        amounts = details["amount"]

        AdvertisementRenewalx.objects.create(
            advertisement=advertisement,
            seller=request.user,
            plan=plan,
            duration=duration,
            amounts=amounts,
            payment_status="PAID",
            payment_method="RAZORPAY",
            payment_id="pay_xxxxx",
            paid_at=timezone.now()
        )

        today = timezone.now().date()

        # Extend from current end date if still active
        if advertisement.end_date and advertisement.end_date >= today:
            advertisement.end_date = advertisement.end_date + timedelta(days=duration)
        else:
            advertisement.start_date = today
            advertisement.end_date = today + timedelta(days=duration)

        advertisement.status = "PENDING"
        advertisement.is_renewed = True
        advertisement.renewal_date = today
        advertisement.renewal_expiry = advertisement.end_date

        advertisement.save()

        return redirect("renewal_history", advertisement.id)

    return render(
        request,
        "saller/renew_ad.html",
        {
            "advertisement": advertisement
        }
    )

@login_required
def renewal_history(request,id):


    advertisement=get_object_or_404(
        Advertisementx,
        id=id,
        seller=request.user
    )


    renewals=AdvertisementRenewalx.objects.filter(
        advertisement=advertisement
    )


    return render(
        request,
        "saller/renewal_history.html",
        {
            "advertisement":advertisement,
            "renewals":renewals
        }
    )


@login_required
def renewal_detail(request,id):


    ad=get_object_or_404(
        Advertisementx,
        id=id,
        seller=request.user
    )


    renewals=Advertisementx.objects.filter(
        advertisement=ad
    ).order_by(
        "-created_at"
    )


    return render(
        request,
        "saller/renewal_detail.html",
        {
            "ad":ad,
            "renewals":renewals
        }
    )

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone



@login_required
def advertisement_payment(request, id):

    advertisement = get_object_or_404(
        Advertisementx,
        id=id,
        seller=request.user
    )

    if request.method == "POST":

        payment_method = request.POST.get("payment_method")

        payment_result = request.POST.get("payment_result")

        payment_id = request.POST.get("payment_id")

        advertisement.payment_method = payment_method
        advertisement.payment_id = payment_id

        if payment_result == "SUCCESS":

            advertisement.payment_status = "PAID"

            advertisement.status = "WAITING_APPROVAL"

            advertisement.paid_at = timezone.now()

            advertisement.save()

            messages.success(
                request,
                "Payment completed successfully."
            )

            return redirect(
                "advertisement_detail",
                advertisement.id
            )

        else:

            advertisement.payment_status = "FAILED"

            advertisement.status = "PENDING_PAYMENT"

            advertisement.save()

            messages.error(
                request,
                "Payment failed. Please try again."
            )

            return redirect(
                "advertisement_payment",
                advertisement.id
            )

    return render(
        request,
        "saller/advertisement_payment.html",
        {
            "advertisement": advertisement
        }
    )

@login_required
def payment_success(request,id):


    advertisement=Advertisementx.objects.get(
        id=id,
        seller=request.user
    )


    payment_id=request.GET.get(
        "payment_id"
    )


    advertisement.payment_id=payment_id

    advertisement.payment_status="PAID"

    advertisement.status="WAITING_APPROVAL"

    advertisement.paid_at=timezone.now()


    advertisement.audit_log.append({

        "action":"Payment Completed",

        "payment_id":payment_id,

        "time":str(timezone.now())

    })


    advertisement.save()



    messages.success(
        request,
        "Payment completed. Waiting for admin approval."
    )



    return redirect(
        "saller_advertisements"
    )







@login_required
def advertisement_status(request,id):


    advertisement=Advertisementx.objects.get(

        id=id,

        seller=request.user

    )


    return render(

        request,

        "saller/ad_status.html",

        {
            "advertisement":advertisement
        }

    )


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Advertisementx
from .forms import AdminAdvertisementUpdateForm

@login_required
def advertisement_dashboard(request):

    ads = Advertisementx.objects.all().order_by("-created_at")

    for ad in ads:
        ad.update_status(save=True)
    ads = Advertisementx.objects.all().order_by("-created_at")

    total_ads = ads.count()

    pending_ads = ads.filter(
        status="WAITING_APPROVAL"
    ).count()

    approved_ads = ads.filter(
        status="APPROVED"
    ).count()

    running_ads = ads.filter(
        status="RUNNING"
    ).count()

    expired_ads = ads.filter(
        status="EXPIRED"
    ).count()

    rejected_ads = ads.filter(
        status="REJECTED"
    ).count()

    context = {
        "ads": ads,
        "total_ads": total_ads,
        "pending_ads": pending_ads,
        "approved_ads": approved_ads,
        "running_ads": running_ads,
        "expired_ads": expired_ads,
        "rejected_ads": rejected_ads,
    }

    return render(
        request,
        "admin/advertisement_dashboard.html",
        context,
    )




from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages

from django.utils import timezone


from .forms import AdminAdvertisementEditForm

def admin_advertisement_detail(request,id):

    ad = get_object_or_404(
        Advertisementx,
        id=id
    )


    return render(
        request,
        "admin/advertisement_detail.html",
        {
            "ad":ad
        }
    )





from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import AdminAdvertisementEditForm


def admin_advertisement_edit(request, id):

    ad = get_object_or_404(
        Advertisementx,
        id=id
    )

    if request.method == "POST":

        form = AdminAdvertisementEditForm(
            request.POST,
            request.FILES,
            instance=ad
        )

        if form.is_valid():

            advertisement = form.save(commit=False)

            old_status = ad.status

            # If admin approves the advertisement
            if advertisement.status == "APPROVED":

                if not advertisement.approved_by:
                    advertisement.approved_by = request.user

                if not advertisement.approved_at:
                    advertisement.approved_at = timezone.now()

            # Prevent manual RUNNING before start time
            if (
                advertisement.status == "RUNNING"
                and advertisement.start_datetime
                and timezone.now() < advertisement.start_datetime
            ):
                advertisement.status = "APPROVED"

            # Clear approval details if rejected
            if advertisement.status == "REJECTED":

                advertisement.approved_by = None
                advertisement.approved_at = None

            # Audit log
            advertisement.audit_log.append({

                "action": "Advertisement Updated",

                "admin": request.user.username,

                "old_status": old_status,

                "new_status": advertisement.status,

                "start_datetime": str(advertisement.start_datetime),

                "end_datetime": str(advertisement.end_datetime),

                "time": str(timezone.now())

            })

            advertisement.save()

            return redirect(
                "admin_advertisement_detail",
                id=advertisement.id
            )

    else:

        form = AdminAdvertisementEditForm(instance=ad)

    return render(
        request,
        "admin/admin_advertisement_edit.html",
        {
            "form": form,
            "ad": ad
        }
    )








from .forms import AdminAdvertisementUpdateForm,AdminAdvertisementautoUpdateForm,AdvertisementxAdmineditForm
from .models import Advertisementx



@login_required
def approve_ad(request, id):

    advertisement = get_object_or_404(
        Advertisementx,
        id=id,
    )
    if request.method == "POST":

        form = AdminAdvertisementUpdateForm(
            request.POST,
            instance=advertisement,
        )

        if form.is_valid():

            obj = form.save(commit=False)

            now = timezone.now()

            if obj.start_datetime and obj.end_datetime:

                if now < obj.start_datetime:

                    obj.status = "APPROVED"

                elif obj.start_datetime <= now < obj.end_datetime:

                    obj.status = "RUNNING"

                else:

                    obj.status = "EXPIRED"

            else:

                obj.status = "WAITING_APPROVAL"

            if obj.status in [
                "APPROVED",
                "RUNNING",
            ]:

                obj.approved_by = request.user
                obj.approved_at = now

            obj.save()

            return redirect(
                "advertisement_dashboard"
            )

    else:

        form = AdminAdvertisementUpdateForm(
            instance=advertisement,
        )

    return render(
        request,
        "admin/approve_ad.html",
        {
            "form": form,
            "advertisement": advertisement,
        },
    )





@login_required
def admin_advertisement_edit(request, id):

    advertisement = get_object_or_404(
        Advertisementx,
        id=id
    )

    # Update current status before displaying the page.
    advertisement.update_status()

    if request.method == "POST":

        form = AdminAdvertisementUpdateForm(
            request.POST,
            instance=advertisement
        )

        if form.is_valid():

            obj = form.save(commit=False)

            now = timezone.now()

            # Admin selected APPROVED.
            if obj.status == "APPROVED":

                if obj.start_datetime and obj.end_datetime:

                    if now < obj.start_datetime:

                        obj.status = "APPROVED"

                    elif obj.start_datetime <= now < obj.end_datetime:

                        obj.status = "RUNNING"

                    else:

                        obj.status = "EXPIRED"

            # If admin selected other manual states,
            # keep them.
            obj.save()

            return redirect("renewals")

    else:

        form = AdminAdvertisementUpdateForm(
            instance=advertisement
        )

    return render(
        request,
        "admin/edit_advertisement.html",
        {
            "form": form,
            "advertisement": advertisement,
        }
    )


def advertisement_edit_form(request, pk):

    advertisement = get_object_or_404(
        Advertisementx,
        pk=pk
    )

    old_status = advertisement.status

    if request.method == "POST":

        form = AdvertisementxAdmineditForm(
            request.POST,
            request.FILES,
            instance=advertisement
        )

        if form.is_valid():

            old_values = {}

            tracked_fields = [
                "seller",
                "title",
                "description",
                "plan",
                "duration",
                "amount",
                "start_datetime",
                "end_datetime",
                "start_date",
                "end_date",
                "status",
                "payment_method",
                "payment_id",
                "payment_status",
                "paid_at",
                "rejected_reason",
                "is_renewed",
                "renewal_date",
                "renewal_expiry",
                "views",
                "clicks",
                "ctr",
                "featured",
            ]

            for field_name in tracked_fields:
                value = getattr(advertisement, field_name)

                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                elif hasattr(value, "pk"):
                    value = value.pk

                old_values[field_name] = value

            # -----------------------------------------
            # Save form
            # -----------------------------------------

            advertisement = form.save(commit=False)

            new_status = advertisement.status

            # -----------------------------------------
            # APPROVED
            # -----------------------------------------

            if new_status == "APPROVED":

                if old_status != "APPROVED":
                    advertisement.approved_by = request.user

                else:
                    advertisement.approved_by = (
                        advertisement.approved_by
                        or request.user
                    )

                    advertisement.approved_at = (
                        advertisement.approved_at
                        or timezone.now()
                    )

                # Remove rejection information
                advertisement.rejected_reason = ""

            elif new_status == "REJECTED":

                # Reason is required
                if not advertisement.rejected_reason:
                    form.add_error(
                        "rejected_reason",
                        "Please enter a rejection reason."
                    )

                    return render(
                        request,
                        "admin/advertisementx_edit.html",
                        {
                            "form": form,
                            "advertisement": advertisement,
                        }
                    )

                advertisement.approved_by = None
                advertisement.approved_at = None

            else:

                # Don't keep an old rejection reason if
                # advertisement is moved out of REJECTED.
                if new_status != "REJECTED":
                    advertisement.rejected_reason = ""

            advertisement.save()

            new_values = {}

            for field_name in tracked_fields:
                value = getattr(advertisement, field_name)

                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                elif hasattr(value, "pk"):
                    value = value.pk

                new_values[field_name] = value

            changes = {}

            for field_name in tracked_fields:

                old_value = old_values.get(field_name)
                new_value = new_values.get(field_name)

                if old_value != new_value:
                    changes[field_name] = {
                        "old": old_value,
                        "new": new_value,
                    }

            if old_status != new_status:

                changes["status_change"] = {
                    "old": old_status,
                    "new": new_status,
                }

            if changes:

                audit_log = advertisement.audit_log or []

                audit_entry = {
                    "action": "ADMIN_UPDATE",
                    "admin_id": request.user.pk,
                    "admin_username": request.user.username,
                    "timestamp": timezone.now().isoformat(),
                    "changes": changes,
                }

                audit_log.append(audit_entry)

                advertisement.audit_log = audit_log

                advertisement.save(
                    update_fields=["audit_log"]
                )

            # -----------------------------------------
            # Success message
            # -----------------------------------------

            if new_status == "APPROVED":

                messages.success(
                    request,
                    "Advertisement approved successfully."
                )

            elif new_status == "REJECTED":

                messages.warning(
                    request,
                    "Advertisement rejected successfully."
                )

            else:

                messages.success(
                    request,
                    "Advertisement updated successfully."
                )

            return redirect(
                "advertisement_dashboard"
            )

    else:

        form = AdvertisementxAdmineditForm(
            instance=advertisement
        )

    return render(
        request,
        "admin/advertisement_edit_form.html",
        {
            "form": form,
            "advertisement": advertisement,
        }
    )




    
def approve_advertisement(request,id):

    ad=get_object_or_404(
        Advertisementx,
        id=id
    )


    ad.status="APPROVED"

    ad.approved_by=request.user

    ad.approved_at=timezone.now()


    ad.audit_log.append({

        "action":"Approved",

        "admin":request.user.username,

        "time":str(timezone.now())

    })


    ad.save()


    messages.success(
        request,
        "Advertisement approved successfully"
    )


    return redirect(
        "advertisement_dashboard"
    )


def reject_advertisement(request,id):

    ad=get_object_or_404(
        Advertisementx,
        id=id
    )



    if request.method=="POST":

        reason=request.POST.get(
            "reason"
        )


        ad.status="REJECTED"

        ad.rejected_reason=reason

        ad.approved_by=request.user


        ad.audit_log.append({

            "action":"Rejected",

            "admin":request.user.username,

            "reason":reason,

            "time":str(timezone.now())

        })


        ad.save()



        messages.success(
            request,
            "Advertisement rejected"
        )


        return redirect(
            "advertisement_dashboard"
        )



    return render(
        request,
        "admin/reject_advertisement.html",
        {
            "ad":ad
        }
    )



from django.shortcuts import render, get_object_or_404

def advertisement_payment_details(request, id):

    payment = get_object_or_404(
        Advertisementx,
        id=id
    )


    context = {
        "payment": payment
    }


    return render(
        request,
        "admin/advertisement_payment_details.html",
        context
    )

from django.shortcuts import render, get_object_or_404

def advertisement_sallerdetails(request, id):
    advertisement = get_object_or_404(
        Advertisementx,
        id=id
    )

    context = {
        "advertisement": advertisement
    }

    return render(
        request,
        "admin/advertisement_sallerdetails.html",
        context
    )


from django.shortcuts import render, get_object_or_404

def advertisement_plan_details(request, id):

    plan = get_object_or_404(
        Advertisementx,
        id=id
    )

    context = {
        "plan": plan
    }

    return render(
        request,
        "admin/advertisement_plan_details.html",
        context
    )



from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render



def expired_advertisements(request):

    advertisements = Advertisementx.objects.filter(
        status="EXPIRED"
    ).select_related("seller")

    return render(
        request,
        "admin/expired_ads.html",
        {
            "advertisements":advertisements
        }
    )


from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import AdvertisementRenewalx
from .forms import (
    AdvertisementRenewalForm,
    AdminRenewalUpdateForm
)


def renewals(request):

    renewals = AdvertisementRenewalx.objects.all()


    for renewal in renewals:

        renewal.update_status()



    return render(
        request,
        "admin/renewals.html",
        {
            "renewals":renewals
        }
    )





from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.utils import timezone

from .models import AdvertisementRenewalx
from .forms import AdminRenewalUpdateForm


def admin_renewal_edit(request, id):

    renewal = get_object_or_404(
        AdvertisementRenewalx,
        id=id
    )

    # Automatic status update
    renewal.update_status()

    if request.method == "POST":

        form = AdminRenewalUpdateForm(
            request.POST,
            instance=renewal
        )

        if form.is_valid():

            obj = form.save(commit=False)

            now = timezone.now()

            if obj.start_date and obj.end_date:

                if now < obj.start_date:
                    obj.status = "APPROVED"

                elif obj.start_date <= now <= obj.end_date:
                    obj.status = "RUNNING"

                else:
                    obj.status = "EXPIRED"

            obj.save()

            return redirect("renewals")

    else:

        form = AdminRenewalUpdateForm(instance=renewal)

    return render(
        request,
        "admin/edit.html",
        {
            "form": form,
            "renewal": renewal,
        }
    )


from django.http import JsonResponse


def check_renewal_status(request):

    renewals = AdvertisementRenewalx.objects.all()


    for renewal in renewals:

        renewal.update_status()



    return JsonResponse(
        {
            "status":"updated"
        }
    )