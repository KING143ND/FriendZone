from django.contrib import admin
from .models import *


admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Likes)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(Tag)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'likes', 'posted']
admin.site.register(Follow)
admin.site.register(Stream)
