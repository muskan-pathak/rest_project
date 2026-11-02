from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import ProjectAttachment
@receiver(post_delete, sender=ProjectAttachment)
def delete_attachment_file(sender, instance, **kwargs):
    if instance.file:
        file_storage = instance.file.storage
        file_name = instance.file.name
        transaction.on_commit(
            lambda: file_storage.delete(file_name)
        )