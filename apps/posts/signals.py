from django.db.models.signals import post_save, post_delete
from .models import Comment


post_save.connect(Comment.user_comment_post, sender=Comment)
post_delete.connect(Comment.user_del_comment_post, sender=Comment)