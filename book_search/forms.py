from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from . import models


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ('text',)


class MakeTopForm(forms.ModelForm):
    class Meta:
        model = models.Top
        fields = ('name', 'top_type', 'books')


class AddBookIntoTop(forms.ModelForm):
    class Meta:
        model = models.BookInTop
        fields = ('name', 'author', 'description', 'image', 'place_in_top')


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-control', }))
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control', }))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', }))
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={'class': 'form-control', }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-control', }))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', }))


class ShareBookForm(forms.Form):
    email = forms.EmailField(label='Email', required=True)
    name = forms.CharField(max_length=230)
    message = forms.CharField(widget=forms.Textarea)


class VotingForm(forms.ModelForm):
    value = forms.ModelChoiceField(queryset=models.VoteStar.objects.all(), widget=forms.RadioSelect)

    class Meta:
        model = models.Vote
        fields = ('value',)


class ReadForm(forms.ModelForm):
    class Meta:
        model = models.Read
        fields = ('is_read',)


class AddBook(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ('name', 'author', 'description', 'image', 'genre_id')