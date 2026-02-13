import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User, Blog, BlogImage

@receiver(pre_save, sender=User)
def delete_old_pancard(sender, instance, **kwargs):
    if not instance.pk:
        return  # new user, nothing to delete

    try:
        old_instance = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    old_file = old_instance.pancard
    new_file = instance.pancard

    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
            
@receiver(post_delete, sender=Blog)
def delete_blog_cover(sender, instance, **kwargs):
    if instance.cover_photo:
        instance.cover_photo.delete(save=False)

@receiver(post_delete, sender=BlogImage)
def delete_blog_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)