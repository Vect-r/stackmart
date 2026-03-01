from django.contrib import admin
from .models import *

# Register your models here.
# admin.site.register(Message)
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('body','created_at','sender__username','is_read')
    ordering = ['-created_at']
        

admin.site.register(Conversation)

