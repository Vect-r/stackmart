from django.db import models
from apps.master.models import BaseClass
import os
from django.utils import timezone

# Create your models here.

def pancard_upload_path(instance, filename):
    ext = filename.split('.')[-1]  
    filename = f"{instance.id}.{ext}"
    return os.path.join("users_pancards", filename)

def profile_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"user_{instance.id}.{ext}"
    return os.path.join("user-profiles", filename)

class User(BaseClass):
    USER_TYPE_CHOICES = (
        ("buyer", "Buyer"),
        ("seller", "Seller"),
    )
    user_type = models.CharField(max_length=50, null=False, blank=False, choices=USER_TYPE_CHOICES)
    profile = models.ImageField(upload_to=profile_upload_path, default="defaults/user-avatar.svg")
    username = models.CharField(max_length=100,null=False,blank=False,unique=True)
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    mobile = models.CharField(max_length=100, null=False, blank=False, unique=True)
    pancard = models.FileField(upload_to=pancard_upload_path, null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    def remove_profile_picture(self):
        if self.profile and self.profile.name != "defaults/user-avatar.svg":
            self.profile.delete(save=False)
        self.profile = "defaults/user-avatar.svg"
        self.save()

class UserVerification(BaseClass):
    # VERIFICATION_CHOICE = (
    #     ('email', 'Mail Verification'),
    #     ('password', 'Password Reset Verification')
    # )
    VERIFICATION_CHOICE = (
        ('email', 'Mail Verification'),
        ('password', 'Password Reset Verification'),
    )
    verification_type = models.CharField(max_length=50, choices=VERIFICATION_CHOICE)
    # Changed to CASCADE to keep database clean
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verifications")
    isVerifiedByUser = models.BooleanField(default=False)
    expiryDateTime = models.DateTimeField()

    def __str__(self):
        return f"Type: {self.verification_type}, {self.user.username}"

    @property
    def isTimeExpired(self):
        return timezone.now() > self.expiryDateTime