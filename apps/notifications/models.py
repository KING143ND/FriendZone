from django.db import models
from apps.posts.models import Post
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Create your models here.
class Notification(models.Model):
    LIKE = 1
    COMMENT = 2
    FOLLOW = 3
    NOTIFICATION_TYPES = (
        (LIKE, 'Like'),
        (COMMENT, 'Comment'),
        (FOLLOW, 'Follow'),
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="notification_post", null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_from_user")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_to_user")
    notification_types = models.IntegerField(choices=NOTIFICATION_TYPES, null=True, blank=True)
    text_preview = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.notification_types == self.LIKE:
            self.text_preview = 'Like'
        elif self.notification_types == self.COMMENT:
            self.text_preview = 'Comment'
        elif self.notification_types == self.FOLLOW:
            self.text_preview = 'Follow'
        super(Notification, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)
