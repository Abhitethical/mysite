from django.urls import path
from . import views

urlpatterns= [
   
    path('',views.home,name="home"),
    path("ad-view/<int:id>/",views.ad_view,name="ad_view"),

    path('carted',views.cart_paged,name="carted"),
    path('fav',views.fav_page,name="fav"),
    path('favviewpage',views.favviewpage,name="favviewpage"),
    path('remove_fav/<str:fid>',views.remove_fav,name="remove_fav"),
    path('remove_cart/<str:cid>',views.remove_cart,name="remove_cart"),
    path('collections/<str:name>',views.collectionsview,name="collections"),
    path('collections',views.collections,name="collections"),
    path('collections/<str:cname>/<str:pname>/',views.product_details,name="product_details"),
    path("ad-click/<int:id>/",views.ad_click,name="ad_click"),
    path('addtocart',views.add_to_cart,name="addtocart"),
    path('checkouts/', views.checkouts, name='checkoutview'),
    path('orderstatus/', views.orderstatus, name='orderstatus'), 
    path('order/<int:pk>/', views.order_detail, name='orderdetail'),  
    path('add-review/<int:order_id>/', views.add_review, name='add_review'),
    path('invoice/<int:order_id>/', views.invoice, name='invoice'),
    path('productsearch/', views.productsearch, name='productsearch'),
    path('profile/', views.profile, name='profile'),
    path('register/',views.register,name="register"),
    path('login',views.login_page,name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),


  

    















    #admindashboerd
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('low-stock/', views.low_stock_products, name='low_stock'),
    path('admin-orders/', views.admin_order_notifications, name='admin_orders'),

    path('admin_unlock_seller/', views.admin_unlock_seller, name='admin_unlock_seller'),


    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path("forgot-password/",views.admin_forgot_password,name="admin_forgot_password",),
    path( "reset-password/<int:profile_id>/",views.admin_forgot_password_reset,name="admin_forgot_password_reset",),



    path("category/", views.category_list, name="category_list"),
    path("category/add/", views.category_add, name="category_add"),
    path('category/edit/<int:id>/', views.category_edit, name='category_edit'),
    path('category/delete/<int:id>/', views.category_delete, name='category_delete'),
    path("product/", views.product_list, name="product_list"),
    path("product/add/", views.product_add, name="product_add"),
    path('saller_product_edit/edit/<int:id>/', views.product_edit, name='saller_product_edit'),
    path("product/delete/<int:id>/",views.admin_product_delete,name="admin_product_delete"),
    path('seller_profile/', views.seller_profile, name='seller_profile'),
    path("orders/", views.order_list, name="order_list"),
    path("orders/update/<int:id>/", views.update_order_status, name="update_order_status"),
    path("orders/customer/<int:user_id>/", views.customer_address, name="customer_address"),
    path("orders/product/<int:product_id>/", views.product_detailz, name="product_detailz"),
    path("my-orders/", views.customer_orders, name="customer_orders"),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('visit_list', views.visit_list, name='visit_list'),
    path('user-login-history/', views.user_login_history_view, name='user_login_history'),
    path('customer-activity/', views.customer_activity_view, name='customer_activity'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('user-login-history/', views.user_login_history_view, name='user_login_history'),
    path('admin_contoll_seller_details/', views.admin_contoll_seller_details, name='admin_contoll_seller_details'),
    path('seller/<int:id>/update_status/', views.admin_seller_update_status, name='admin_seller_update_status'),
    path('sellers/', views.admin_contoll_seller_details, name='admin_seller_list'),
    path('seller/<int:id>/', views.admin_seller_detail, name='admin_seller_detail'),
    path('admin_seller_bank_list/', views.admin_seller_bank_list, name='admin_seller_bank_list'),
    path( 'admin_seller_bank_edit/edit/<int:bank_id>/',views.admin_seller_bank_edit,name='admin_seller_bank_edit'),
    path('admin_seller_bank_by_seller/<int:seller_id>/banks/',views.admin_seller_bank_by_seller,name='admin_seller_bank_by_seller'),
    path('bank-details/', views.seller_bank_form, name='seller_bank_form'),  
    path('bank-view/', views.seller_bank_view, name='seller_bank_view'),  
    path('saller_low_stock/', views.saller_low_stock, name='saller_low_stock'),
    path('seller_neworders/', views.seller_neworders, name='seller_neworders'),

















    path('step1/', views.seller_register_step1, name='seller_register_step1'),
    path('step2/<int:seller_id>/', views.seller_register_step2, name='seller_register_step2'),
    path('step3/<int:seller_id>/', views.seller_register_step3, name='seller_register_step3'),
    path('complete/', views.registration_complete, name='registration_complete'),
    path('seller_login/', views.seller_login, name='seller_login'),
    path('logout/', views.seller_logout, name='seller_logout'),
    path("seller_dashboard/", views.seller_dashboard, name="seller_dashboard"),
    path('orders/', views.order_list, name='orderlist'),
    path('orders/<int:pk>/', views.customer_order_detail, name='customerorderdetail'),
    path('order_status_chart/', views.order_status_chart, name='order_status_chart'),
    path('top_selling_products/', views.top_selling_products, name='top_selling_products'),
    path('admin_line_sales/', views.admin_line_sales, name='admin_line_sales'),
    path("saller_product_list/", views.saller_product_list, name="saller_product_list"),
    path("views.saller_product_add/add/", views.saller_product_add, name="saller_product_add"),
    path('seller/product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('seller/product/delete/<int:pk>/', views.delete_product, name='delete_product'),   
    path("saller_customer_orders/", views.saller_customer_orders, name="saller_customer_orders"), 
    path("order/update/<int:order_id>/",views.seller_update_order_status,name="seller_update_order_status",),
    path('saller_sales_report/', views.saller_sales_report, name='saller_sales_report'),
    path('seller_order_status/', views.seller_order_status, name='seller_order_status'),
    path('seller_top_selling_products/',views.seller_top_selling_products,name='seller_top_selling_products'),
    path('seller_ticket_dashboard/', views.seller_ticket_dashboard, name='seller_ticket_dashboard'),
    path('seller/create/', views.create_ticket, name='create_ticket'),
    path("ticket/<int:ticket_id>/", views.ticket_detail,name="ticket_detail"),
    path('ticket-success/<str:ticket_number>/', views.ticket_success, name='ticket_success'),
    path('admin_saller_tickat_dashboard/', views.admin_saller_tickat_dashboard, name='admin_saller_tickat_dashboard'),
    path('ticket/<int:ticket_id>/update/', views.admin_update_ticket, name='admin_update_ticket'),

    path('search/', views.ticket_search, name='ticket_search'),
    path('ticket/<str:ticket_number>/', views.ticket_detailabcd, name='ticket_detailabcd'),
    path('ticket/<str:ticket_number>/cancel/', views.ticket_cancel, name='ticket_cancel'),
  
    path('admin_seller_tickets_details/<int:ticket_id>/details/',views.admin_seller_tickets_details,name='admin_seller_tickets_details'),


    path('unlock/', views.unlock_username, name='unlock_username'),
    path('unlock/questions/', views.seller_unlock_questions, name='seller_unlock_questions'),
    path('unlock/confirm/', views.seller_unlock_confirm, name='seller_unlock_confirm'),

    path("return/<int:order_id>/", views.create_return_request, name="return_request"),

    path('my-returns/',views.customer_return_list,name='customer_return_list'),
    path('return-detail/<int:pk>/',views.return_detail, name='return_detail'),

    path('seller/returns/',views.seller_return_list,name='seller_return_list'),

    path('seller/returns/<int:pk>/',views.seller_return_detail,name='seller_return_detail'),



    path('returns/', views.admin_return_list, name='admin_return_list'),

    path('returns/<int:id>/', views.admin_return_detail, name='admin_return_detail'),

    path('returns/<int:id>/edit/',views.admin_return_edit, name='admin_return_edit'),

    path('returns/<int:id>/delete/',views.admin_return_delete,name='admin_return_delete'),


    path("advertisements/",views.saller_advertisements,name="saller_advertisements"),
    path("advertisements/create/",views.create_advertisement,name="create_advertisement"),

    path("advertisement/<int:pk>/",views.advertisement_detail,name="advertisement_detail"),

    path("advertisement/<int:pk>/edit/",views.edit_advertisement,name="edit_advertisement"),

    path("advertisement/<int:pk>/delete/",views.delete_advertisement,name="delete_advertisement"),

    path("seller/ad/<int:id>/renew/",views.create_renewal,name="create_renewal"),

    path("advertisement/<int:id>/renew/",views.renew_advertisement,name="renew_advertisement"),

    path("advertisement/<int:id>/renewal-history/",views.renewal_history,name="renewal_history"),

    path("seller/ad/<int:id>/renewal-history/",views.renewal_detail,name="renewal_detail"),
    
    path("advertisement_payment/<int:id>/",views.advertisement_payment,name="advertisement_payment"),

    path("advertisements/payment-success/<int:id>/",views.payment_success,name="payment_success"),

    path("advertisements/status/<int:id>/",views.advertisement_status,name="advertisement_status"),
  
    path("advertisement_dashboard/",views.advertisement_dashboard,name="advertisement_dashboard"),

    path("admin_advertisement_detail/<int:id>/",views.admin_advertisement_detail,name="admin_advertisement_detail"),

    path("admin_advertisement_edit/<int:id>/edit/",views.admin_advertisement_edit,name="admin_advertisement_edit"),

    path("approve_advertisement/approve/<int:id>/",views.approve_advertisement,name="approve_advertisement"),

    path("approve_ad/approve/<int:id>/",views.approve_ad, name="approve_ad"),

    path("advertisement/reject/<int:id>/",views.reject_advertisement,name="reject_advertisement"),

    path("advertisement_payment_details/payment/<int:id>/",views.advertisement_payment_details,name="advertisement_payment_details"),

    path("advertisement_sallerdetails/details/<int:id>/",views.advertisement_sallerdetails,name="advertisement_sallerdetails",),

    path("advertisement_edit_form/<int:pk>/edit/",views.advertisement_edit_form,name="advertisement_edit_form",),

    path("advertisement_plan_details/details/<int:id>/",views.advertisement_plan_details,name="advertisement_plan_details",),

    path("expired-advertisements/",views.expired_advertisements,name="expired_advertisements"),

    path("renewals/",views.renewals,name="renewals"),


    path("renewal/edit/<int:id>/",views.admin_renewal_edit,name="admin_renewal_edit"),


    path("check-renewal-status/",views.check_renewal_status,name="check_renewal_status"),


    path("helpcenter",views.helpcenter,name="helpcenter"),

    path("contactus",views.contactus,name="contactus"),

    path("shipping",views.shipping,name="shipping"),

    path("returnpolicy",views.returnpolicy,name="returnpolicy"),

    path("privacypolicy",views.privacypolicy,name="privacypolicy"),

    path("termsconditions",views.termsconditions,name="termsconditions"),

    path("cookiepolicy",views.cookiepolicy,name="cookiepolicy"),


    path("seller/forgot-password/",views.seller_forgot_password,name="seller_forgot_password"),

    path("seller/password-reset/<str:token>/",views.seller_password_reset,name="seller_password_reset"),


]






























