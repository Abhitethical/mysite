from atexit import register
from django.contrib import admin
from .models import *


"""
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'image', 'description')
admin.site.register(Catagory,CategoryAdmin)
"""
admin.site.register(CustomUser)
admin.site.register(CustomerRegistration)
admin.site.register(SellerLoginHistory)

admin.site.register(SellerPasswordResetToken)


admin.site.register(CouponUsage)
admin.site.register(Catagory)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Favourite)
admin.site.register(OrderPlacededx)
admin.site.register(Placedorderxx)
admin.site.register(PasswordResetOTPds)
admin.site.register(AdminProfilez)
admin.site.register(Orderz)


admin.site.register(UserProfile)

admin.site.register(UserActivity)

admin.site.register(CustomerLoginLogout)

admin.site.register(Sale)

admin.site.register(UserLoginHistory)





admin.site.register(SellerBankDetailxx)



admin.site.register(UserProfiles)


admin.site.register(Tickets)


admin.site.register(SellerPasswordResetOTP)

admin.site.register(SellerUnlockOTP)



admin.site.register(TicketReply)



admin.site.register(Review)

admin.site.register(ReturnRequested)

admin.site.register(RefundTransaction)

admin.site.register(Notification)


admin.site.register(Advertisementx)




admin.site.register(AdvertisementRenewalx)

admin.site.register(VisitorProfile)

admin.site.register(VisitorSession)
admin.site.register(PageVisit)
admin.site.register(VisitorEvent)

admin.site.register(LoginHistory)

admin.site.register(VisitorDevice)

admin.site.register(SecurityAuditLog)

admin.site.register(TrafficSource)




