from datetime import datetime
from .models import SiteVisit


class TrackVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        # set visit start only once per session
        if 'visit_start' not in request.session:
            request.session['visit_start'] = datetime.now().isoformat()

        visit_start = request.session.get('visit_start')

        response = self.get_response(request)

        if visit_start:
            start_time = datetime.fromisoformat(visit_start)
            end_time = datetime.now()
            spent_time = end_time - start_time

            SiteVisit.objects.create(
                ip_address=ip,
                start_time=start_time,
                end_time=end_time,
                spent_time=spent_time
            )

            # reset for next request
            request.session['visit_start'] = datetime.now().isoformat()

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip





# home/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden

from .models import AdminProfilez, SellerProfile


class ShopKartURLSecurityMiddleware(MiddlewareMixin):
    """
    Central role-based access control for ShopKart.

    Admin: authenticated user + AdminProfilez
    Seller: authenticated user + SellerProfile
    Customer: authenticated user

    Keep object ownership checks in the individual views.
    """

    ADMIN_PATHS = (
        "/admin-dashboard/",
        "/low-stock/",
        "/admin-orders/",
        "/admin_unlock_seller/",
        "/xxxx/",
        "/category/",
        "/product/",
        "/saller_product_edit/",
        "/seller_profile/",
        "/sales-report/",
        "/visit_list",
        "/user-login-history/",
        "/customer-activity/",
        "/admin_contoll_seller_details/",
        "/sellers/",
        "/admin_seller_bank_list/",
        "/admin_seller_bank_edit/",
        "/admin_seller_bank_by_seller/",
        "/admin_line_sales/",
        "/order_status_chart/",
        "/top_selling_products/",
        "/admin_saller_tickat_dashboard/",
        "/admin_seller_tickets_details/",
        "/returns/",
        "/admin_advertisement_detail/",
        "/admin_advertisement_edit/",
        "/approve_advertisement/",
        "/approve_ad/",
        "/advertisement/reject/",
        "/advertisement_payment_details/",
        "/advertisement_sallerdetails/",
        "/advertisement_edit_form/",
        "/advertisement_plan_details/",
        "/expired-advertisements/",
        "/renewals/",
        "/renewal/edit/",
        "/check-renewal-status/",
    )

    SELLER_PATHS = (
        "/seller_dashboard/",
        "/bank-details/",
        "/bank-view/",
        "/saller_low_stock/",
        "/seller_neworders/",
        "/saller_product_list/",
        "/views.saller_product_add/",
        "/seller/product/",
        "/saller_customer_orders/",
        "/order/update/",
        "/saller_sales_report/",
        "/seller_order_status/",
        "/seller_top_selling_products/",
        "/seller_ticket_dashboard/",
        "/seller/create/",
        "/seller/returns/",
        "/unlock/",
        "/unlock/questions/",
        "/unlock/confirm/",
        "/advertisements/",
        "/advertisement/",
        "/seller/ad/",
        "/advertisement_payment/",
        "/advertisements/payment-success/",
        "/advertisements/status/",
    )

    CUSTOMER_PATHS = (
        "/carted",
        "/fav",
        "/favviewpage",
        "/remove_fav/",
        "/remove_cart/",
        "/addtocart",
        "/checkouts/",
        "/orderstatus/",
        "/order/",
        "/add-review/",
        "/invoice/",
        "/profile/",
        "/my-orders/",
        "/return/",
        "/my-returns/",
        "/return-detail/",
    )

    # Never put login, registration, OTP, or password-reset
    # routes in the protected path lists.
    PUBLIC_AUTH_PATHS = (
        "/login",
        "/register/",
        "/admin-login/",
        "/seller_login/",
        "/logout/",
        "/forgotpassword/",
        "/verify-otp/",
        "/resend-otp/",
        "/reset-password/",
        "/forgot-password/",
        "/seller/forgot-password/",
        "/seller/password-reset/",
        "/step1/",
        "/step2/",
        "/step3/",
        "/complete/",
        "/unlock/",
        "/unlock/questions/",
        "/unlock/confirm/",
    )

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path_info

        # Match path prefixes without matching unrelated paths.
        def matches(path, prefixes):
            for prefix in prefixes:
                base = prefix.rstrip("/")
                if path == base or path.startswith(base + "/"):
                    return True
            return False

        # Public login and registration routes must remain accessible.
        if matches(path, self.PUBLIC_AUTH_PATHS):
            return None

        is_admin = matches(path, self.ADMIN_PATHS)
        is_seller = matches(path, self.SELLER_PATHS)
        is_customer = matches(path, self.CUSTOMER_PATHS)

        # Unlisted pages remain public.
        if not (is_admin or is_seller or is_customer):
            return None

        # Require authentication.
        if not request.user.is_authenticated:
            if is_admin:
                login_url = "/admin-login/"
            elif is_seller:
                login_url = "/seller_login/"
            else:
                login_url = "/login"

            return redirect_to_login(
                request.get_full_path(),
                login_url=login_url,
            )

        # Admin role check.
        if is_admin:
            if not AdminProfilez.objects.filter(
                user_id=request.user.pk
            ).exists():
                return HttpResponseForbidden(
                    "403 Forbidden: Admin access required."
                )

        # Seller role check.
        if is_seller:
            if not SellerProfile.objects.filter(
                user_id=request.user.pk
            ).exists():
                return HttpResponseForbidden(
                    "403 Forbidden: Seller access required."
                )

        # Customer pages require login.
        # Order ownership must be checked by the view.
        return None













