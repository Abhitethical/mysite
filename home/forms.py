from pyexpat import model

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomerRegistration


class CustomUserForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter User Name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Email Address'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Your Password'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")

        return email


class CustomerRegistrationFormx(forms.ModelForm):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Phone Number'
        })
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Address',
            'rows': 3
        })
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = CustomerRegistration
        fields = ['profile_image', 'phone', 'address']
        


from django import forms
from PIL import Image, UnidentifiedImageError
from .models import CustomerRegistration


class CustomerRegistrationForm(forms.ModelForm):

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Phone Number',
                'inputmode': 'numeric',
                'maxlength': '10',
                'autocomplete': 'off'
            }
        )
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Address',
                'rows': 3,
                'autocomplete': 'off'
            }
        )
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp'
            }
        )
    )

    class Meta:
        model = CustomerRegistration
        fields = ['profile_image', 'phone', 'address']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()

        # Only digits
        if not phone.isdigit():
            raise forms.ValidationError(
                "Phone number must contain only numbers."
            )

        # Indian 10-digit mobile number
        if len(phone) != 10:
            raise forms.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        if phone[0] not in "6789":
            raise forms.ValidationError(
                "Enter a valid mobile number."
            )

        return phone

    def clean_profile_image(self):
        uploaded_file = self.cleaned_data.get('profile_image')

        if not uploaded_file:
            return uploaded_file

        # -----------------------------------------
        # 1. Maximum file size: 5 MB
        # -----------------------------------------
        MAX_SIZE = 5 * 1024 * 1024

        if uploaded_file.size > MAX_SIZE:
            raise forms.ValidationError(
                "Profile image must be smaller than 5 MB."
            )

        # -----------------------------------------
        # 2. Check extension
        # -----------------------------------------
        allowed_extensions = {
            'jpg',
            'jpeg',
            'png',
            'webp'
        }

        filename = uploaded_file.name.lower()

        if '.' not in filename:
            raise forms.ValidationError(
                "Invalid image filename."
            )

        extension = filename.rsplit('.', 1)[1]

        if extension not in allowed_extensions:
            raise forms.ValidationError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        # -----------------------------------------
        # 3. Check actual image content with Pillow
        # -----------------------------------------
        try:
            uploaded_file.seek(0)

            image = Image.open(uploaded_file)

            # Verify image structure
            image.verify()

            uploaded_file.seek(0)

            # Open again after verify()
            image = Image.open(uploaded_file)

            # -----------------------------------------
            # 4. Verify actual detected format
            # -----------------------------------------
            allowed_formats = {
                'JPEG',
                'PNG',
                'WEBP'
            }

            if image.format not in allowed_formats:
                raise forms.ValidationError(
                    "The uploaded file is not a supported image format."
                )

            # -----------------------------------------
            # 5. Prevent decompression-bomb images
            # -----------------------------------------
            MAX_PIXELS = 20_000_000

            if image.width * image.height > MAX_PIXELS:
                raise forms.ValidationError(
                    "Image dimensions are too large."
                )

            # -----------------------------------------
            # 6. Force complete image loading
            # -----------------------------------------
            image.load()

        except (UnidentifiedImageError, OSError, ValueError):
            raise forms.ValidationError(
                "The uploaded file is corrupted or is not a valid image."
            )

        finally:
            uploaded_file.seek(0)

        return uploaded_file



from django import forms
from django.core.exceptions import ValidationError
import re

# Country, State, and City choices (ideally you'd load these dynamically or model them)
COUNTRY_CHOICES = [
    ('', 'Select Country'),
    ('India', 'India'),
    ('USA', 'USA'),
    ('UK', 'UK'),
]

STATE_CHOICES = [
     ('', 'Select State'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
    ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
    ('Chandigarh', 'Chandigarh'),
    ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('Delhi', 'Delhi'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Ladakh', 'Ladakh'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Puducherry', 'Puducherry'),
]

CITY_CHOICES = [
    ('', 'Select District'),
    ('Alappuzha', 'Alappuzha'),
    ('Ernakulam', 'Ernakulam'),
    ('Idukki', 'Idukki'),
    ('Kannur', 'Kannur'),
    ('Kasaragod', 'Kasaragod'),
    ('Kollam', 'Kollam'),
    ('Kottayam', 'Kottayam'),
    ('Kozhikode', 'Kozhikode'),
    ('Malappuram', 'Malappuram'),
    ('Palakkad', 'Palakkad'),
    ('Pathanamthitta', 'Pathanamthitta'),
    ('Thiruvananthapuram', 'Thiruvananthapuram'),
    ('Thrissur', 'Thrissur'),
    ('Wayanad', 'Wayanad'),

]

class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'})
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )
    address_line1 = forms.CharField(
        max_length=255,
        label="Address Line 1",
        widget=forms.TextInput(attrs={'placeholder': 'Street address, P.O. box, etc.'})
    )
    address_line2 = forms.CharField(
        max_length=255,
        required=False,
        label="Address Line 2",
        widget=forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit, etc. (optional)'})
    )
    
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        label="Country"
    )
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        label="State"
    )
    city = forms.ChoiceField(
        choices=CITY_CHOICES,
        label="City"
    )

    postal_code = forms.CharField(
        max_length=6,
        label="Postal Code",
        widget=forms.TextInput(attrs={'placeholder': '6-digit PIN/ZIP code'})
    )
    phone = forms.CharField(
        max_length=10,
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': '10-digit phone number'})
    )

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if not re.match(r'^\d{6}$', postal_code):
            raise ValidationError("Postal code must be exactly 6 digits.")
        return postal_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\d{10}$', phone):
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone



