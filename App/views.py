from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login
from .models import Post, Follow, Stream, Profile, Comment, Message, Tag, Likes, Notification
from .forms import EditProfileForm, UserRegisterForm, UserLoginForm, NewPostform, NewCommentForm
from django.db.models import Q
from PIL import Image
from django.core.files import File
from io import BytesIO
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
import logging
from django.views.decorators.http import require_GET


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def UserProfile(request, username):
    Profile.objects.get_or_create(user=request.user)
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name
    posts = Post.objects.filter(user=user).order_by('-posted')
    notification = Notification.objects.filter(user=request.user).order_by('-date')
    notifications = notification[:5]
    total_unread=Message.objects.filter(user=request.user, is_read=False).count()
    saved = ''
    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        posts = profile.favourite.all()
        saved = 'true'
    posts_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    follower_uname=Follow.objects.filter(following=user).values_list('follower__username', flat=True)
    follower_verfied=Follow.objects.filter(following=user).values_list('follower__profile__is_celebrity', flat=True)
    follower_fname=Follow.objects.filter(following=user).values_list('follower__profile__first_name', flat=True)
    follower_lname=Follow.objects.filter(following=user).values_list('follower__profile__last_name', flat=True)
    follower_img=Follow.objects.filter(following=user).values_list('follower__profile__image', flat=True)
    following_verfied=Follow.objects.filter(follower=user).values_list('following__profile__is_celebrity', flat=True)
    following_uname=Follow.objects.filter(follower=user).values_list('following__username', flat=True)
    following_fname=Follow.objects.filter(follower=user).values_list('following__profile__first_name', flat=True)
    following_lname=Follow.objects.filter(follower=user).values_list('following__profile__last_name', flat=True)
    following_img=Follow.objects.filter(follower=user).values_list('following__profile__image', flat=True)
    follower_data = zip(follower_fname, follower_lname, follower_img, follower_uname, follower_verfied)
    following_data = zip(following_fname, following_lname, following_img, following_uname, following_verfied)
    following = list(following_data)
    follower = list(follower_data)
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
    context = {
        'posts': posts,
        'profile':profile,
        'posts_count':posts_count,
        'following_count':following_count,
        'followers_count':followers_count,
        'follower':follower,
        'following':following,
        'follow_status':follow_status,
        'notifications': notifications,
        'total_unread': total_unread,
        'saved': saved,
    }
    return render(request, 'profile.html', context)


def EditProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)
    total_unread=Message.objects.filter(user=request.user, is_read=False).count()
    notification = Notification.objects.filter(user=request.user).order_by('-date')
    notifications = notification[:5]
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile.image = form.cleaned_data.get('image')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.url = form.cleaned_data.get('url')
            profile.bio = form.cleaned_data.get('bio')
            profile.save()
            messages.success(request,f'{profile.first_name} {profile.last_name} your Profile has been Successfully Updated!')
            return redirect('profile', profile.user.username)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = EditProfileForm(instance=request.user.profile)
    context = {
        'form':form,
        'total_unread':total_unread,
        'notifications':notifications,
    }
    return render(request, 'editprofile.html', context)


def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)
    try:
        f, created = Follow.objects.get_or_create(follower=user, following=following)
        request.user.profile.following_list.add(following)
        if int(option) == 0:
            f.delete()
            request.user.profile.following_list.remove(following)
            Stream.objects.filter(following=following, user=request.user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:25]
            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=user, date=post.posted, following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profile', args=[username]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").lower()
        request.POST = request.POST.copy()
        request.POST['username'] = username
        form = UserRegisterForm(request.POST, request=request)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f'Hurray! Your account was created Welcome {new_user.first_name} {new_user.last_name}')
            new_user = authenticate(username=new_user.username, password=form.cleaned_data['password1'])
            login(request, new_user)
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = UserRegisterForm(request=request)
    return render(request, 'sign-up.html', {'form': form})

        
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Login successful! Welcome back {username}')
                return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = UserLoginForm()
    return render(request, 'sign-in.html', {'form': form})


