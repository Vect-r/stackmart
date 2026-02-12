from django.contrib import admin
from apps.users.models import *
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
    
@admin.register(ConnectionRequest)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('status', 'sender', 'receiver', 'created_at')
    list_filter = ('status',)
    actions = ['make_connections_accepted','make_connections_pending']

    def make_connections_accepted(self, request, queryset):
        queryset.update(status="accepted")

    def make_connections_pending(self,request,queryset):
        queryset.update(status="pending")

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)

admin.site.register(Blog)
# admin.site.register(BlogCategory)

admin.site.register(BlogImage)