from django import forms

class ProductSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255)

















# forms.py
from django import forms
from django.contrib.auth.models import User

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user with this email.")
        return email



from django import forms

class OTPVerifyForm(forms.Form):
    otp = forms.CharField(max_length=6, label="Enter OTP")













from django import forms
from .models import SellerProfile

class SellerProfileForm(forms.ModelForm):
     class Meta:
         model = SellerProfile
         fields = [
             'company_name',
             'address',
             'city',
             'state',
             'pincode',
             'country',
        ]
         widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }







from django import forms
from .models import SellerBankDetailxx

class SellerBankForm(forms.ModelForm):
    class Meta:
        model = SellerBankDetailxx
        # Seller fills these fields
        fields = ['name', 'mobile_number', 'address', 'account_number', 'ifsc_code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter account number'}),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter IFSC code', 'id': 'ifsc'}),
        }





# forms.py
from django import forms
from .models import SellerBankDetailxx

class SellerBankFormxx(forms.ModelForm):
    class Meta:
        model = SellerBankDetailxx
        fields = [
            'name',
            'mobile_number',
            'account_number',
            'ifsc_code',
            'bank_name',
            'bank_branch',
            'bank_code',
        ]
        widgets = {
            'bank_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'bank_branch': forms.TextInput(attrs={'readonly': 'readonly'}),
            'bank_code': forms.TextInput(attrs={'readonly': 'readonly'}),
        }




from django import forms
from .models import ReturnRequested

class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequested
        fields = ["reason", "description", "image", "video"]


from django import forms
from .models import ReturnRequested

class SellerRefundForm(forms.ModelForm):
    class Meta:
        model = ReturnRequested
        fields = [
            "refund_amount",
            "refund_method",
            "transaction_id",
            "refund_date",
            "seller_name",
            "seller_email",
            "refund_approved_by",
        ]

















from django import forms
from .models import Advertisementx


class AdvertisementForm(forms.ModelForm):

    class Meta:

        model = Advertisementx

        fields = [
            "title",
            "product_image",
            "video",
            "thumbnail",
            "start_date",
            "end_date",
            "description",
            "plan",
        ]


        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Advertisement Title"
                }
            ),


            "product_image": forms.FileInput(
                attrs={
                    "class": "form-control"
                }
            ),


            "video": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "video/mp4"
                }
            ),


            "thumbnail": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*"
                }
            ),


            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),


            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),


            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Advertisement Description"
                }
            ),


            "plan": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "plan"
                }
            ),
        }



    # Video Validation

    def clean_video(self):

        video = self.cleaned_data.get("video")


        if video:

            # Check size 100MB

            size = video.size / (1024 * 1024)


            if size > 100:

                raise forms.ValidationError(
                    "Maximum video size allowed is 100 MB"
                )


            # Check MP4

            extension = video.name.split(".")[-1].lower()


            if extension != "mp4":

                raise forms.ValidationError(
                    "Only MP4 video format is supported"
                )


        return video



    # Date Validation

    def clean(self):

        cleaned_data = super().clean()


        start = cleaned_data.get(
            "start_date"
        )

        end = cleaned_data.get(
            "end_date"
        )


        if start and end:

            if end < start:

                raise forms.ValidationError(
                    "End date must be after start date"
                )


        return cleaned_data
    






























from django import forms
from .models import AdvertisementRenewalx


class AdvertisementRenewalForm(forms.ModelForm):

    class Meta:
        model = AdvertisementRenewalx

        fields = [
            "advertisement",
            "plan",
            "duration",
            "amounts",
            "payment_method",
            "payment_id",
        ]

        widgets = {

            "plan": forms.TextInput(
                attrs={
                    "class":"form-control"
                }
            ),

            "duration": forms.NumberInput(
                attrs={
                    "class":"form-control"
                }
            ),

            "amounts": forms.NumberInput(
                attrs={
                    "class":"form-control"
                }
            ),

            "payment_method": forms.Select(
                attrs={
                    "class":"form-control"
                }
            ),

            "payment_id": forms.TextInput(
                attrs={
                    "class":"form-control"
                }
            ),
        }