@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=request.user)
    active_direct = None
    directs = None
    profile = get_object_or_404(Profile, user=user)
    notification = Notification.objects.filter(user=request.user).order_by('-date')
    notifications = notification[:5]
    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, reciepient=message['user'])
    total_unread=Message.objects.filter(user=request.user, is_read=False).count()
    context = {
        'directs':directs,
        'message_data': messages,
        'notifications': notifications,
        'active_direct': active_direct,
        'profile': profile,
        'total_unread': total_unread,
    }
    return render(request, 'direct.html', context)


@login_required
def Directs(request, username):
    user  = request.user
    messages = Message.get_message(user=user) 
    active_direct = username
    alldirect = Message.objects.filter(user=user, reciepient__username=username).order_by('-date')
    direct = Message.objects.filter(user=user, reciepient__username=username).order_by('-date')[:10]
    moredirect = Message.objects.filter(user=user, reciepient__username=username).order_by('-date')[10:]
    messages_to_update_ids = direct.values_list('id', flat=True)
    Message.objects.filter(id__in=messages_to_update_ids).update(is_read=True)
    for message in messages:
            if message['user'].username == username:
                message['unread'] = 0
    context = {
        'directs': direct,
        'alldirect': alldirect,
        'moredirect': moredirect,
        'message_data': messages,
        'active_direct': active_direct,
    }
    return render(request, 'inbox.html', context)


def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')
    if request.method == "POST":
        to_user = User.objects.get(username=to_user_username)
        Message.sender_message(from_user, to_user, body)
        return redirect(reverse('directs', args=[to_user_username]))
    return render(request, 'direct.html')


def UserSearch(request):
    query = request.GET.get('q')
    context = {}
    notification = Notification.objects.filter(user=request.user).order_by('-date')
    notifications = notification[:5]
    total_unread=Message.objects.filter(user=request.user, is_read=False).count()
    if query:
        users = User.objects.filter(
            Q(username__icontains=query)|
            Q(first_name__icontains=query)|
            Q(last_name__icontains=query)
            )
        following = Profile.objects.filter(user=request.user)
        uname = User.objects.filter(Q(username__icontains=query))
        paginator = Paginator(users, 8)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)
        if following == uname:
            follow_status = True
        else:
            follow_status = False
        context = {
            'users': users_paginator,
            'follow_status': follow_status,
            'following': following,
            'notifications': notifications,
            'total_unread': total_unread,
        }
    return render(request, 'search.html', context)


