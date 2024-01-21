from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.exceptions import ValidationError


class EditProfileForm(forms.ModelForm):
    image = forms.ImageField(required=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'First Name'}), required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Last Name'}), required=True)
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'input', 'placeholder': 'Bio', 'rows': 5}), required=False)
    url = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'URL'}), required=False)
    location = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Address'}), required=False)

    class Meta:
        model = Profile
        fields = ['image', 'first_name', 'last_name', 'bio', 'url', 'location']

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if url:
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'http://' + url
        return url

class UsernameValidator(RegexValidator):
    regex = r'^[\w.]+$'
    message = _('Username can only includes letters, numbers, underscores and full stops.')
    
class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        validators=[UsernameValidator()],
        max_length=50,
        help_text=_('Required. 150 characters or fewer. Letters, numbers, underscores, and dots only.'),
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'prompt srch_explore'})
    )
    fullname = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'prompt srch_explore'}), 
        max_length=70, 
        required=True
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email (Optional)', 'class': 'prompt srch_explore'}), 
        required=False
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'prompt srch_explore'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'prompt srch_explore'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'fullname', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserRegisterForm, self).__init__(*args, **kwargs)
            
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username == 'admin':
            raise ValidationError(_('This username is not accepted please choose another!'))
        return username.lower()
        
    def clean_fullname(self):
        fullname = self.cleaned_data.get('fullname')
        if not fullname:
            raise ValidationError(_('Full name is required.'))
        if ' ' not in fullname:
            raise ValidationError(_('Please enter both first name and last name with a space!'))
        return fullname.title()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        fullname = self.cleaned_data.get('fullname')
        first_name, last_name = fullname.split(' ', 1)
        user.first_name = first_name.title()
        user.last_name = last_name.title()
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'prompt srch_explore'}), max_length=40, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'prompt srch_explore'}), required=True)

    class Meta:
        model = User
        fields = ['username', 'password']

class NewCommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Write comment'}), required=True)
    
    class Meta:
        model = Comment
        fields = ("body",)
        

class NewPostform(forms.ModelForm):    
    picture = forms.ImageField(required=True)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=False)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Seperate with comma'}), required=False)

    class Meta:
        model = Post
        fields = ['picture', 'caption', 'tags']