from django.contrib import admin
from apps.users.models import User, UserVerification, Service, SocialLink, SellerProfile

class UserAdmin(admin.ModelAdmin):
    list_filter = ["is_active"]


admin.site.register(User, UserAdmin)

# Register your models here.
# admin.site.register(User)
admin.site.register(UserVerification)
admin.site.register(SocialLink)
admin.site.register(SellerProfile)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_approved', 'suggested_by', 'seller_count')
    list_filter = ('is_approved',)
    actions = ['approve_services']

    def approve_services(self, request, queryset):
        queryset.update(is_approved=True)
    
    # Custom column to see popularity in Admin panel
    def seller_count(self, obj):
        return obj.sellers.count()