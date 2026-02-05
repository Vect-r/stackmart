import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User

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
            