def NewConversation(request, username):
    from_user = request.user
    body = 'newmessagefromdjango'
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('search-users')
    if from_user != to_user:
        Message.sender_message(from_user, to_user, body)
        return redirect(reverse('directs', args=[to_user]))
    return render(request, 'direct.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def index(request):
    user = request.user
    all_users = User.objects.all().order_by('-last_login')
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
    notification = Notification.objects.filter(user=request.user).order_by('-date')
    notifications = notification[:5]
    total_unread=Message.objects.filter(user=request.user, is_read=False).count()
    profile = Profile.objects.all()
    follow=Follow.objects.filter(follower=user).values_list('following__username', flat=True)
    favourite_ids = Profile.objects.filter(user=user).values_list('favourite__id',flat=True)
    user_posts = Stream.objects.filter(user=user)
    liked_post_ids = user.liked_by.values_list('id', flat=True)
    user_posts = user_posts.exclude(post_id__in=liked_post_ids)
    post_items = Post.objects.filter(id__in=user_posts.values_list('post_id')).order_by('-posted')
    comments = Comment.objects.filter(post__in=post_items).all().order_by('-date')
    has_users = any(user.username != user.username and user.username not in follow for user in User.objects.all())
    context = {
        'post_items': post_items,
        'follow_status': follow_status,
        'follow': follow,
        'profile': profile,
        'favourite_ids': favourite_ids,
        'all_users': all_users,
        'comments': comments,
        'notifications': notifications,
        'total_unread': total_unread,
        'has_users': has_users,
    }
    return render(request, 'index.html', context)


@login_required
def NewPost(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    tags_obj = []
    if request.method == "POST":
        form = NewPostform(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tags')
            tag_list = list(tag_form.split(',')) if tag_form else []
            for tag in tag_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_obj.append(t)
            if hasattr(picture, 'temporary_file_path'):
                img = Image.open(picture.temporary_file_path())
            else:
                img = Image.open(BytesIO(picture.read()))
            if picture.size > 300 * 1024:
                new_size = (img.width // 2, img.height // 2)
                img = img.resize(new_size, Image.BICUBIC)
                img = img.convert('RGB')
                output_buffer = BytesIO()
                img.save(output_buffer, format='JPEG', quality=85)
                picture = File(output_buffer, name=picture.name)
            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user=user)
            p.tags.set(tags_obj)
            p.save()
            return redirect('profile', request.user.username)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = NewPostform()
    context = {
        'form': form
    }
    return redirect('', context)


@login_required
def PostDetail(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-date')
    notification = Notification.objects.filter(user=request.user).order_by('-date')
    notifications = notification[:5]
    total_unread=Message.objects.filter(user=request.user, is_read=False).count()
    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('post-details', args=[post.id]))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = NewCommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'notifications': notifications,
        'total_unread': total_unread
    }
    return render(request, 'postdetail.html', context)


def IndexComment(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-date')
    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return redirect('/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = NewCommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'index.html', context)


def add_comment(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    try:
        if request.method == "POST":
            form = NewCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.user = user
                comment.save()
                messages.success(request,f'{comment.user.profile.first_name} {comment.user.profile.last_name} Your Comment has been Successfully Posted!')
                return HttpResponseRedirect(reverse('post-details', args=[post.id]))
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except Exception as e:
        logging.exception("An error occurred: %s", str(e))
        return JsonResponse({'success': False, 'error': 'Internal Server Error'}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@require_GET
def get_comments(request, post_id):
    try:
        comments = Comment.objects.filter(post=post_id).values()
        comments_data = list(comments)
        for comment in comments_data:
            comment['date'] = comment['date'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return JsonResponse({'success': True, 'comments': comments_data})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})
    
    
@login_required
def Tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    total_unread=Message.objects.filter(user=request.user, is_read=False).count()
    notification = Notification.objects.filter(user=request.user).order_by('-date')
    notifications = notification[:5]
    posts = Post.objects.filter(tags=tag).order_by('-posted')
    context = {
        'posts': posts,
        'tag': tag,
        'total_unread': total_unread,
        'notifications': notifications
    }
    return render(request, 'tag.html', context)


@login_required
@csrf_exempt
def like(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    liker = user
    current_likes = post.likes
    liked = Likes.objects.filter(user=user, post=post).exists()
    print(liked)
    if not liked:
        Likes.objects.create(user=user, post=post)
        post.likes_list.add(liker)
        current_likes += 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        post.likes_list.remove(liker)
        current_likes -= 1
    post.likes = current_likes
    post.save()
    data = {
        'current_likes': current_likes,
        'liked': not liked
    }
    return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def favourite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    favourite = post
    profile = Profile.objects.get(user=user)
    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(favourite)
        is_favourite = False
    else:
        profile.favourite.add(favourite)
        is_favourite = True
    data = {
        'is_favourite': is_favourite,
    }
    return JsonResponse(data)


def ShowNotification(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')
    total_unread=Message.objects.filter(user=request.user, is_read=False).count()
    for notification in notifications:
        notification.is_seen = True
        notification.save()
    context = {
        'notifications': notifications,
        'total_unread': total_unread,
    }
    return render(request, 'notification.html', context)


def DeleteNotification(request, noti_id):
    user = request.user
    print(noti_id)
    Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect('show-notification')


def logout(request):
    auth.logout(request)
    return redirect("/")