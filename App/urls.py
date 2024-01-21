from django.urls import path,include
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('<username>/', UserProfile, name='profile'),
    path('<username>/saved/', UserProfile, name='profilefavourite'),
    path('<username>/follow/<option>/', follow, name='follow'),
    path('accounts/edit/', EditProfile, name="editprofile"),
    path('users/sign-up/', register, name="sign-up"),
    path('users/sign-in/', user_login, name="sign-in"),
    path('users/sign-out/', logout, name='sign-out'),
    path('direct/inbox/', inbox, name="message"),
    path('direct/inbox/<username>/', Directs, name="directs"),
    path('message/send/', SendDirect, name="send-directs"),
    path('message/search/', UserSearch, name="search-users"),
    path('message/new/<username>/', NewConversation, name="conversation"),
    path('allnotifications', ShowNotification, name='show-notification'),
    path('notifications/delete/<int:noti_id>', DeleteNotification, name='delete-notification'),
    path('', index, name='index'),
    path('newpost', NewPost, name='newpost'),
    path('<uuid:post_id>', PostDetail, name='post-details'),
    path('<uuid:post_id>', IndexComment, name='index_comment'),
    path('tag/<slug:tag_slug>', Tags, name='tags'),
    path('like/<uuid:post_id>/', like, name='like'),
    path('favourite/<uuid:post_id>/', favourite, name='favourite'),
    path('add_comment/<uuid:post_id>/', add_comment, name='add_comment'),
    path('get_comments/<uuid:post_id>/', get_comments, name='get_comments'),
]
