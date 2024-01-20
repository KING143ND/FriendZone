from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse
import uuid
from .models import *
from django.db.models.signals import post_save, post_delete
from django.db.models import Max
from django.utils.text import slugify
from django.dispatch import receiver



class CustomUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        super().save(*args, **kwargs)
 
        
def generate_slug():
    return str(uuid.uuid1()) 
class Tag(models.Model):
    title = models.CharField(max_length=75, verbose_name='Tag', blank=True)
    slug = models.SlugField(null=False, unique=True, default=generate_slug)
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
    def get_absolute_url(self):
        return reverse('tags', args=[self.slug])
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


def user_directory_path(instance, filename):
    username = instance.user.username
    return f'user_{username}/{filename}'
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.ImageField(upload_to=user_directory_path, verbose_name="Picture")
    caption = models.CharField(max_length=10000, verbose_name="Caption", null=True, blank=True)
    posted = models.DateField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name="tags", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    likes_list = models.ManyToManyField(User, related_name='liked_by', blank=True)
    def get_absolute_url(self):
        return reverse("post-details", args=[str(self.id)])
    def __str__(self):
        return f'{self.user}-{self.id}'


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, _ = Profile.objects.get_or_create(user=instance)
        profile.first_name = instance.first_name
        profile.last_name = instance.last_name
        profile.save()


def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comment")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return str(f'{self.post}')
    def user_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        text_preview = comment.body[:90]
        sender = comment.user
        notify = Notification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_types=2)
        notify.save()
    def user_del_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.user
        notify = Notification.objects.filter(post=post, sender=sender, user=post.user, notification_types=2)
        notify.delete()
post_save.connect(Comment.user_comment_post, sender=Comment)
post_delete.connect(Comment.user_del_comment_post, sender=Comment)


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    reciepient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
    body = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def is_unread(self, user):
        return not self.is_read and self.reciepient == user
    def sender_message(from_user, to_user, body):
        sender_message = Message(
            user=from_user,
            sender = from_user,
            reciepient = to_user,
            body = body,
            is_read = True
            )
        sender_message.save()
        reciepient_message = Message(
            user=to_user,
            sender = from_user,
            reciepient = from_user,
            body = body,
            is_read = False
            )
        reciepient_message.save()
        return sender_message
    def get_message(user):
        users = []
        messages_data = Message.objects.filter(user=user).values('reciepient').annotate(last=Max('date')).order_by('-last')
        for message_data in messages_data:
            reciepient = User.objects.get(pk=message_data['reciepient'])
            unread_count = Message.objects.filter(user=user, reciepient=reciepient, is_read=False).count()
            users.append({
                'user': reciepient,
                'last': message_data['last'],
                'unread': unread_count
            })
        return users
    def __str__(self):
        return f'{self.user.username } - {self.pk}'
      
            
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
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_from_user" )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_to_user" )
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
    

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    bookmarked = models.BooleanField(default=False)
    def user_liked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        if sender != post.user:
            notify = Notification(post=post, sender=sender, user=post.user, notification_types=1)
            notify.save()
    def user_unliked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        notify = Notification.objects.filter(post=post, sender=sender, notification_types=1)
        notify.delete()
    def __str__(self):
            return str(self.post)


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    def user_follow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification(sender=sender, user=following, notification_types=3)
        notify.save()
    def user_unfollow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification.objects.filter(sender=sender, user=following, notification_types=3)
        notify.delete()
    def __str__(self):
        return str(self.follower)


class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()
    def add_post(sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.filter(following=user)
        streams = [Stream(post=post, user=follower.follower, date=post.posted, following=user) for follower in followers]
        Stream.objects.bulk_create(streams)
    def __str__(self):
        return str(self.user)
post_save.connect(Stream.add_post, sender=Post)
post_save.connect(Likes.user_liked_post, sender=Likes)
post_delete.connect(Likes.user_unliked_post, sender=Likes)
post_save.connect(Follow.user_follow, sender=Follow)
post_delete.connect(Follow.user_unfollow, sender=Follow)            