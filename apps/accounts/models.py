from PIL.Image import Image
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager()

# Create your models here.

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)

    objects = UserManager()

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, related_name='profile', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="User/Profile_Picture", null=True, default="default.jpg")
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    favourite = models.ManyToManyField(Post, blank=True)
    is_celebrity = models.BooleanField(default=False)
    following_list = models.ManyToManyField(User, related_name='following_list', blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    def is_online(self):
        if self.last_login:
            return timezone.now() - self.last_login < timedelta(minutes=5)
        return False
    def __str__(self):
        return str(self.user.username)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and self.image.file and hasattr(self.image.file, 'temporary_file_path'):
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