# home/middleware.py

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class ShopKartSecurityMiddleware:
    """
    ShopKart:
    1. Prevent browser/proxy caching of dynamic pages.
    2. Require login for selected protected URL prefixes.
    3. Redirect admin and seller areas to their respective login pages.

    Add this middleware AFTER Django AuthenticationMiddleware.
    """

    # Pages that require a logged-in customer or another authenticated user.
    AUTH_REQUIRED_PREFIXES = (
        "/checkouts",
        "/orderstatus",
        "/order/",
        "/add-review/",
        "/invoice/",
        "/profile/",
        "/my-orders",
        "/return/",
        "/my-returns",
        "/return-detail/",
        "/carted",
        "/fav",
        "/favviewpage",
        "/remove_cart/",
        "/remove_fav/",
        "/bank-details/",
        "/bank-view/",
    )

    # Admin pages. Keep admin-login and password-reset pages public.
    ADMIN_PREFIXES = (
        "/admin-dashboard/",
        "/low-stock/",
        "/admin-orders/",
        "/admin_unlock_seller/",
        "/category/",
        "/product/",
        "/seller_profile/",
        "/sales-report/",
        "/visit_list",
        "/user-login-history/",
        "/customer-activity/",
        "/admin_contoll_seller_details/",
        "/sellers/",
        "/admin_seller_bank_list/",
        "/admin_seller_bank_edit/",
        "/admin_seller_bank_by_seller/",
        "/admin_saller_tickat_dashboard/",
        "/admin_seller_tickets_details/",
        "/returns/",
        "/admin_advertisement_detail/",
        "/admin_advertisement_edit/",
        "/approve_advertisement/",
        "/approve_ad/",
        "/advertisement_payment_details/",
        "/advertisement_sallerdetails/",
        "/advertisement_plan_details/",
        "/expired-advertisements/",
        "/renewals/",
        "/renewal/edit/",
        "/admin_line_sales/",
        "/order_status_chart/",
        "/top_selling_products/",
    )

    # Seller-only area. These URLs must also be protected by seller-role
    # checks inside their views (see section 4).
    SELLER_PREFIXES = (
        "/seller_dashboard/",
        "/saller_product_list/",
        "/views.saller_product_add/",
        "/seller/product/",
        "/saller_customer_orders/",
        "/order/update/",
        "/saller_sales_report/",
        "/seller_order_status/",
        "/seller_top_selling_products/",
        "/seller_ticket_dashboard/",
        "/seller/create/",
        "/seller/returns/",
        "/saller_low_stock/",
        "/seller_neworders/",
        "/advertisements/",
        "/advertisement/",
        "/seller/ad/",
        "/advertisement_payment/",
        "/advertisements/payment-success/",
        "/advertisements/status/",
        "/advertisement_dashboard/",
        "/seller/forgot-password/",
        "/seller/password-reset/",
    )

    # Never force authentication on these login/recovery URLs.
    PUBLIC_AUTH_PREFIXES = (
        "/login",
        "/register/",
        "/admin-login/",
        "/seller_login/",
        "/forgotpassword/",
        "/verify-otp/",
        "/resend-otp/",
        "/reset-password/",
        "/forgot-password/",
        "/unlock/",
        "/unlock/questions/",
        "/unlock/confirm/",
        "/step1/",
        "/step2/",
        "/step3/",
        "/complete/",
        "/logout/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def starts_with_any(path, prefixes):
        return any(path.startswith(prefix) for prefix in prefixes)

    def __call__(self, request):
        path = request.path_info

        # Allow login, logout, registration and recovery pages through.
        is_public_auth = self.starts_with_any(
            path, self.PUBLIC_AUTH_PREFIXES
        )

        if not is_public_auth:
            # Admin area: redirect anonymous users to admin login.
            if self.starts_with_any(path, self.ADMIN_PREFIXES):
                if not request.user.is_authenticated:
                    return redirect(
                        reverse("admin_login") + "?next=" + path
                    )

            # Seller area: redirect anonymous users to seller login.
            elif self.starts_with_any(path, self.SELLER_PREFIXES):
                if not request.user.is_authenticated:
                    return redirect(
                        reverse("seller_login") + "?next=" + path
                    )

            # Other selected authenticated-user pages.
            elif self.starts_with_any(
                path, self.AUTH_REQUIRED_PREFIXES
            ):
                if not request.user.is_authenticated:
                    return redirect(
                        reverse("login") + "?next=" + path
                    )

        response = self.get_response(request)

        # Prevent browsers and intermediary caches from retaining
        # sensitive HTML pages, including login/logout-related pages.
        if response.get("Content-Type", "").startswith("text/html"):
            response["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0, private"
            )
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        return response


