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

def bizz_profile_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"user_{instance.user.id}.{ext}"
    return os.path.join("bizz-profiles", filename)

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
    is_mail_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    def remove_profile_picture(self):
        if self.profile and self.profile.name != "defaults/user-avatar.svg":
            self.profile.delete(save=False)
        self.profile = "defaults/user-avatar.svg"
        self.save()

    def __str__(self):
        return f"{self.username} -> {self.id}"


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Approval System
    is_approved = models.BooleanField(default=False, help_text="Only admin approved services are visible to all.")
    
    # Optional: Track who suggested it (so you can notify them when approved)
    suggested_by = models.ForeignKey(
        'SellerProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='suggested_services'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SellerProfile(BaseClass):
    SELLER_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('business', 'Business'),
    )

    # Link to your existing User model (One Profile per User)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='seller_profile'
    )
    
    seller_type = models.CharField(
        max_length=20, 
        choices=SELLER_TYPE_CHOICES, 
        default='individual'
    )

    # Basic Info
    business_name = models.CharField(max_length=255, help_text="Brand name or Company name")
    profile_pic = models.ImageField(upload_to=bizz_profile_upload_path, blank=True, null=True, default="defaults/seller-avatar.svg")
    description = models.TextField(blank=True)
    
    # Address (Simple text for now, or you can make a separate Address model later)
    address = models.TextField()
    
    # Verification/Business Specifics
    is_verified = models.BooleanField(default=False)
    
    services = models.ManyToManyField(
        Service, 
        related_name='sellers',  # This key allows the reverse lookup!
        blank=True
    )

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"
    

    def remove_profile_picture(self):
        if self.profile_pic and self.profile_pic.name != "defaults/seller-avatar.svg":
            self.profile_pic.delete(save=False)
        self.profile_pic = "defaults/seller-avatar.svg"
        self.save()
    
    

class SocialLink(models.Model):
    PLATFORM_CHOICES = (
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('twitter', 'X (Twitter)'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('website', 'Personal Website'),
    )

    # Link to the Seller Profile
    seller = models.ForeignKey(
        SellerProfile, 
        on_delete=models.CASCADE, 
        related_name='social_links' # This allows access via seller.social_links.all()
    )
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField(help_text="Full URL (e.g., https://github.com/username)")
    
    # Optional: To control the order they appear on the profile
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f"{self.get_platform_display()} - {self.seller.business_name}"

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
    
class ConnectionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_connections')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_connections')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver') # Prevent duplicate requests

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"