class AdminRenewalUpdateForm(forms.ModelForm):

    class Meta:

        model = AdvertisementRenewalx

        fields = [
            "start_date",
            "end_date",
            "status",
        ]


        widgets = {

            "start_date": forms.DateTimeInput(
                attrs={
                    "class":"form-control",
                    "type":"datetime-local"
                }
            ),


            "end_date": forms.DateTimeInput(
                attrs={
                    "class":"form-control",
                    "type":"datetime-local"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class":"form-control"
                }
            ),
        }


from django import forms
from .models import Advertisementx

class AdminAdvertisementEditForm(forms.ModelForm):

    class Meta:

        model = Advertisementx

        fields = [

            "title",
            "description",
            "product_image",
            "video",
            "thumbnail",

            "plan",
            "duration",
            "amount",

            "start_datetime",
            "end_datetime",

            "status",

            "payment_method",
            "payment_status",

            "featured",

            "approved_by",
            "approved_at",

            "rejected_reason",

        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5
                }
            ),

            "start_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                },
                format="%Y-%m-%dT%H:%M"
            ),

            "end_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                },
                format="%Y-%m-%dT%H:%M"
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "payment_status": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "payment_method": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "plan": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "featured": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["start_datetime"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

        self.fields["end_datetime"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

from django import forms
from .models import Advertisementx

from django import forms
from .models import Advertisementx


class AdminAdvertisementUpdateForm(forms.ModelForm):

    class Meta:
        model = Advertisementx
        fields = [
            "start_datetime",
            "end_datetime",
            "status",
        ]

        widgets = {
            "start_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "end_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["start_datetime"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

        self.fields["end_datetime"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]






class AdminAdvertisementautoUpdateForm(forms.ModelForm):

    class Meta:

        model = Advertisementx

        fields = [
            "start_date",
            "end_date",
            "status",
        ]


        widgets = {

            "start_date": forms.DateTimeInput(
                attrs={
                    "class":"form-control",
                    "type":"datetime-local"
                }
            ),


            "end_date": forms.DateTimeInput(
                attrs={
                    "class":"form-control",
                    "type":"datetime-local"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class":"form-control"
                }
            ),
        }







# =========================================================
# forms.py
# =========================================================

from django import forms
from .models import Advertisementx


class AdminAdvertisementUpdateForm(forms.ModelForm):

    class Meta:
        model = Advertisementx

        fields = [
            "start_datetime",
            "end_datetime",
        ]

        widgets = {
            "start_datetime": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "end_datetime": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.start_datetime:
            self.initial["start_datetime"] = (
                self.instance.start_datetime.strftime(
                    "%Y-%m-%dT%H:%M"
                )
            )

        if self.instance and self.instance.end_datetime:
            self.initial["end_datetime"] = (
                self.instance.end_datetime.strftime(
                    "%Y-%m-%dT%H:%M"
                )
            )

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get("start_datetime")
        end = cleaned_data.get("end_datetime")

        if start and end and end <= start:
            raise forms.ValidationError(
                "End date/time must be after start date/time."
            )

        return cleaned_data

















from django import forms
from django.contrib.auth.models import User

from .models import Advertisementx





class AdvertisementxAdmineditForm(forms.ModelForm):

    class Meta:
        model = Advertisementx

        fields = [
            "seller",

            "product_image",

            "start_datetime",
            "end_datetime",

            "title",
            "description",
            "video",
            "thumbnail",

            "plan",
            "duration",
            "amount",

            "start_date",
            "end_date",

            "status",

            "payment_method",
            "payment_id",
            "payment_status",
            "paid_at",

            "approved_by",
            "approved_at",
            "rejected_reason",

            "is_renewed",
            "renewal_date",
            "renewal_expiry",

            "views",
            "clicks",
            "ctr",
            "featured",

            "invoice_pdf",

            "audit_log",
        ]

        widgets = {
            "start_datetime": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),

            "end_datetime": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),

            "paid_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),

            "approved_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),

            "rejected_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter rejection reason...",
                }
            ),

            "audit_log": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                }
            ),

            "duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "views": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "clicks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "ctr": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "renewal_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "renewal_expiry": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "payment_method": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "payment_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "plan": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select status-select",
                }
            ),

            "seller": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "approved_by": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        rejected_reason = cleaned_data.get("rejected_reason")

        if status == "REJECTED" and not rejected_reason:
            self.add_error(
                "rejected_reason",
                "Rejection reason is required when status is REJECTED."
            )

        return cleaned_data
    












from django import forms
from django.contrib.auth.password_validation import validate_password


class SellerForgotPasswordForm(forms.Form):

    email = forms.EmailField(
        label="Registered Email",
        max_length=255,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your registered email",
                "autocomplete": "off",
                "autocapitalize": "none",
                "spellcheck": "false",
            }
        )
    )


class SellerResetPasswordForm(forms.Form):

    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter new password",
                "autocomplete": "new-password",
                "spellcheck": "false",
            }
        )
    )

    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm new password",
                "autocomplete": "new-password",
                "spellcheck": "false",
            }
        )
    )

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm:

            if password != confirm:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

            try:
                validate_password(password)

            except forms.ValidationError as error:
                raise forms.ValidationError(error.messages)

        return cleaned_data