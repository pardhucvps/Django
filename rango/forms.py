from django import forms
from rango.models import Page, Category, UserProfile
from django.contrib.auth.models import User


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                           help_text='Please enter Category')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name',)


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128,
                            help_text='Please enter Title of Page')
    url = forms.URLField(max_length=200, help_text='Enter Url of page')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0, required=False)


    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data

    class Meta:
        model = Page
        exclude = ('category',)


class UserForm(forms.ModelForm):
    username = forms.CharField(help_text = 'Please enter a username')
    email = forms.CharField(help_text = 'Please enter your email')
    password = forms.CharField(widget=forms.PasswordInput(),
                               help_text = 'please enter a valid password')

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(required=False)
    picture = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
