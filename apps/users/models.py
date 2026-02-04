from django.db import models
from apps.master.models import BaseClass
import os
from django.utils import timezone

# Create your models here.

def pancard_upload_path(instance, filename):
    ext = filename.split('.')[-1]  
    filename = f"{instance.id}.{ext}"
    return os.path.join("users_pancards", filename)


class User(BaseClass):
    USER_TYPE_CHOICES = (
        ("buyer", "Buyer"),
        ("seller", "Seller"),
    )
    user_type = models.CharField(max_length=50, null=False, blank=False, choices=USER_TYPE_CHOICES)
    username = models.CharField(max_length=100,null=False,blank=False,unique=True)
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    mobile = models.CharField(max_length=100, null=False, blank=False, unique=True)
    pancard = models.FileField(upload_to=pancard_upload_path, null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    is_active = models.BooleanField(default=False)

class UserVerification(BaseClass):
    # VERIFICATION_CHOICE = (
    #     ('email', 'Mail Verification'),
    #     ('password', 'Password Reset Verification')
    # )
    VERIFICATION_CHOICE = (
        ('email', 'Mail Verification'),
        ('password', 'Password Reset Verification')
    )
    verification_type = models.CharField(max_length=50, choices=VERIFICATION_CHOICE)
    # Changed to CASCADE to keep database clean
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verifications")
    token = models.CharField(max_length=255, unique=True)
    isVerifiedByUser = models.BooleanField(default=False)
    expiryDateTime = models.DateTimeField()

    def __str__(self):
        return f"Type: {self.verification_type}, {self.user.username}"

    def is_expired(self):
        return timezone.now() > self.expiryDateTime